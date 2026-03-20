from PyQt6.QtCore import pyqtSignal, QObject

class Counter(QObject):
    # signal
    valueChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._val = 0

    def increment(self):
        self._val += 1
        # gen signal (emit)
        self.valueChanged.emit(self._val)

    def getValue(self) -> int :
        return self._val