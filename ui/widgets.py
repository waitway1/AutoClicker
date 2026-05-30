from PySide6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QPushButton,
    QGraphicsDropShadowEffect, QSpinBox,
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QColor


class NoScrollSpinBox(QSpinBox):
    """屏蔽鼠标滚轮的 SpinBox，只能点击或输入修改数值。"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # StrongFocus = 只有点击或Tab才能获得焦点，悬停/滚轮不会触发
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, event):
        event.ignore()

    def focusInEvent(self, event):
        # 只接受鼠标点击和Tab键触发的焦点，忽略其他来源
        if event.reason() in (Qt.MouseFocusReason, Qt.TabFocusReason, Qt.BacktabFocusReason):
            super().focusInEvent(event)
        else:
            event.ignore()


class Card(QFrame):
    """Rounded dark card container."""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 14, 16, 14)
        self._layout.setSpacing(10)

        if title:
            lbl = QLabel(title)
            lbl.setStyleSheet("font-weight: bold; font-size: 13px; color: #e6edf3;")
            self._layout.addWidget(lbl)

    def add_widget(self, w):
        self._layout.addWidget(w)

    def add_layout(self, l):
        self._layout.addLayout(l)


class StatCard(QFrame):
    """Small statistic display card."""

    def __init__(self, label_text, value_text="0", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)

        self.value_label = QLabel(value_text)
        self.value_label.setObjectName("stat_value")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)

        self.text_label = QLabel(label_text)
        self.text_label.setObjectName("stat_label")
        self.text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.text_label)

    def set_value(self, text):
        self.value_label.setText(str(text))


class ToggleSwitch(QWidget):
    """iOS-style toggle switch."""
    toggled = Signal(bool)

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 24)
        self._checked = checked
        self._circle_x = 18 if checked else 4
        self.setCursor(Qt.PointingHandCursor)

    def isChecked(self):
        return self._checked

    def setChecked(self, v):
        self._checked = v
        self._circle_x = 18 if v else 4
        self.update()

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self.toggled.emit(self._checked)
        self.update()

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter, QBrush, QPen
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Track
        color = QColor("#238636") if self._checked else QColor("#30363d")
        p.setBrush(QBrush(color))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, 44, 24, 12, 12)

        # Handle
        target_x = 22 if self._checked else 4
        p.setBrush(QBrush(QColor("#ffffff")))
        p.drawEllipse(target_x, 2, 20, 20)
        p.end()


class SectionLabel(QLabel):
    """Small section header label."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #8b949e; "
            "text-transform: uppercase; letter-spacing: 0.5px; background: transparent;"
        )


class HotkeyButton(QPushButton):
    """Button that records a hotkey when clicked."""
    hotkey_recorded = Signal(str, str)  # action_name, key_name

    def __init__(self, action_name, key_name="...", parent=None):
        super().__init__(key_name, parent)
        self.setObjectName("record_btn")
        self.action_name = action_name
        self.setFixedHeight(30)
        self.setMinimumWidth(80)
        self._recording = False

    def set_recording_state(self, recording):
        self._recording = recording
        if recording:
            self.setText("请按键...")
            self.setProperty("class", "recording")
        else:
            self.setProperty("class", "")
        self.style().unpolish(self)
        self.style().polish(self)

    def set_key_name(self, name):
        self.setText(name)
        self.set_recording_state(False)


class AccentButton(QPushButton):
    """Primary accent button."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("accent")
        self.setFixedHeight(36)
        self.setCursor(Qt.PointingHandCursor)


class DangerButton(QPushButton):
    """Red danger button."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("danger")
        self.setFixedHeight(36)
        self.setCursor(Qt.PointingHandCursor)
