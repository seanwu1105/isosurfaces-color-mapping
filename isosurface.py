import argparse
import sys

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QMainWindow,
    QSlider,
    QWidget,
)
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkIOXML import vtkXMLImageDataReader
from vtkmodules.vtkRenderingCore import vtkActor, vtkDataSetMapper, vtkRenderer

from src.vtk_side_effects import import_for_rendering_core

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
ISOVALUE_MIN = 0
ISOVALUE_MAX = 3000
ISOVALUE_DEFAULT = 1000


def build_vtk_widget(parent: QObject, data_filename: str):
    def change_isovalue(value: int):
        contour_filter.SetValue(0, value)
        widget.GetRenderWindow().Render()

    reader = vtkXMLImageDataReader()
    reader.SetFileName(data_filename)

    contour_filter = vtkContourFilter()

    # Force the filter to have initial value. If not, the filter will not
    # generate any output even if the value is changed.
    contour_filter.SetValue(0, ISOVALUE_DEFAULT)

    contour_filter.SetInputConnection(reader.GetOutputPort())

    mapper = vtkDataSetMapper()
    mapper.SetScalarVisibility(False)
    mapper.SetInputConnection(contour_filter.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)

    renderer = vtkRenderer()
    renderer.AddActor(actor)
    colors = vtkNamedColors()
    renderer.SetBackground(colors.GetColor3d("Gray"))  # type: ignore

    widget = QVTKRenderWindowInteractor(parent)
    widget.GetRenderWindow().AddRenderer(renderer)
    widget.GetRenderWindow().GetInteractor().Initialize()
    return widget, change_isovalue


def build_gui(data_filename: str, default_isovalue: int):
    window = QMainWindow()
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    central = QWidget()
    layout = QGridLayout()

    vtk_widget, change_isovalue = build_vtk_widget(central, data_filename)
    change_isovalue(default_isovalue)

    layout.addWidget(vtk_widget, 0, 0, 1, -1)
    layout.addWidget(QLabel("Isovalue"), 1, 0)

    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(ISOVALUE_MIN)
    slider.setMaximum(max(ISOVALUE_MAX, default_isovalue))
    slider.setValue(default_isovalue)
    slider.valueChanged.connect(change_isovalue)  # type: ignore

    layout.addWidget(slider, 1, 1)

    central.setLayout(layout)
    window.setCentralWidget(central)
    return window


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("--value", type=int, default=ISOVALUE_DEFAULT)
    parser.add_argument("--clip", nargs=3, type=float, default=[0.0, 0.0, 0.0])
    return parser.parse_args()


if __name__ == "__main__":
    import_for_rendering_core()
    args = parse_args()
    app = QApplication()
    gui = build_gui(args.input, args.value)
    gui.show()
    sys.exit(app.exec())
