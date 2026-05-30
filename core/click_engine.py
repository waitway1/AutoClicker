import ctypes
import ctypes.wintypes
import time
import threading
from PySide6.QtCore import QObject, Signal

from .click_simulator import ClickSimulator

# --- Windows SendInput constants ---
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000

user32 = ctypes.windll.user32


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.wintypes.LONG),
        ("dy", ctypes.wintypes.LONG),
        ("mouseData", ctypes.wintypes.DWORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _fields_ = [
        ("type", ctypes.wintypes.DWORD),
        ("_input", _INPUT),
    ]


def _send_click(x, y, button="left", double=False, hold_ms=50):
    """Move cursor to (x,y) and click using SendInput for minimal latency."""
    # Set cursor position
    ctypes.windll.user32.SetCursorPos(int(x), int(y))

    if button == "left":
        down_flag = MOUSEEVENTF_LEFTDOWN
        up_flag = MOUSEEVENTF_LEFTUP
    elif button == "right":
        down_flag = MOUSEEVENTF_RIGHTDOWN
        up_flag = MOUSEEVENTF_RIGHTUP
    else:
        down_flag = MOUSEEVENTF_MIDDLEDOWN
        up_flag = MOUSEEVENTF_MIDDLEUP

    def _press():
        extra = ctypes.c_ulong(0)
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp._input.mi = MOUSEINPUT(0, 0, 0, down_flag, 0, ctypes.pointer(extra))
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

    def _release():
        extra = ctypes.c_ulong(0)
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp._input.mi = MOUSEINPUT(0, 0, 0, up_flag, 0, ctypes.pointer(extra))
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

    _press()
    if hold_ms > 0:
        time.sleep(hold_ms / 1000.0)
    _release()

    if double:
        time.sleep(0.02)
        _press()
        if hold_ms > 0:
            time.sleep(hold_ms / 1000.0)
        _release()


class ClickEngine(QObject):
    click_count_changed = Signal(int)
    status_changed = Signal(str)
    log_message = Signal(str)
    elapsed_changed = Signal(float)

    def __init__(self):
        super().__init__()
        self._simulator = ClickSimulator()
        self._translator = lambda key, **kwargs: key.format(**kwargs)
        self._running = False
        self._paused = False
        self._thread = None
        self._click_count = 0
        self._start_time = 0

        # Click parameters
        self.interval_min_ms = 80
        self.interval_max_ms = 120
        self.click_mode = "left"
        self.hold_duration_ms = 50

        # Circle parameters
        self.circle_x = 960
        self.circle_y = 540
        self.circle_radius = 50

        # Timer
        self.timer_mode = "continuous"
        self.countdown_seconds = 60
        self.delay_start_seconds = 0

    @property
    def simulator(self):
        return self._simulator

    @property
    def running(self):
        return self._running

    @property
    def paused(self):
        return self._paused

    @property
    def click_count(self):
        return self._click_count

    @property
    def elapsed(self):
        if self._start_time and self._running:
            return time.time() - self._start_time
        return 0.0

    def set_translator(self, translator):
        self._translator = translator

    def _tr(self, key, **kwargs):
        return self._translator(key, **kwargs)

    def start(self):
        if self._running and not self._paused:
            return
        if self._paused:
            self._paused = False
            self.status_changed.emit("running")
            self.log_message.emit(self._tr("log.resumed"))
            return

        self._running = True
        self._paused = False
        self._click_count = 0
        self.click_count_changed.emit(0)
        self.status_changed.emit("running")

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        mode_names = {
            "left": self._tr("mode.left"),
            "right": self._tr("mode.right"),
            "double": self._tr("mode.double"),
            "long": self._tr("mode.long"),
        }
        self.log_message.emit(
            self._tr("log.started", mode=mode_names.get(self.click_mode, self.click_mode))
        )

    def pause(self):
        if self._running and not self._paused:
            self._paused = True
            self.status_changed.emit("paused")
            self.log_message.emit(self._tr("log.paused"))

    def stop(self):
        self._running = False
        self._paused = False
        self._start_time = 0
        self.status_changed.emit("stopped")
        self.log_message.emit(self._tr("log.stopped"))

    def toggle(self):
        if self._running and not self._paused:
            self.pause()
        elif self._paused:
            self.start()
        else:
            self.start()

    def emergency_stop(self):
        self.stop()
        self.log_message.emit(self._tr("log.emergency_stop"))

    def set_circle(self, x, y, radius):
        self.circle_x = x
        self.circle_y = y
        self.circle_radius = radius

    def set_click_params(self, mode, interval_min, interval_max, hold_ms):
        self.click_mode = mode
        self.interval_min_ms = interval_min
        self.interval_max_ms = interval_max
        self.hold_duration_ms = hold_ms

    def set_timer(self, mode, countdown_s, delay_s):
        self.timer_mode = mode
        self.countdown_seconds = countdown_s
        self.delay_start_seconds = delay_s

    def set_human_mode(self, enabled, intensity, jitter_px, pause_chance, pause_min, pause_max):
        self._simulator.configure(enabled, intensity, jitter_px, pause_chance, pause_min, pause_max)

    def _run_loop(self):
        # Delay start
        if self.delay_start_seconds > 0:
            self.log_message.emit(
                self._tr("log.delay_start", seconds=self.delay_start_seconds)
            )
            self.status_changed.emit("waiting")
            deadline = time.time() + self.delay_start_seconds
            while time.time() < deadline and self._running:
                remaining = deadline - time.time()
                self.elapsed_changed.emit(-remaining)
                time.sleep(0.05)
            if not self._running:
                return

        self._start_time = time.time()
        self.status_changed.emit("running")

        while self._running:
            if self._paused:
                time.sleep(0.05)
                continue

            # Check countdown
            if self.timer_mode == "countdown":
                elapsed = time.time() - self._start_time
                if elapsed >= self.countdown_seconds:
                    self.log_message.emit(self._tr("log.countdown_finished"))
                    self._running = False
                    self.status_changed.emit("stopped")
                    break
                self.elapsed_changed.emit(elapsed)

            # Pick random point in circle
            px, py = self._simulator.jitter_point(
                self.circle_x, self.circle_y, self.circle_radius
            )

            # Perform click
            try:
                _send_click(
                    px, py,
                    button=self.click_mode if self.click_mode in ("left", "right") else "left",
                    double=(self.click_mode == "double"),
                    hold_ms=self.hold_duration_ms if self.click_mode == "long" else 10,
                )
            except Exception as e:
                self.log_message.emit(self._tr("log.click_error", error=e))

            self._click_count += 1
            self.click_count_changed.emit(self._click_count)

            # Human micro-pause
            should_pause, pause_ms = self._simulator.should_micro_pause()
            if should_pause:
                time.sleep(pause_ms / 1000.0)

            # Random interval
            interval_ms = self._simulator.jitter_interval(
                self.interval_min_ms, self.interval_max_ms
            )
            time.sleep(interval_ms / 1000.0)

        self._start_time = 0
