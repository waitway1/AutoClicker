from __future__ import annotations

import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt


THEME_MODES = ("system", "light", "dark")


def system_prefers_dark() -> bool:
    app = QGuiApplication.instance()
    if app is not None:
        hints = app.styleHints()
        color_scheme = getattr(hints, "colorScheme", None)
        if callable(color_scheme):
            try:
                return color_scheme() == Qt.ColorScheme.Dark
            except Exception:
                pass

    if sys.platform.startswith("win"):
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except OSError:
            pass

    return False


def resolve_theme_mode(mode: str | None) -> str:
    if mode not in THEME_MODES:
        mode = "system"
    if mode == "system":
        return "dark" if system_prefers_dark() else "light"
    return mode


def get_theme_stylesheet(mode: str | None) -> str:
    resolved = resolve_theme_mode(mode)
    palette = _DARK if resolved == "dark" else _LIGHT
    return _STYLE_TEMPLATE.format(**palette)


_LIGHT = {
    "window": "#f5f5f7",
    "panel": "#fbfbfd",
    "panel_alt": "#ffffff",
    "elevated": "#ffffff",
    "header": "rgba(255, 255, 255, 0.94)",
    "text": "#1d1d1f",
    "muted": "#6e6e73",
    "subtle": "#86868b",
    "border": "#d2d2d7",
    "border_soft": "#e5e5ea",
    "control": "#f2f2f7",
    "control_hover": "#e8e8ed",
    "control_pressed": "#dedee3",
    "accent": "#007aff",
    "accent_hover": "#0a84ff",
    "accent_pressed": "#0062cc",
    "accent_soft": "#eaf4ff",
    "success": "#34c759",
    "success_hover": "#30d158",
    "danger": "#ff3b30",
    "danger_hover": "#ff453a",
    "danger_pressed": "#d70015",
    "console": "#f8f8fa",
    "selection": "#d7ebff",
}

_DARK = {
    "window": "#1c1c1e",
    "panel": "#242426",
    "panel_alt": "#2c2c2e",
    "elevated": "#2c2c2e",
    "header": "rgba(28, 28, 30, 0.96)",
    "text": "#f5f5f7",
    "muted": "#a1a1a6",
    "subtle": "#8e8e93",
    "border": "#3a3a3c",
    "border_soft": "#38383a",
    "control": "#3a3a3c",
    "control_hover": "#48484a",
    "control_pressed": "#545456",
    "accent": "#0a84ff",
    "accent_hover": "#409cff",
    "accent_pressed": "#006edb",
    "accent_soft": "#172d45",
    "success": "#30d158",
    "success_hover": "#32d74b",
    "danger": "#ff453a",
    "danger_hover": "#ff6961",
    "danger_pressed": "#d70015",
    "console": "#1f1f21",
    "selection": "#17324d",
}

_STYLE_TEMPLATE = """
QMainWindow, QWidget {{
    background-color: {window};
    color: {text};
    font-family: 'Microsoft YaHei UI', 'Segoe UI Variable', 'SF Pro Display', 'Segoe UI', sans-serif;
    font-size: 13px;
}}

QScrollArea, QScrollArea > QWidget > QWidget {{
    background-color: {window};
}}

QLabel {{
    color: {text};
    background: transparent;
}}

QLabel#title {{
    font-size: 18px;
    font-weight: 700;
    color: {text};
}}

QLabel#subtitle {{
    font-size: 11px;
    color: {muted};
}}

QLabel#section_label {{
    font-size: 11px;
    font-weight: 700;
    color: {muted};
    background: transparent;
}}

QLabel#card_title {{
    font-size: 13px;
    font-weight: 700;
    color: {text};
}}

QLabel#status_running {{
    color: {success};
    font-weight: 700;
    font-size: 13px;
}}

QLabel#status_stopped {{
    color: {danger};
    font-weight: 700;
    font-size: 13px;
}}

QLabel#stat_value {{
    font-size: 23px;
    font-weight: 750;
    color: {accent};
}}

QLabel#stat_label {{
    font-size: 11px;
    color: {muted};
}}

QFrame#card, QFrame#stat_card {{
    background-color: {panel_alt};
    border: 1px solid {border_soft};
    border-radius: 14px;
}}

QFrame#header {{
    background-color: {header};
    border-bottom: 1px solid {border_soft};
}}

QPushButton {{
    background-color: {control};
    color: {text};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 8px 16px;
    font-weight: 600;
    min-height: 22px;
}}

QPushButton:hover {{
    background-color: {control_hover};
    border-color: {border};
}}

QPushButton:pressed {{
    background-color: {control_pressed};
}}

QPushButton#accent {{
    background-color: {accent};
    color: #ffffff;
    border: none;
}}

QPushButton#accent:hover {{
    background-color: {accent_hover};
}}

QPushButton#accent:pressed {{
    background-color: {accent_pressed};
}}

QPushButton#danger {{
    background-color: {danger};
    color: #ffffff;
    border: none;
}}

QPushButton#danger:hover {{
    background-color: {danger_hover};
}}

QPushButton#danger:pressed {{
    background-color: {danger_pressed};
}}

QPushButton#record_btn {{
    background-color: {control};
    color: {muted};
    border: 1px dashed {border};
    border-radius: 9px;
    padding: 5px 12px;
    font-size: 12px;
}}

QPushButton#record_btn:hover {{
    border-color: {accent};
    color: {accent};
}}

QPushButton#record_btn[class="recording"] {{
    border-color: {danger};
    color: {danger};
    border-style: solid;
}}

QSlider::groove:horizontal {{
    background: {control};
    height: 6px;
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {accent};
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border: 2px solid {panel_alt};
    border-radius: 9px;
}}

QSlider::handle:horizontal:hover {{
    background: {accent_hover};
}}

QSlider::sub-page:horizontal {{
    background: {accent};
    border-radius: 3px;
}}

QComboBox {{
    background-color: {control};
    color: {text};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 7px 12px;
    min-height: 22px;
}}

QComboBox:hover {{
    background-color: {control_hover};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {subtle};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {elevated};
    color: {text};
    border: 1px solid {border};
    selection-background-color: {selection};
    selection-color: {text};
    border-radius: 10px;
    padding: 4px;
}}

QSpinBox, QDoubleSpinBox, QLineEdit {{
    background-color: {control};
    color: {text};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 7px 10px;
}}

QSpinBox:hover, QDoubleSpinBox:hover, QLineEdit:hover {{
    background-color: {control_hover};
}}

QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {{
    border-color: {accent};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background: transparent;
    border: none;
    width: 16px;
}}

QTextEdit, QPlainTextEdit {{
    background-color: {console};
    color: {muted};
    border: 1px solid {border_soft};
    border-radius: 10px;
    padding: 8px;
    font-family: 'Cascadia Mono', 'Consolas', 'Courier New', monospace;
    font-size: 11px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {border};
    border-radius: 4px;
    min-height: 32px;
}}

QScrollBar::handle:vertical:hover {{
    background: {subtle};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QToolTip {{
    background-color: {elevated};
    color: {text};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 7px;
}}
"""

DARK_THEME = get_theme_stylesheet("dark")
LIGHT_THEME = get_theme_stylesheet("light")
