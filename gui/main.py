import sys

from PyQt6.QtWidgets import ( 
    QApplication, 
    QWidget, 
    QVBoxLayout, 
    QTreeWidget,
    QMainWindow, 
    QSplitter,
    QTextEdit,
    )
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IFC editor")
        self.resize(800, 600)

        #main widgets
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        #splitters
        v_splitter = QSplitter(Qt.Orientation.Vertical)
        v_splitter.setSizes([500, 100])
        h_splitter = QSplitter(Qt.Orientation.Horizontal) 
        
        #empty widgets (empty just now)
        tree = QTreeWidget()
        tree.setHeaderLabel("Struct of IFC")
        
        viewport = QWidget()
        viewport.setStyleSheet("background-color: #333333;") #just color

        bottom_panel = QTextEdit()
        bottom_panel.setPlaceholderText("Place for logs")

        h_splitter.addWidget(tree)
        h_splitter.addWidget(viewport)

        v_splitter.addWidget(h_splitter)
        v_splitter.addWidget(bottom_panel)


        main_layout.addWidget(v_splitter)

        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)




app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()