from gui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication

import sys

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()