import os
import glob
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, QTimer, Qt

from OCC.Display.backend import load_backend

from OCC.Core.AIS import AIS_Shape
from OCC.Core.Quantity import Quantity_NOC_CYAN, Quantity_Color
from OCC.Core.Prs3d import Prs3d_LineAspect
from OCC.Core.Aspect import Aspect_TOL_SOLID
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib

load_backend("pyqt6")

from OCC.Display.qtDisplay import qtViewer3d
from OCC.Core.BRepTools import breptools
from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Shape


class IFCViewport(QWidget):
    element_selected_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = qtViewer3d(self)
        self.layout.addWidget(self.canvas)

        self.canvas.InitDriver()
        self.display = self.canvas._display

        self.display.set_bg_gradient_color([51, 51, 51], [51, 51, 51])

        self.ais_dict = {}
        self._is_updating_selection = False

        self._original_mouseDoubleClickEvent = self.canvas.mouseDoubleClickEvent
        self.canvas.mouseDoubleClickEvent = self.on_canvas_double_click

        self.cx = 0.0
        self.cy = 0.0
        self.cz = 0.0

    def showEvent(self, event):
        super().showEvent(event)
        self.canvas.InitDriver()
        self.canvas.update()
        if hasattr(self, 'display'):
            self.display.FitAll()

    def load_model(self, dir_path: str):
        self.display.EraseAll()
        self.ais_dict.clear()

        builder = BRep_Builder()
        brep_files = glob.glob(os.path.join(dir_path, "*.brep"))

        for file_path in brep_files:
            shape = TopoDS_Shape()
            breptools.Read(shape, file_path, builder)

            my_ais_shape = AIS_Shape(shape)
            drawer = my_ais_shape.Attributes()

            drawer.SetFaceBoundaryDraw(True)
            cyan_color = Quantity_Color(Quantity_NOC_CYAN)

            if drawer.FaceBoundaryAspect() is None:
                new_aspect = Prs3d_LineAspect(cyan_color, Aspect_TOL_SOLID, 1.5)
                drawer.SetFaceBoundaryAspect(new_aspect)
            else:
                drawer.FaceBoundaryAspect().SetColor(cyan_color)
                drawer.FaceBoundaryAspect().SetWidth(1.5)

            self.display.Context.Display(my_ais_shape, False)

            filename = os.path.basename(file_path)
            global_id = os.path.splitext(filename)[0]
            self.ais_dict[my_ais_shape] = global_id

        self.display.Context.UpdateCurrentViewer()
        self.display.FitAll()

    def on_canvas_double_click(self, event):
        self._original_mouseDoubleClickEvent(event)

        if event.button() == Qt.MouseButton.LeftButton:

            if self._is_updating_selection:
                return

            self.display.Context.InitSelected()
            if self.display.Context.MoreSelected():
                selected_ais = self.display.Context.SelectedInteractive()

                found_guid = None
                for ais, guid in self.ais_dict.items():
                    if str(ais.this) == str(selected_ais.this) or ais == selected_ais:
                        found_guid = guid
                        break

                if found_guid:
                    QTimer.singleShot(10, lambda g=found_guid: self.element_selected_signal.emit(g))

    def select_and_rotate(self, global_id):
        target_ais = None
        for ais, guid in self.ais_dict.items():
            if guid == global_id:
                target_ais = ais
                break

        self._is_updating_selection = True

        if target_ais:
            self.display.Context.ClearSelected(False)
            self.display.Context.SetSelected(target_ais, True)
            self.display.Context.UpdateCurrentViewer()

            bbox = Bnd_Box()
            brepbndlib.Add(target_ais.Shape(), bbox)
            xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
            self.cx = (xmin + xmax) / 2.0
            self.cy = (ymin + ymax) / 2.0
            self.cz = (zmin + zmax) / 2.0

            self.display.View.SetAt(self.cx, self.cy, self.cz)

            max_size = max(xmax - xmin, ymax - ymin, zmax - zmin)
            if max_size > 0:
                self.display.View.SetSize(max_size * 1.5)

            self.display.View.ZFitAll()
        else:
            self.display.Context.ClearSelected(True)

        self._is_updating_selection = False