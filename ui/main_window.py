import time
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QComboBox, QScrollArea, QFrame, QLineEdit, QTextEdit,
    QApplication, QSizePolicy, QPushButton,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QIcon

from .widgets import (
    Card, StatCard, ToggleSwitch, SectionLabel, HotkeyButton,
    AccentButton, DangerButton, NoScrollSpinBox,
)
from .overlay import CircleOverlay
from core.click_engine import ClickEngine
from core.hotkey_manager import HotkeyManager
from core.config_manager import ConfigManager


class MainWindow(QMainWindow):
    def __init__(self, config: ConfigManager):
        super().__init__()
        self._config = config
        self._engine = ClickEngine()
        self._hotkey_mgr = HotkeyManager()
        self._overlay = CircleOverlay()
        self._start_time = 0
        self._click_record_buttons = {}

        self._init_window()
        self._build_ui()
        self._load_config_to_ui()
        self._connect_signals()
        self._start_timers()
        self._apply_config()

        self._overlay.showFullScreen()
        self._hotkey_mgr.start_listening()

    def _init_window(self):
        self.setWindowTitle("自动连点器 Pro")
        self.setMinimumSize(420, 680)
        self.resize(440, 720)

        x = self._config.get("window_x")
        y = self._config.get("window_y")
        if x is not None and y is not None:
            self.move(x, y)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Header ---
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(48)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 0, 16, 0)

        title = QLabel("自动连点器 Pro")
        title.setObjectName("title")
        h_layout.addWidget(title)
        h_layout.addStretch()

        self._status_label = QLabel("空闲")
        self._status_label.setObjectName("status_stopped")
        h_layout.addWidget(self._status_label)

        main_layout.addWidget(header)

        # --- Scroll area ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_widget = QWidget()
        self._scroll_layout = QVBoxLayout(scroll_widget)
        self._scroll_layout.setContentsMargins(12, 12, 12, 12)
        self._scroll_layout.setSpacing(10)

        self._build_stats_row()
        self._build_click_settings()
        self._build_circle_settings()
        self._build_timer_settings()
        self._build_human_mode()
        self._build_hotkey_settings()
        self._build_profile_settings()
        self._build_log()

        self._scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

    def _build_stats_row(self):
        row = QHBoxLayout()
        row.setSpacing(8)

        self._clicks_stat = StatCard("点击数", "0")
        self._cps_stat = StatCard("CPS", "0.0")
        self._time_stat = StatCard("运行时间", "00:00")

        row.addWidget(self._clicks_stat)
        row.addWidget(self._cps_stat)
        row.addWidget(self._time_stat)
        self._scroll_layout.addLayout(row)

    def _build_click_settings(self):
        card = Card("点击设置")

        row = QHBoxLayout()
        row.addWidget(SectionLabel("模式"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["左键", "右键", "双击", "长按"])
        self._mode_combo.setCurrentIndex(0)
        row.addWidget(self._mode_combo, 1)
        card.add_layout(row)

        row2 = QHBoxLayout()
        row2.addWidget(SectionLabel("CPS"))
        self._cps_slider = QSlider(Qt.Horizontal)
        self._cps_slider.setRange(1, 100)
        self._cps_slider.setValue(10)
        row2.addWidget(self._cps_slider, 1)
        self._cps_value_label = QLabel("10")
        self._cps_value_label.setFixedWidth(30)
        self._cps_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row2.addWidget(self._cps_value_label)
        card.add_layout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(SectionLabel("间隔 (毫秒)"))
        self._interval_min = NoScrollSpinBox()
        self._interval_min.setRange(1, 5000)
        self._interval_min.setValue(80)
        self._interval_min.setPrefix("最小 ")
        row3.addWidget(self._interval_min)
        self._interval_max = NoScrollSpinBox()
        self._interval_max.setRange(1, 5000)
        self._interval_max.setValue(120)
        self._interval_max.setPrefix("最大 ")
        row3.addWidget(self._interval_max)
        card.add_layout(row3)

        row4 = QHBoxLayout()
        row4.addWidget(SectionLabel("按压时长 (毫秒)"))
        self._hold_spin = NoScrollSpinBox()
        self._hold_spin.setRange(10, 5000)
        self._hold_spin.setValue(50)
        row4.addWidget(self._hold_spin, 1)
        card.add_layout(row4)

        btn_row = QHBoxLayout()
        self._start_btn = AccentButton("开始 (F6)")
        self._start_btn.clicked.connect(self._on_start)
        btn_row.addWidget(self._start_btn)

        self._stop_btn = DangerButton("停止 (F8)")
        self._stop_btn.clicked.connect(self._on_stop)
        btn_row.addWidget(self._stop_btn)

        card.add_layout(btn_row)
        self._scroll_layout.addWidget(card)

    def _build_circle_settings(self):
        card = Card("点击范围")

        row = QHBoxLayout()
        row.addWidget(SectionLabel("半径"))
        self._radius_slider = QSlider(Qt.Horizontal)
        self._radius_slider.setRange(10, 500)
        self._radius_slider.setValue(50)
        row.addWidget(self._radius_slider, 1)
        self._radius_label = QLabel("50px")
        self._radius_label.setFixedWidth(50)
        self._radius_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(self._radius_label)
        card.add_layout(row)

        row2 = QHBoxLayout()
        row2.addWidget(SectionLabel("显示范围圈"))
        self._overlay_toggle = ToggleSwitch(checked=True)
        self._overlay_toggle.toggled.connect(self._on_overlay_toggle)
        row2.addWidget(self._overlay_toggle)
        row2.addStretch()

        row2.addWidget(SectionLabel("编辑位置"))
        self._edit_pos_toggle = ToggleSwitch(checked=False)
        self._edit_pos_toggle.toggled.connect(self._on_edit_pos_toggle)
        row2.addWidget(self._edit_pos_toggle)
        card.add_layout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(SectionLabel("坐标"))
        self._pos_x_spin = NoScrollSpinBox()
        self._pos_x_spin.setRange(0, 9999)
        self._pos_x_spin.setValue(960)
        self._pos_x_spin.setPrefix("X ")
        row3.addWidget(self._pos_x_spin)
        self._pos_y_spin = NoScrollSpinBox()
        self._pos_y_spin.setRange(0, 9999)
        self._pos_y_spin.setValue(540)
        self._pos_y_spin.setPrefix("Y ")
        row3.addWidget(self._pos_y_spin)
        card.add_layout(row3)

        self._scroll_layout.addWidget(card)

    def _build_timer_settings(self):
        card = Card("定时器")

        row = QHBoxLayout()
        row.addWidget(SectionLabel("模式"))
        self._timer_combo = QComboBox()
        self._timer_combo.addItems(["持续运行", "倒计时停止", "延迟启动"])
        self._timer_combo.currentIndexChanged.connect(self._on_timer_mode_changed)
        row.addWidget(self._timer_combo, 1)
        card.add_layout(row)

        # 提示标签（持续运行模式下显示）
        self._timer_hint = QLabel("手动停止前将一直运行，不会自动停止")
        self._timer_hint.setStyleSheet("color: #8b949e; font-size: 11px; background: transparent;")
        self._timer_hint.setWordWrap(True)
        card.add_widget(self._timer_hint)

        # 秒数输入（倒计时/延迟模式下显示）
        self._timer_row_widget = QWidget()
        self._timer_row_widget.setStyleSheet("background: transparent;")
        row2 = QHBoxLayout(self._timer_row_widget)
        row2.setContentsMargins(0, 0, 0, 0)
        row2.addWidget(SectionLabel("秒数"))
        self._timer_spin = NoScrollSpinBox()
        self._timer_spin.setRange(1, 86400)
        self._timer_spin.setValue(60)
        row2.addWidget(self._timer_spin, 1)
        card.add_widget(self._timer_row_widget)

        # 默认持续运行 → 隐藏秒数，显示提示
        self._on_timer_mode_changed(0)

        self._scroll_layout.addWidget(card)

    def _build_human_mode(self):
        card = Card("模拟人类行为")

        row = QHBoxLayout()
        row.addWidget(SectionLabel("启用"))
        self._human_toggle = ToggleSwitch(checked=False)
        self._human_toggle.toggled.connect(self._on_human_toggle)
        row.addWidget(self._human_toggle)
        row.addStretch()
        card.add_layout(row)

        row2 = QHBoxLayout()
        row2.addWidget(SectionLabel("强度"))
        self._human_slider = QSlider(Qt.Horizontal)
        self._human_slider.setRange(1, 100)
        self._human_slider.setValue(50)
        row2.addWidget(self._human_slider, 1)
        self._human_label = QLabel("50")
        self._human_label.setFixedWidth(30)
        self._human_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row2.addWidget(self._human_label)
        card.add_layout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(SectionLabel("抖动 (像素)"))
        self._jitter_spin = NoScrollSpinBox()
        self._jitter_spin.setRange(0, 50)
        self._jitter_spin.setValue(5)
        row3.addWidget(self._jitter_spin, 1)
        card.add_layout(row3)

        self._scroll_layout.addWidget(card)

    def _build_hotkey_settings(self):
        card = Card("快捷键")

        actions = [
            ("start_stop", "开始 / 暂停"),
            ("toggle_overlay", "显示 / 隐藏范围圈"),
            ("emergency_stop", "紧急停止"),
        ]

        for action, label_text in actions:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #c9d1d9;")
            row.addWidget(lbl, 1)

            key = self._config.get(f"hotkey_{action}", "")
            btn = HotkeyButton(action, key)
            btn.clicked.connect(lambda checked, a=action: self._on_record_hotkey(a))
            self._click_record_buttons[action] = btn
            row.addWidget(btn)
            card.add_layout(row)

        self._scroll_layout.addWidget(card)

    def _build_profile_settings(self):
        card = Card("配置方案")

        row = QHBoxLayout()
        self._profile_combo = QComboBox()
        self._profile_combo.setEditable(True)
        self._profile_combo.setInsertPolicy(QComboBox.NoInsert)
        self._refresh_profiles()
        row.addWidget(self._profile_combo, 1)

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._on_save_profile)
        row.addWidget(save_btn)

        load_btn = QPushButton("加载")
        load_btn.clicked.connect(self._on_load_profile)
        row.addWidget(load_btn)
        card.add_layout(row)

        self._scroll_layout.addWidget(card)

    def _build_log(self):
        card = Card("操作日志")
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setMaximumHeight(120)
        self._log_text.setPlaceholderText("日志将在此显示...")
        card.add_widget(self._log_text)
        self._scroll_layout.addWidget(card)

    def _connect_signals(self):
        self._engine.click_count_changed.connect(self._on_click_count)
        self._engine.status_changed.connect(self._on_status_changed)
        self._engine.log_message.connect(self._on_log)
        self._engine.elapsed_changed.connect(self._on_elapsed)

        self._hotkey_mgr.hotkey_triggered.connect(self._on_hotkey_action)

        self._cps_slider.valueChanged.connect(self._on_cps_changed)
        self._radius_slider.valueChanged.connect(self._on_radius_changed)
        self._human_slider.valueChanged.connect(self._on_human_intensity_changed)

        self._pos_x_spin.valueChanged.connect(self._on_pos_changed)
        self._pos_y_spin.valueChanged.connect(self._on_pos_changed)

        self._overlay.circle_changed.connect(self._on_overlay_circle_changed)

    def _start_timers(self):
        self._ui_timer = QTimer(self)
        self._ui_timer.timeout.connect(self._update_ui)
        self._ui_timer.start(100)

    def _load_config_to_ui(self):
        c = self._config
        self._cps_slider.setValue(c.get("cps", 10))
        self._interval_min.setValue(c.get("interval_min_ms", 80))
        self._interval_max.setValue(c.get("interval_max_ms", 120))
        self._hold_spin.setValue(c.get("hold_duration_ms", 50))

        mode_map = {"left": 0, "right": 1, "double": 2, "long": 3}
        self._mode_combo.setCurrentIndex(mode_map.get(c.get("click_mode", "left"), 0))

        self._radius_slider.setValue(c.get("circle_radius", 50))
        self._pos_x_spin.setValue(c.get("circle_x", 960))
        self._pos_y_spin.setValue(c.get("circle_y", 540))

        self._overlay_toggle.setChecked(c.get("overlay_visible", True))

        timer_map = {"continuous": 0, "countdown": 1, "delayed": 2}
        self._timer_combo.setCurrentIndex(timer_map.get(c.get("timer_mode", "continuous"), 0))
        self._timer_spin.setValue(c.get("countdown_seconds", 60))

        self._human_toggle.setChecked(c.get("human_mode", False))
        self._human_slider.setValue(c.get("human_intensity", 50))
        self._jitter_spin.setValue(c.get("position_jitter_px", 5))

        for action in ("start_stop", "toggle_overlay", "emergency_stop"):
            key = c.get(f"hotkey_{action}", "")
            if action in self._click_record_buttons:
                self._click_record_buttons[action].set_key_name(key)

    def _apply_config(self):
        mode_keys = ["left", "right", "double", "long"]
        mode = mode_keys[self._mode_combo.currentIndex()]

        self._engine.set_click_params(
            mode,
            self._interval_min.value(),
            self._interval_max.value(),
            self._hold_spin.value(),
        )

        timer_modes = ["continuous", "countdown", "delayed"]
        self._engine.set_timer(
            timer_modes[self._timer_combo.currentIndex()],
            self._timer_spin.value(),
            self._timer_spin.value() if self._timer_combo.currentIndex() == 2 else 0,
        )

        self._engine.set_circle(
            self._pos_x_spin.value(),
            self._pos_y_spin.value(),
            self._radius_slider.value(),
        )

        self._engine.set_human_mode(
            self._human_toggle.isChecked(),
            self._human_slider.value(),
            self._jitter_spin.value(),
            0.02,
            100,
            500,
        )

        self._overlay.set_circle(
            self._pos_x_spin.value(),
            self._pos_y_spin.value(),
            self._radius_slider.value(),
        )
        self._overlay.set_overlay_visible(self._overlay_toggle.isChecked())

        self._hotkey_mgr.clear_bindings()
        for action in ("start_stop", "toggle_overlay", "emergency_stop"):
            btn = self._click_record_buttons.get(action)
            if btn:
                key = btn.text()
                if key and key != "..." and key != "请按键...":
                    self._hotkey_mgr.set_binding(action, key)

    def _save_config(self):
        mode_keys = ["left", "right", "double", "long"]
        timer_modes = ["continuous", "countdown", "delayed"]

        self._config.update({
            "cps": self._cps_slider.value(),
            "interval_min_ms": self._interval_min.value(),
            "interval_max_ms": self._interval_max.value(),
            "hold_duration_ms": self._hold_spin.value(),
            "click_mode": mode_keys[self._mode_combo.currentIndex()],
            "circle_x": self._pos_x_spin.value(),
            "circle_y": self._pos_y_spin.value(),
            "circle_radius": self._radius_slider.value(),
            "overlay_visible": self._overlay_toggle.isChecked(),
            "timer_mode": timer_modes[self._timer_combo.currentIndex()],
            "countdown_seconds": self._timer_spin.value(),
            "human_mode": self._human_toggle.isChecked(),
            "human_intensity": self._human_slider.value(),
            "position_jitter_px": self._jitter_spin.value(),
            "window_x": self.x(),
            "window_y": self.y(),
        })
        for action in ("start_stop", "toggle_overlay", "emergency_stop"):
            btn = self._click_record_buttons.get(action)
            if btn:
                self._config.set(f"hotkey_{action}", btn.text())
        self._config.save()

    # --- Slots ---

    def _on_start(self):
        self._apply_config()
        self._engine.start()
        self._start_time = time.time()

    def _on_stop(self):
        self._engine.stop()
        self._start_time = 0

    def _on_cps_changed(self, value):
        self._cps_value_label.setText(str(value))
        if value > 0:
            interval = int(1000 / value)
            half = max(5, interval // 4)
            self._interval_min.setValue(max(1, interval - half))
            self._interval_max.setValue(interval + half)

    def _on_radius_changed(self, value):
        self._radius_label.setText(f"{value}px")
        self._overlay.set_circle(
            self._pos_x_spin.value(),
            self._pos_y_spin.value(),
            value,
        )
        self._engine.circle_radius = value

    def _on_pos_changed(self):
        x = self._pos_x_spin.value()
        y = self._pos_y_spin.value()
        r = self._radius_slider.value()
        self._overlay.set_circle(x, y, r)
        self._engine.set_circle(x, y, r)

    def _on_overlay_circle_changed(self, x, y, r):
        self._pos_x_spin.blockSignals(True)
        self._pos_y_spin.blockSignals(True)
        self._radius_slider.blockSignals(True)

        self._pos_x_spin.setValue(x)
        self._pos_y_spin.setValue(y)
        self._radius_slider.setValue(r)
        self._radius_label.setText(f"{r}px")

        self._engine.set_circle(x, y, r)

        self._pos_x_spin.blockSignals(False)
        self._pos_y_spin.blockSignals(False)
        self._radius_slider.blockSignals(False)

    def _on_overlay_toggle(self, checked):
        self._overlay.set_overlay_visible(checked)

    def _on_timer_mode_changed(self, index):
        """定时器模式切换：持续运行时隐藏秒数输入，显示提示"""
        is_continuous = (index == 0)
        self._timer_row_widget.setVisible(not is_continuous)
        self._timer_hint.setVisible(is_continuous)

    def _on_edit_pos_toggle(self, checked):
        self._overlay.enable_interaction(checked)

    def _on_human_toggle(self, checked):
        self._apply_config()

    def _on_human_intensity_changed(self, value):
        self._human_label.setText(str(value))

    def _on_record_hotkey(self, action):
        btn = self._click_record_buttons.get(action)
        if not btn:
            return
        for b in self._click_record_buttons.values():
            b.set_recording_state(False)
        btn.set_recording_state(True)
        self._hotkey_mgr.start_recording(action, self._on_hotkey_recorded)

    def _on_hotkey_recorded(self, action, key_name):
        btn = self._click_record_buttons.get(action)
        if btn:
            btn.set_key_name(key_name)
        self._apply_config()

    def _on_hotkey_action(self, action):
        if action == "start_stop":
            if self._engine.running and not self._engine.paused:
                self._engine.pause()
            else:
                self._apply_config()
                self._engine.start()
                if not self._start_time:
                    self._start_time = time.time()
        elif action == "toggle_overlay":
            v = not self._overlay_toggle.isChecked()
            self._overlay_toggle.setChecked(v)
            self._overlay.set_overlay_visible(v)
        elif action == "emergency_stop":
            self._engine.emergency_stop()
            self._start_time = 0

    def _on_click_count(self, count):
        self._clicks_stat.set_value(str(count))

    def _on_status_changed(self, status):
        if status == "running":
            self._status_label.setText("运行中")
            self._status_label.setObjectName("status_running")
            self._start_btn.setText("暂停 (F6)")
        elif status == "paused":
            self._status_label.setText("已暂停")
            self._status_label.setObjectName("status_stopped")
            self._start_btn.setText("继续 (F6)")
        elif status == "waiting":
            self._status_label.setText("等待中")
            self._status_label.setObjectName("status_stopped")
        else:
            self._status_label.setText("空闲")
            self._status_label.setObjectName("status_stopped")
            self._start_btn.setText("开始 (F6)")

        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)

    def _on_log(self, msg):
        ts = time.strftime("%H:%M:%S")
        self._log_text.append(f"[{ts}] {msg}")

    def _on_elapsed(self, seconds):
        if seconds < 0:
            self._time_stat.set_value(f"-{-seconds:.0f}秒")
        else:
            m, s = divmod(int(seconds), 60)
            self._time_stat.set_value(f"{m:02d}:{s:02d}")

    def _on_save_profile(self):
        name = self._profile_combo.currentText().strip()
        if not name:
            name = "default"
        self._save_config()
        self._config.save_profile(name)
        self._refresh_profiles()
        self._on_log(f"配置方案 '{name}' 已保存")

    def _on_load_profile(self):
        name = self._profile_combo.currentText().strip()
        if not name:
            return
        self._config.load_profile(name)
        self._load_config_to_ui()
        self._apply_config()
        self._on_log(f"配置方案 '{name}' 已加载")

    def _refresh_profiles(self):
        self._profile_combo.clear()
        profiles = self._config.list_profiles()
        self._profile_combo.addItems(profiles)
        last = self._config.get("last_profile", "default")
        idx = self._profile_combo.findText(last)
        if idx >= 0:
            self._profile_combo.setCurrentIndex(idx)

    def _update_ui(self):
        if self._engine.running:
            elapsed = self._engine.elapsed
            m, s = divmod(int(elapsed), 60)
            self._time_stat.set_value(f"{m:02d}:{s:02d}")

            count = self._engine.click_count
            if elapsed > 0:
                cps = count / elapsed
                self._cps_stat.set_value(f"{cps:.1f}")
            self._clicks_stat.set_value(str(count))

    def closeEvent(self, event):
        self._engine.stop()
        self._hotkey_mgr.stop_listening()
        self._overlay.close()
        self._save_config()
        super().closeEvent(event)
