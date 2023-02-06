import argparse
import sys
from typing import Callable

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
from vtkmodules.vtkCommonDataModel import vtkPlanes
from vtkmodules.vtkFiltersCore import vtkClipPolyData, vtkContourFilter
from vtkmodules.vtkIOXML import vtkXMLImageDataReader
from vtkmodules.vtkRenderingCore import vtkActor, vtkDataSetMapper, vtkRenderer

from src.vtk_side_effects import import_for_rendering_core

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

ISOVALUE_MIN = 0
ISOVALUE_DEFAULT_MAX = 3000
ISOVALUE_DEFAULT = 1000

CLIP_X_MIN = 1
CLIP_X_DEFAULT_MAX = 250
CLIP_X_DEFAULT = CLIP_X_DEFAULT_MAX

CLIP_Y_MIN = 1
CLIP_Y_DEFAULT_MAX = 250
CLIP_Y_DEFAULT = CLIP_Y_DEFAULT_MAX

CLIP_Z_MIN = 1
CLIP_Z_DEFAULT_MAX = 270
CLIP_Z_DEFAULT = CLIP_Z_DEFAULT_MAX


def build_vtk_widget(parent: QObject, data_filename: str, default_isovalue: int):
    def change_isovalue(value: int):
        contour_filter.SetValue(0, value)
        widget.GetRenderWindow().Render()

    def change_clip(x: float, y: float, z: float):
        clip_planes.SetBounds(
            CLIP_X_MIN - 1,
            x,
            CLIP_Y_MIN - 1,
            y,
            CLIP_Z_MIN - 1,
            z,
        )
        widget.GetRenderWindow().Render()

    reader = vtkXMLImageDataReader()
    reader.SetFileName(data_filename)

    contour_filter = vtkContourFilter()

    # Force the filter to have initial value. If not, the filter will not
    # generate any output even if the value is changed.
    contour_filter.SetValue(0, ISOVALUE_DEFAULT)
    contour_filter.SetInputConnection(reader.GetOutputPort())

    clip_planes = vtkPlanes()
    clip_planes.SetBounds(
        CLIP_X_MIN - 1,
        CLIP_X_DEFAULT,
        CLIP_Y_MIN - 1,
        CLIP_Y_DEFAULT,
        CLIP_Z_MIN - 1,
        CLIP_Z_DEFAULT,
    )

    clip_filter = vtkClipPolyData()
    clip_filter.SetClipFunction(clip_planes)
    clip_filter.SetInsideOut(True)
    clip_filter.SetInputConnection(contour_filter.GetOutputPort())

    mapper = vtkDataSetMapper()
    mapper.SetScalarVisibility(False)
    mapper.SetInputConnection(clip_filter.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)

    renderer = vtkRenderer()
    renderer.AddActor(actor)
    colors = vtkNamedColors()
    renderer.SetBackground(colors.GetColor3d("Gray"))  # type: ignore

    widget = QVTKRenderWindowInteractor(parent)
    widget.GetRenderWindow().AddRenderer(renderer)
    widget.GetRenderWindow().GetInteractor().Initialize()
    change_isovalue(default_isovalue)

    return widget, change_isovalue, change_clip


# pylint: disable=too-many-locals
def build_gui(data_filename: str, default_isovalue: int, default_clips: list[int]):
    def on_isovalue_changed(value: int):
        isovalue_label.setText(str(value))
        change_isovalue(value)

    def on_clip_changed():
        change_clip(*(slider.value() for slider in clip_sliders))

    window = QMainWindow()
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    central = QWidget()
    layout = QGridLayout()

    vtk_widget, change_isovalue, change_clip = build_vtk_widget(
        central, data_filename, default_isovalue
    )
    layout.addWidget(vtk_widget, 0, 0, 1, -1)

    layout.addWidget(QLabel("Isovalue"), 1, 0)

    isovalue_slider = QSlider(Qt.Orientation.Horizontal)
    isovalue_slider.setMinimum(ISOVALUE_MIN)
    isovalue_slider.setMaximum(max(ISOVALUE_DEFAULT_MAX, default_isovalue))
    isovalue_slider.setValue(default_isovalue)
    isovalue_slider.valueChanged.connect(on_isovalue_changed)  # type: ignore
    layout.addWidget(isovalue_slider, 1, 1)

    isovalue_label = QLabel(str(default_isovalue))
    layout.addWidget(isovalue_label, 1, 2)

    clip_widgets = {
        "Clip X": (CLIP_X_MIN, CLIP_X_DEFAULT_MAX, default_clips[0]),
        "Clip Y": (CLIP_Y_MIN, CLIP_Y_DEFAULT_MAX, default_clips[1]),
        "Clip Z": (CLIP_Z_MIN, CLIP_Z_DEFAULT_MAX, default_clips[2]),
    }

    clip_sliders: list[QSlider] = []

    for i, (name, (min_value, max_value, default_value)) in enumerate(
        clip_widgets.items(), start=2
    ):
        clip_sliders.append(
            build_clip_widgets(
                layout,
                i,
                name,
                min_value,
                max_value,
                default_value,
                on_clip_changed,
            )
        )

    central.setLayout(layout)
    window.setCentralWidget(central)
    return window


# pylint: disable=too-many-arguments
def build_clip_widgets(
    layout: QGridLayout,
    row: int,
    name: str,
    min_value: int,
    max_value: int,
    default_value: int,
    on_value_changed: Callable[[], None],
):
    def _on_value_changed(value: int):
        label.setText(str(value))
        on_value_changed()

    layout.addWidget(QLabel(name), row, 0)

    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(min_value)
    slider.setMaximum(max(max_value, default_value))
    slider.setValue(default_value)
    slider.valueChanged.connect(_on_value_changed)  # type: ignore
    layout.addWidget(slider, row, 1)

    label = QLabel(str(default_value))
    layout.addWidget(label, row, 2)

    return slider


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("--value", type=int, default=ISOVALUE_DEFAULT)
    parser.add_argument(
        "--clip",
        nargs=3,
        type=int,
        default=[CLIP_X_DEFAULT, CLIP_Y_DEFAULT, CLIP_Z_DEFAULT],
    )
    return parser.parse_args()


if __name__ == "__main__":
    import_for_rendering_core()
    args = parse_args()
    app = QApplication()
    gui = build_gui(args.input, args.value, args.clip)
    gui.show()
    sys.exit(app.exec())
