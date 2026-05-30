DARK_THEME = """
QMainWindow, QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
    font-size: 13px;
}

QLabel {
    color: #c9d1d9;
    background: transparent;
}

QLabel#title {
    font-size: 18px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#subtitle {
    font-size: 11px;
    color: #8b949e;
}

QLabel#status_running {
    color: #3fb950;
    font-weight: bold;
    font-size: 14px;
}

QLabel#status_stopped {
    color: #f85149;
    font-weight: bold;
    font-size: 14px;
}

QLabel#stat_value {
    font-size: 22px;
    font-weight: bold;
    color: #58a6ff;
}

QLabel#stat_label {
    font-size: 11px;
    color: #8b949e;
}

QFrame#card {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 16px;
}

QFrame#header {
    background-color: #161b22;
    border-bottom: 1px solid #21262d;
    padding: 8px 16px;
}

QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #484f58;
}

QPushButton:pressed {
    background-color: #282e36;
}

QPushButton#accent {
    background-color: #238636;
    color: #ffffff;
    border: none;
}

QPushButton#accent:hover {
    background-color: #2ea043;
}

QPushButton#accent:pressed {
    background-color: #196c2e;
}

QPushButton#danger {
    background-color: #da3633;
    color: #ffffff;
    border: none;
}

QPushButton#danger:hover {
    background-color: #f85149;
}

QPushButton#danger:pressed {
    background-color: #b62324;
}

QPushButton#record_btn {
    background-color: #1c2128;
    color: #8b949e;
    border: 1px dashed #30363d;
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 12px;
}

QPushButton#record_btn:hover {
    border-color: #58a6ff;
    color: #58a6ff;
}

QPushButton#record_btn.recording {
    border-color: #f85149;
    color: #f85149;
    border-style: solid;
}

QSlider::groove:horizontal {
    background: #21262d;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #58a6ff;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #79c0ff;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1f6feb, stop:1 #58a6ff);
    border-radius: 3px;
}

QComboBox {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 6px 12px;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #484f58;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #8b949e;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    selection-background-color: #21262d;
    selection-color: #58a6ff;
    border-radius: 8px;
    padding: 4px;
}

QSpinBox, QDoubleSpinBox {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 6px 8px;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #484f58;
}

QSpinBox::up-button, QSpinBox::down-button {
    background: transparent;
    border: none;
    width: 16px;
}

QLineEdit {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 6px 12px;
}

QLineEdit:focus {
    border-color: #58a6ff;
}

QTextEdit, QPlainTextEdit {
    background-color: #0d1117;
    color: #8b949e;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
}

QGroupBox {
    color: #c9d1d9;
    border: 1px solid #21262d;
    border-radius: 8px;
    margin-top: 8px;
    padding-top: 16px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

QScrollBar:vertical {
    background: #0d1117;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #484f58;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QToolTip {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px;
}

QTabWidget::pane {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #0d1117;
    color: #8b949e;
    padding: 8px 16px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #161b22;
    color: #58a6ff;
}

QTabBar::tab:hover {
    color: #c9d1d9;
}
"""
