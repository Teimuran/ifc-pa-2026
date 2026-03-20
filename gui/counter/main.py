from counter.counter import Counter

import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMainWindow
from PyQt6.QtCore import pyqtSignal, QObject, QSize

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.counter = Counter()

        self.setWindowTitle("Counter")
        self.setFixedSize(QSize(400, 300))

        btn = QPushButton("Press for +1")
        txt = QLabel(str(self.counter.getValue()))

        main_widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(btn)
        layout.addWidget(txt)

        main_widget.setLayout(layout)

        self.setCentralWidget(main_widget)

        btn.clicked.connect(self.counter.increment)
        self.counter.valueChanged.connect(txt.setNum)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()