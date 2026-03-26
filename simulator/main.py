import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from simulator.ui.main_window import MainWindow


def resource_path(*parts):
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_dir, *parts)


def main():
    app = QApplication(sys.argv)
    icon_path = resource_path("assets", "mouse_key_simulator.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    window.setWindowTitle("鼠标键盘流程模拟器")
    window.resize(760, 840)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
