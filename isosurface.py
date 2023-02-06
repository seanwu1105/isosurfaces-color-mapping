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
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import vtkActor, vtkDataSetMapper, vtkRenderer

from src.vtk_side_effects import import_for_rendering_core

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

CLIP_X_MIN = 1
CLIP_X_DEFAULT_MAX = 250
CLIP_X_DEFAULT = CLIP_X_DEFAULT_MAX

CLIP_Y_MIN = 1
CLIP_Y_DEFAULT_MAX = 250
CLIP_Y_DEFAULT = CLIP_Y_DEFAULT_MAX

CLIP_Z_MIN = 1
CLIP_Z_DEFAULT_MAX = 270
CLIP_Z_DEFAULT = CLIP_Z_DEFAULT_MAX


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("--value", type=int)
    parser.add_argument(
        "--clip",
        nargs=3,
        type=int,
        default=[CLIP_X_DEFAULT, CLIP_Y_DEFAULT, CLIP_Z_DEFAULT],
    )
    return parser.parse_args()


def read_data(data_filename: str):
    reader = vtkXMLImageDataReader()
    reader.SetFileName(data_filename)
    reader.Update()
    return reader


# Use GUI wigets to store the state of the application.
# pylint: disable=too-many-locals
def build_gui(
    reader: vtkXMLImageDataReader,
    isovalue_default: int | None,
    clips_default: list[int],
):
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
        central, reader, isovalue_default
    )
    layout.addWidget(vtk_widget, 0, 0, 1, -1)

    _isovalue_default = (
        isovalue_default if isovalue_default else get_default_isovalue(reader)
    )
    isovalue_min: float
    isovalue_max: float
    isovalue_min, isovalue_max = reader.GetOutput().GetScalarRange()
    layout.addWidget(QLabel("Isovalue"), 1, 0)
    isovalue_slider = QSlider(Qt.Orientation.Horizontal)
    isovalue_slider.setMinimum(int(isovalue_min))
    isovalue_slider.setMaximum(max(int(isovalue_max), _isovalue_default))
    isovalue_slider.setValue(_isovalue_default)
    isovalue_slider.valueChanged.connect(on_isovalue_changed)  # type: ignore
    layout.addWidget(isovalue_slider, 1, 1)
    isovalue_label = QLabel(str(_isovalue_default))
    layout.addWidget(isovalue_label, 1, 2)

    clip_widgets = {
        "Clip X": (CLIP_X_MIN, CLIP_X_DEFAULT_MAX, clips_default[0]),
        "Clip Y": (CLIP_Y_MIN, CLIP_Y_DEFAULT_MAX, clips_default[1]),
        "Clip Z": (CLIP_Z_MIN, CLIP_Z_DEFAULT_MAX, clips_default[2]),
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


# pylint: disable=too-many-locals
def build_vtk_widget(
    parent: QObject,
    reader: vtkXMLImageDataReader,
    isovalue_default: int | None,
):
    def change_isovalue(value: int):
        contour_filter.SetValue(contour_index, value)
        widget.GetRenderWindow().Render()

    def change_clips(x: float, y: float, z: float):
        clip_planes.SetBounds(
            CLIP_X_MIN - 1,
            x,
            CLIP_Y_MIN - 1,
            y,
            CLIP_Z_MIN - 1,
            z,
        )
        widget.GetRenderWindow().Render()

    isovalue_range: tuple[float, float] = reader.GetOutput().GetScalarRange()

    _isovalue_default = get_default_isovalue(reader)

    contour_filter = vtkContourFilter()
    contour_index = 0

    # Force the filter to have initial value. If not, the filter will not
    # generate any output even if the value is changed.
    contour_filter.SetValue(contour_index, _isovalue_default)
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
    mapper.SetScalarRange(isovalue_range)
    mapper.SetInputConnection(clip_filter.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)

    scalar_bar = vtkScalarBarActor()
    scalar_bar.SetLookupTable(mapper.GetLookupTable())  # type: ignore

    renderer = vtkRenderer()
    renderer.AddActor(actor)
    renderer.AddActor2D(scalar_bar)
    colors = vtkNamedColors()
    renderer.SetBackground(colors.GetColor3d("Gray"))  # type: ignore

    widget = QVTKRenderWindowInteractor(parent)
    widget.GetRenderWindow().AddRenderer(renderer)
    widget.GetRenderWindow().GetInteractor().Initialize()

    change_isovalue(isovalue_default if isovalue_default else _isovalue_default)

    return widget, change_isovalue, change_clips


def get_default_isovalue(reader: vtkXMLImageDataReader) -> int:
    isovalue_range: tuple[float, float] = reader.GetOutput().GetScalarRange()
    return int((isovalue_range[0] + isovalue_range[1]) / 2)


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


if __name__ == "__main__":
    import_for_rendering_core()
    args = parse_args()
    app = QApplication()
    gui = build_gui(read_data(args.input), args.value, args.clip)
    gui.show()
    sys.exit(app.exec())
