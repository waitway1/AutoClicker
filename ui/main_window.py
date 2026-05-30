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
from .styles import get_theme_stylesheet
from .i18n import translate
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
        self._theme_combo = None
        self._language_combo = None
        self._text_labels = {}
        self._cards = {}
        self._hotkey_labels = {}
        self._current_status = "stopped"
        self._language_apply_mode = None

        self._init_window()
        self._build_ui()
        self._load_config_to_ui()
        self._engine.set_translator(self._tr)
        self._connect_signals()
        self._start_timers()
        self._apply_config()

        self._overlay.showFullScreen()
        self._hotkey_mgr.start_listening()

    def _init_window(self):
        self.setWindowTitle(self._tr("app.title"))
        self.setMinimumSize(560, 720)
        self.resize(620, 780)

        x = self._config.get("window_x")
        y = self._config.get("window_y")
        if x is not None and y is not None:
            self.move(x, y)

    def _tr(self, key, **kwargs):
        mode = self._language_apply_mode or self._current_language_mode()
        return translate(mode, key, **kwargs)

    def _section(self, key):
        label = SectionLabel("")
        self._text_labels.setdefault(key, []).append(label)
        return label

    def _label(self, key):
        label = QLabel("")
        self._text_labels.setdefault(key, []).append(label)
        return label

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Header ---
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(70)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(18, 0, 18, 0)
        h_layout.setSpacing(12)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        self._title_label = QLabel("")
        self._title_label.setObjectName("title")
        self._subtitle_label = QLabel("")
        self._subtitle_label.setObjectName("subtitle")
        title_box.addWidget(self._title_label)
        title_box.addWidget(self._subtitle_label)
        h_layout.addLayout(title_box)
        h_layout.addStretch()

        self._appearance_label = self._section("appearance")
        h_layout.addWidget(self._appearance_label)
        self._theme_combo = QComboBox()
        self._theme_combo.setFixedWidth(96)
        self._theme_combo.addItem("跟随系统", "system")
        self._theme_combo.addItem("白天", "light")
        self._theme_combo.addItem("黑夜", "dark")
        h_layout.addWidget(self._theme_combo)

        self._language_label = self._section("language")
        h_layout.addWidget(self._language_label)
        self._language_combo = QComboBox()
        self._language_combo.setFixedWidth(96)
        self._language_combo.addItem("默认", "system")
        self._language_combo.addItem("中文", "zh")
        self._language_combo.addItem("English", "en")
        h_layout.addWidget(self._language_combo)

        self._status_label = QLabel("")
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
        self._scroll_layout.setContentsMargins(14, 14, 14, 14)
        self._scroll_layout.setSpacing(12)

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

        self._clicks_stat = StatCard("", "0")
        self._cps_stat = StatCard("CPS", "0.0")
        self._time_stat = StatCard("", "00:00")

        row.addWidget(self._clicks_stat)
        row.addWidget(self._cps_stat)
        row.addWidget(self._time_stat)
        self._scroll_layout.addLayout(row)

    def _build_click_settings(self):
        card = Card("")
        self._cards["click"] = card

        row = QHBoxLayout()
        row.addWidget(self._section("mode"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItem("左键", "left")
        self._mode_combo.addItem("右键", "right")
        self._mode_combo.addItem("双击", "double")
        self._mode_combo.addItem("长按", "long")
        self._mode_combo.setCurrentIndex(0)
        row.addWidget(self._mode_combo, 1)
        card.add_layout(row)

        row2 = QHBoxLayout()
        row2.addWidget(self._section("cps"))
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
        row3.addWidget(self._section("interval_ms"))
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
        row4.addWidget(self._section("hold_ms"))
        self._hold_spin = NoScrollSpinBox()
        self._hold_spin.setRange(10, 5000)
        self._hold_spin.setValue(50)
        row4.addWidget(self._hold_spin, 1)
        card.add_layout(row4)

        btn_row = QHBoxLayout()
        self._start_btn = AccentButton("")
        self._start_btn.clicked.connect(self._on_start)
        btn_row.addWidget(self._start_btn)

        self._stop_btn = DangerButton("")
        self._stop_btn.clicked.connect(self._on_stop)
        btn_row.addWidget(self._stop_btn)

        card.add_layout(btn_row)
        self._scroll_layout.addWidget(card)

    def _build_circle_settings(self):
        card = Card("")
        self._cards["circle"] = card

        row = QHBoxLayout()
        row.addWidget(self._section("radius"))
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
        row2.addWidget(self._section("show_circle"))
        self._overlay_toggle = ToggleSwitch(checked=True)
        self._overlay_toggle.toggled.connect(self._on_overlay_toggle)
        row2.addWidget(self._overlay_toggle)
        row2.addStretch()

        row2.addWidget(self._section("edit_position"))
        self._edit_pos_toggle = ToggleSwitch(checked=False)
        self._edit_pos_toggle.toggled.connect(self._on_edit_pos_toggle)
        row2.addWidget(self._edit_pos_toggle)
        card.add_layout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(self._section("coordinates"))
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
        card = Card("")
        self._cards["timer"] = card

        row = QHBoxLayout()
        row.addWidget(self._section("mode"))
        self._timer_combo = QComboBox()
        self._timer_combo.addItem("持续运行", "continuous")
        self._timer_combo.addItem("倒计时停止", "countdown")
        self._timer_combo.addItem("延迟启动", "delayed")
        self._timer_combo.currentIndexChanged.connect(self._on_timer_mode_changed)
        row.addWidget(self._timer_combo, 1)
        card.add_layout(row)

        # 提示标签（持续运行模式下显示）
        self._timer_hint = QLabel("")
        self._timer_hint.setObjectName("subtitle")
        self._timer_hint.setWordWrap(True)
        card.add_widget(self._timer_hint)

        # 秒数输入（倒计时/延迟模式下显示）
        self._timer_row_widget = QWidget()
        self._timer_row_widget.setStyleSheet("background: transparent;")
        row2 = QHBoxLayout(self._timer_row_widget)
        row2.setContentsMargins(0, 0, 0, 0)
        row2.addWidget(self._section("seconds"))
        self._timer_spin = NoScrollSpinBox()
        self._timer_spin.setRange(1, 86400)
        self._timer_spin.setValue(60)
        row2.addWidget(self._timer_spin, 1)
        card.add_widget(self._timer_row_widget)

        # 默认持续运行 → 隐藏秒数，显示提示
        self._on_timer_mode_changed(0)

        self._scroll_layout.addWidget(card)

    def _build_human_mode(self):
        card = Card("")
        self._cards["human"] = card

        row = QHBoxLayout()
        row.addWidget(self._section("enable"))
        self._human_toggle = ToggleSwitch(checked=False)
        self._human_toggle.toggled.connect(self._on_human_toggle)
        row.addWidget(self._human_toggle)
        row.addStretch()
        card.add_layout(row)

        row2 = QHBoxLayout()
        row2.addWidget(self._section("intensity"))
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
        row3.addWidget(self._section("jitter_px"))
        self._jitter_spin = NoScrollSpinBox()
        self._jitter_spin.setRange(0, 50)
        self._jitter_spin.setValue(5)
        row3.addWidget(self._jitter_spin, 1)
        card.add_layout(row3)

        self._scroll_layout.addWidget(card)

    def _build_hotkey_settings(self):
        card = Card("")
        self._cards["hotkeys"] = card

        actions = [
            ("start_stop", "hotkey.start_pause"),
            ("toggle_overlay", "hotkey.toggle_overlay"),
            ("emergency_stop", "hotkey.emergency_stop"),
        ]

        for action, label_key in actions:
            row = QHBoxLayout()
            lbl = QLabel("")
            self._hotkey_labels[action] = (lbl, label_key)
            row.addWidget(lbl, 1)

            key = self._config.get(f"hotkey_{action}", "")
            btn = HotkeyButton(action, key)
            btn.clicked.connect(lambda checked, a=action: self._on_record_hotkey(a))
            self._click_record_buttons[action] = btn
            row.addWidget(btn)
            card.add_layout(row)

        self._scroll_layout.addWidget(card)

    def _build_profile_settings(self):
        card = Card("")
        self._cards["profiles"] = card

        row = QHBoxLayout()
        self._profile_combo = QComboBox()
        self._profile_combo.setEditable(True)
        self._profile_combo.setInsertPolicy(QComboBox.NoInsert)
        self._refresh_profiles()
        row.addWidget(self._profile_combo, 1)

        self._save_profile_btn = QPushButton("")
        self._save_profile_btn.clicked.connect(self._on_save_profile)
        row.addWidget(self._save_profile_btn)

        self._load_profile_btn = QPushButton("")
        self._load_profile_btn.clicked.connect(self._on_load_profile)
        row.addWidget(self._load_profile_btn)
        card.add_layout(row)

        self._scroll_layout.addWidget(card)

    def _build_log(self):
        card = Card("")
        self._cards["log"] = card
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setMaximumHeight(120)
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
        self._theme_combo.currentIndexChanged.connect(self._on_theme_mode_changed)
        self._language_combo.currentIndexChanged.connect(self._on_language_mode_changed)
        self._connect_system_theme_listener()

    def _start_timers(self):
        self._ui_timer = QTimer(self)
        self._ui_timer.timeout.connect(self._update_ui)
        self._ui_timer.start(100)

    def _load_config_to_ui(self):
        c = self._config
        language_mode = c.get("language_mode", "system")
        idx = self._language_combo.findData(language_mode)
        self._language_combo.setCurrentIndex(idx if idx >= 0 else 0)

        theme_mode = c.get("theme_mode", "system")
        idx = self._theme_combo.findData(theme_mode)
        self._theme_combo.setCurrentIndex(idx if idx >= 0 else 0)

        self._cps_slider.setValue(c.get("cps", 10))
        self._interval_min.setValue(c.get("interval_min_ms", 80))
        self._interval_max.setValue(c.get("interval_max_ms", 120))
        self._hold_spin.setValue(c.get("hold_duration_ms", 50))

        idx = self._mode_combo.findData(c.get("click_mode", "left"))
        self._mode_combo.setCurrentIndex(idx if idx >= 0 else 0)

        self._radius_slider.setValue(c.get("circle_radius", 50))
        self._pos_x_spin.setValue(c.get("circle_x", 960))
        self._pos_y_spin.setValue(c.get("circle_y", 540))

        self._overlay_toggle.setChecked(c.get("overlay_visible", True))

        idx = self._timer_combo.findData(c.get("timer_mode", "continuous"))
        self._timer_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self._timer_spin.setValue(c.get("countdown_seconds", 60))

        self._human_toggle.setChecked(c.get("human_mode", False))
        self._human_slider.setValue(c.get("human_intensity", 50))
        self._jitter_spin.setValue(c.get("position_jitter_px", 5))

        for action in ("start_stop", "toggle_overlay", "emergency_stop"):
            key = c.get(f"hotkey_{action}", "")
            if action in self._click_record_buttons:
                self._click_record_buttons[action].set_key_name(key)

        self._apply_theme_mode()
        self._apply_language()

    def _apply_config(self):
        mode = self._mode_combo.currentData() or "left"

        self._engine.set_click_params(
            mode,
            self._interval_min.value(),
            self._interval_max.value(),
            self._hold_spin.value(),
        )

        self._engine.set_timer(
            self._timer_combo.currentData() or "continuous",
            self._timer_spin.value(),
            self._timer_spin.value() if self._timer_combo.currentData() == "delayed" else 0,
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
                key = btn.key_name()
                if key and key != "...":
                    self._hotkey_mgr.set_binding(action, key)

    def _save_config(self):
        self._config.update({
            "cps": self._cps_slider.value(),
            "interval_min_ms": self._interval_min.value(),
            "interval_max_ms": self._interval_max.value(),
            "hold_duration_ms": self._hold_spin.value(),
            "click_mode": self._mode_combo.currentData() or "left",
            "circle_x": self._pos_x_spin.value(),
            "circle_y": self._pos_y_spin.value(),
            "circle_radius": self._radius_slider.value(),
            "overlay_visible": self._overlay_toggle.isChecked(),
            "timer_mode": self._timer_combo.currentData() or "continuous",
            "countdown_seconds": self._timer_spin.value(),
            "human_mode": self._human_toggle.isChecked(),
            "human_intensity": self._human_slider.value(),
            "position_jitter_px": self._jitter_spin.value(),
            "window_x": self.x(),
            "window_y": self.y(),
            "theme_mode": self._current_theme_mode(),
            "language_mode": self._current_language_mode(),
        })
        for action in ("start_stop", "toggle_overlay", "emergency_stop"):
            btn = self._click_record_buttons.get(action)
            if btn:
                key = btn.key_name()
                if key:
                    self._config.set(f"hotkey_{action}", key)
        self._config.save()

    def _current_theme_mode(self):
        if self._theme_combo is None:
            return self._config.get("theme_mode", "system")
        return self._theme_combo.currentData() or "system"

    def _current_language_mode(self):
        if self._language_combo is None:
            return self._config.get("language_mode", "system")
        return self._language_combo.currentData() or "system"

    def _apply_theme_mode(self):
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_theme_stylesheet(self._current_theme_mode()))
        for switch in self.findChildren(ToggleSwitch):
            switch.update()

    def _set_combo_options(self, combo, options):
        current = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        for key, data in options:
            combo.addItem(self._tr(key), data)
        idx = combo.findData(current)
        combo.setCurrentIndex(idx if idx >= 0 else 0)
        combo.blockSignals(False)

    def _apply_language(self):
        self._language_apply_mode = self._current_language_mode()
        self.setWindowTitle(self._tr("app.title"))
        self._title_label.setText(self._tr("app.title"))
        self._subtitle_label.setText(self._tr("app.subtitle"))

        for key, labels in self._text_labels.items():
            for label in labels:
                label.setText(self._tr(key))

        card_titles = {
            "click": "click.title",
            "circle": "circle.title",
            "timer": "timer.title",
            "human": "human.title",
            "hotkeys": "hotkeys.title",
            "profiles": "profiles.title",
            "log": "log.title",
        }
        for card_key, text_key in card_titles.items():
            self._cards[card_key].set_title(self._tr(text_key))

        self._clicks_stat.set_label(self._tr("stat.clicks"))
        self._time_stat.set_label(self._tr("stat.runtime"))
        self._interval_min.setPrefix(self._tr("prefix.min"))
        self._interval_max.setPrefix(self._tr("prefix.max"))

        self._set_combo_options(self._theme_combo, [
            ("theme.system", "system"),
            ("theme.light", "light"),
            ("theme.dark", "dark"),
        ])
        self._set_combo_options(self._language_combo, [
            ("language.system", "system"),
            ("language.zh", "zh"),
            ("language.en", "en"),
        ])
        self._set_combo_options(self._mode_combo, [
            ("mode.left", "left"),
            ("mode.right", "right"),
            ("mode.double", "double"),
            ("mode.long", "long"),
        ])
        self._set_combo_options(self._timer_combo, [
            ("timer.continuous", "continuous"),
            ("timer.countdown", "countdown"),
            ("timer.delayed", "delayed"),
        ])

        self._timer_hint.setText(self._tr("timer.hint"))
        self._save_profile_btn.setText(self._tr("button.save"))
        self._load_profile_btn.setText(self._tr("button.load"))
        self._log_text.setPlaceholderText(self._tr("log.placeholder"))

        for action, (label, label_key) in self._hotkey_labels.items():
            label.setText(self._tr(label_key))
        for btn in self._click_record_buttons.values():
            btn.set_recording_text(self._tr("hotkey.press_key"))

        self._engine.set_translator(self._tr)
        self._on_timer_mode_changed()
        self._on_status_changed(self._current_status)
        self._language_apply_mode = None

    def _connect_system_theme_listener(self):
        app = QApplication.instance()
        if not app:
            return
        signal = getattr(app.styleHints(), "colorSchemeChanged", None)
        if signal is None:
            return
        try:
            signal.connect(self._on_system_theme_changed)
        except TypeError:
            pass

    def _on_theme_mode_changed(self, *args):
        self._config.set("theme_mode", self._current_theme_mode())
        self._config.save()
        self._apply_theme_mode()

    def _on_language_mode_changed(self, *args):
        self._config.set("language_mode", self._current_language_mode())
        self._config.save()
        self._apply_language()

    def _on_system_theme_changed(self, *args):
        if self._current_theme_mode() == "system":
            self._apply_theme_mode()

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

    def _on_timer_mode_changed(self, *args):
        """定时器模式切换：持续运行时隐藏秒数输入，显示提示"""
        is_continuous = (self._timer_combo.currentData() == "continuous")
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
        self._current_status = status
        if status == "running":
            self._status_label.setText(self._tr("status.running"))
            self._status_label.setObjectName("status_running")
            self._start_btn.setText(self._tr("button.pause"))
        elif status == "paused":
            self._status_label.setText(self._tr("status.paused"))
            self._status_label.setObjectName("status_stopped")
            self._start_btn.setText(self._tr("button.resume"))
        elif status == "waiting":
            self._status_label.setText(self._tr("status.waiting"))
            self._status_label.setObjectName("status_stopped")
        else:
            self._status_label.setText(self._tr("status.idle"))
            self._status_label.setObjectName("status_stopped")
            self._start_btn.setText(self._tr("button.start"))
        self._stop_btn.setText(self._tr("button.stop"))

        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)

    def _on_log(self, msg):
        ts = time.strftime("%H:%M:%S")
        self._log_text.append(f"[{ts}] {msg}")

    def _on_elapsed(self, seconds):
        if seconds < 0:
            self._time_stat.set_value(f"-{-seconds:.0f}{self._tr('unit.second')}")
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
        self._on_log(self._tr("log.profile_saved", name=name))

    def _on_load_profile(self):
        name = self._profile_combo.currentText().strip()
        if not name:
            return
        self._config.load_profile(name)
        self._load_config_to_ui()
        self._apply_config()
        self._on_log(self._tr("log.profile_loaded", name=name))

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
