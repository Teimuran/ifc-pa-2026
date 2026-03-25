from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyvista as pv
from pyvistaqt import QtInteractor

class IFCViewport(QWidget):
    def __init__(self):
        super().__init__()
        
        # Настраиваем слой, чтобы 3D-окно занимало всё доступное место
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем встроенный 3D-вьюпорт от PyVista
        self.plotter = QtInteractor(self)
        self.layout.addWidget(self.plotter.interactor)
        
        # Настраиваем красивый темный фон
        self.plotter.set_background("#333333")

    def load_model(self, file_path: str):
        """ Загружает .vtm файл в сцену """
        # Очищаем сцену от старых моделей, если они были
        self.plotter.clear()
        
        # Загружаем мультиблок, который сгенерировала команда
        multiblock = pv.read(file_path)
        
        # Добавляем модель на сцену. 
        # color="white" - базовый цвет, show_edges=True - чтобы видеть грани элементов
        self.plotter.add_mesh(multiblock, color="#e0e0e0", show_edges=True)
        
        # Камера автоматически центрируется на здании
        self.plotter.reset_camera()