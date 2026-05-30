from PySide6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QPushButton,
    QGraphicsDropShadowEffect, QSpinBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


def _apply_soft_shadow(widget, blur=22, y_offset=8, alpha=24):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, y_offset)
    effect.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(effect)


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
    """Rounded card container."""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        _apply_soft_shadow(self, alpha=18)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(18, 16, 18, 16)
        self._layout.setSpacing(12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("card_title")
        self._layout.addWidget(self.title_label)

    def add_widget(self, w):
        self._layout.addWidget(w)

    def add_layout(self, l):
        self._layout.addLayout(l)

    def set_title(self, text):
        self.title_label.setText(text)


class StatCard(QFrame):
    """Small statistic display card."""

    def __init__(self, label_text, value_text="0", parent=None):
        super().__init__(parent)
        self.setObjectName("stat_card")
        _apply_soft_shadow(self, blur=18, y_offset=6, alpha=16)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(3)

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

    def set_label(self, text):
        self.text_label.setText(text)


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

        is_dark = self.palette().window().color().lightness() < 128
        off_color = QColor("#48484a") if is_dark else QColor("#d1d1d6")
        on_color = QColor("#34c759")

        color = on_color if self._checked else off_color
        p.setBrush(QBrush(color))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, 44, 24, 12, 12)

        target_x = 22 if self._checked else 4
        p.setBrush(QBrush(QColor("#ffffff")))
        p.setPen(QPen(QColor(0, 0, 0, 24), 1))
        p.drawEllipse(target_x, 2, 20, 20)
        p.end()


class SectionLabel(QLabel):
    """Small section header label."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("section_label")


class HotkeyButton(QPushButton):
    """Button that records a hotkey when clicked."""
    hotkey_recorded = Signal(str, str)  # action_name, key_name

    def __init__(self, action_name, key_name="...", parent=None):
        super().__init__(key_name, parent)
        self.setObjectName("record_btn")
        self.action_name = action_name
        self._recording_text = "请按键..."
        self.setFixedHeight(30)
        self.setMinimumWidth(80)
        self._recording = False

    def set_recording_state(self, recording):
        self._recording = recording
        if recording:
            self.setText(self._recording_text)
            self.setProperty("class", "recording")
        else:
            self.setProperty("class", "")
        self.style().unpolish(self)
        self.style().polish(self)

    def set_key_name(self, name):
        self.setText(name)
        self.set_recording_state(False)

    def set_recording_text(self, text):
        self._recording_text = text
        if self._recording:
            self.setText(text)

    def key_name(self):
        if self._recording:
            return ""
        return self.text()


class AccentButton(QPushButton):
    """Primary accent button."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("accent")
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)


class DangerButton(QPushButton):
    """Red danger button."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("danger")
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)
