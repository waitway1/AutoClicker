import sys
import os

# Ensure working directory is the script directory (for PyInstaller)
if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.styles import get_theme_stylesheet
from ui.main_window import MainWindow
from core.config_manager import ConfigManager


def main():
    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("AutoClicker Pro")
    app.setStyle("Fusion")

    # Default font
    font = QFont("Microsoft YaHei UI", 10)
    app.setFont(font)

    config = ConfigManager()
    app.setStyleSheet(get_theme_stylesheet(config.get("theme_mode", "system")))

    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
