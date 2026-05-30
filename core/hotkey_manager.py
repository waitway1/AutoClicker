from PySide6.QtCore import QObject, Signal

from pynput import keyboard


def _normalize_key_name(key):
    """Convert a pynput key to a display string."""
    if isinstance(key, keyboard.Key):
        name = key.name
        replacements = {
            "f1": "F1", "f2": "F2", "f3": "F3", "f4": "F4",
            "f5": "F5", "f6": "F6", "f7": "F7", "f8": "F8",
            "f9": "F9", "f10": "F10", "f11": "F11", "f12": "F12",
            "space": "Space", "enter": "Enter", "tab": "Tab",
            "esc": "Escape", "escape": "Escape",
            "shift": "Shift", "shift_r": "Shift",
            "ctrl_l": "Ctrl", "ctrl_r": "Ctrl",
            "alt_l": "Alt", "alt_r": "Alt",
            "caps_lock": "CapsLock",
            "insert": "Insert", "delete": "Delete",
            "home": "Home", "end": "End",
            "page_up": "PageUp", "page_down": "PageDown",
            "up": "Up", "down": "Down", "left": "Left", "right": "Right",
            "backspace": "Backspace",
        }
        return replacements.get(name, name.upper() if len(name) <= 2 else name.capitalize())
    elif isinstance(key, keyboard.KeyCode):
        if key.char:
            return key.char.upper()
        if key.vk:
            return f"VK_{key.vk}"
    return str(key)


class HotkeyManager(QObject):
    hotkey_triggered = Signal(str)

    def __init__(self):
        super().__init__()
        self._bindings = {}
        self._listener = None
        self._recording_target = None
        self._record_callback = None

    def set_binding(self, action_name, key_name):
        self._bindings[key_name] = action_name

    def get_bindings(self):
        return dict(self._bindings)

    def clear_bindings(self):
        self._bindings.clear()

    def start_listening(self):
        if self._listener and self._listener.running:
            return
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()

    def stop_listening(self):
        if self._listener:
            self._listener.stop()
            self._listener = None

    def start_recording(self, action_name, callback):
        self._recording_target = action_name
        self._record_callback = callback

    def stop_recording(self):
        self._recording_target = None
        self._record_callback = None

    @property
    def is_recording(self):
        return self._recording_target is not None

    def _on_press(self, key):
        key_name = _normalize_key_name(key)

        if self._recording_target:
            old_key = None
            for k, v in self._bindings.items():
                if v == self._recording_target:
                    old_key = k
                    break
            if old_key:
                del self._bindings[old_key]
            self._bindings[key_name] = self._recording_target
            if self._record_callback:
                self._record_callback(self._recording_target, key_name)
            self._recording_target = None
            self._record_callback = None
            return

        if key_name in self._bindings:
            self.hotkey_triggered.emit(self._bindings[key_name])

    def _on_release(self, key):
        pass
