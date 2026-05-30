import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QRegion


class CircleOverlay(QWidget):
    """Transparent fullscreen overlay showing the click circle."""
    circle_changed = Signal(int, int, int)  # x, y, radius

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self._cx = 960
        self._cy = 540
        self._radius = 50
        self._visible = True
        self._dragging = False
        self._drag_offset = QPoint(0, 0)
        self._resizing = False
        self._interaction_enabled = False

        # Pulse animation
        self._pulse_phase = 0.0
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._tick_pulse)
        self._pulse_timer.start(50)

    def set_circle(self, x, y, radius):
        self._cx = x
        self._cy = y
        self._radius = max(10, min(500, radius))
        self.update()

    def get_circle(self):
        return self._cx, self._cy, self._radius

    def set_overlay_visible(self, v):
        self._visible = v
        self.update()

    def enable_interaction(self, v):
        self._interaction_enabled = v
        if v:
            self.setWindowFlags(
                Qt.FramelessWindowHint
                | Qt.WindowStaysOnTopHint
                | Qt.Tool
            )
        else:
            self.setWindowFlags(
                Qt.FramelessWindowHint
                | Qt.WindowStaysOnTopHint
                | Qt.Tool
                | Qt.WindowTransparentForInput
            )
        self.show()

    def _tick_pulse(self):
        self._pulse_phase += 0.08
        if self._pulse_phase > 2 * math.pi:
            self._pulse_phase -= 2 * math.pi
        if self._visible:
            self.update()

    def _point_in_circle(self, px, py):
        dx = px - self._cx
        dy = py - self._cy
        return (dx * dx + dy * dy) <= (self._radius + 15) ** 2

    def _point_on_edge(self, px, py):
        dx = px - self._cx
        dy = py - self._cy
        dist = math.sqrt(dx * dx + dy * dy)
        return abs(dist - self._radius) < 15

    def mousePressEvent(self, event):
        if not self._interaction_enabled or not self._visible:
            return
        pos = event.position().toPoint()
        if self._point_on_edge(pos.x(), pos.y()):
            self._resizing = True
        elif self._point_in_circle(pos.x(), pos.y()):
            self._dragging = True
            self._drag_offset = QPoint(pos.x() - self._cx, pos.y() - self._cy)

    def mouseMoveEvent(self, event):
        if not self._interaction_enabled:
            return
        pos = event.position().toPoint()
        if self._dragging:
            self._cx = pos.x() - self._drag_offset.x()
            self._cy = pos.y() - self._drag_offset.y()
            self.circle_changed.emit(self._cx, self._cy, self._radius)
            self.update()
        elif self._resizing:
            dx = pos.x() - self._cx
            dy = pos.y() - self._cy
            self._radius = max(10, min(500, int(math.sqrt(dx * dx + dy * dy))))
            self.circle_changed.emit(self._cx, self._cy, self._radius)
            self.update()

    def mouseReleaseEvent(self, event):
        self._dragging = False
        self._resizing = False

    def wheelEvent(self, event):
        if not self._interaction_enabled or not self._visible:
            return
        delta = event.angleDelta().y()
        step = 5 if delta > 0 else -5
        self._radius = max(10, min(500, self._radius + step))
        self.circle_changed.emit(self._cx, self._cy, self._radius)
        self.update()

    def paintEvent(self, event):
        if not self._visible:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Outer glow
        pulse = 0.6 + 0.2 * math.sin(self._pulse_phase)
        glow_color = QColor(0, 212, 255, int(30 * pulse))
        gradient = QRadialGradient(self._cx, self._cy, self._radius + 20)
        gradient.setColorAt(0.7, QColor(0, 212, 255, int(40 * pulse)))
        gradient.setColorAt(1.0, QColor(0, 212, 255, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            self._cx - self._radius - 20,
            self._cy - self._radius - 20,
            (self._radius + 20) * 2,
            (self._radius + 20) * 2,
        )

        # Circle fill
        fill_color = QColor(0, 212, 255, int(20 * pulse))
        painter.setBrush(QBrush(fill_color))
        pen = QPen(QColor(0, 212, 255, int(180 * pulse)), 2)
        painter.setPen(pen)
        painter.drawEllipse(
            self._cx - self._radius,
            self._cy - self._radius,
            self._radius * 2,
            self._radius * 2,
        )

        # Crosshair
        ch_len = min(10, self._radius // 3)
        ch_color = QColor(0, 212, 255, int(120 * pulse))
        ch_pen = QPen(ch_color, 1, Qt.DashLine)
        painter.setPen(ch_pen)
        painter.drawLine(self._cx - ch_len, self._cy, self._cx + ch_len, self._cy)
        painter.drawLine(self._cx, self._cy - ch_len, self._cx, self._cy + ch_len)

        # Center dot
        painter.setBrush(QBrush(QColor(0, 212, 255, int(200 * pulse))))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self._cx - 3, self._cy - 3, 6, 6)

        # Radius label
        painter.setPen(QColor(0, 212, 255, int(160 * pulse)))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(
            self._cx + self._radius + 8,
            self._cy - 4,
            f"r={self._radius}",
        )

        painter.end()
