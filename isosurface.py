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
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkIOXML import vtkXMLImageDataReader
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkColorTransferFunction,
    vtkDataSetMapper,
)

from src.clipping import CLIPS_MAX, build_clip_sliders, get_clip_filter
from src.color_map import COLOR_MAP_ISOVALUE_DEFAULT
from src.vtk_side_effects import import_for_rendering_core
from src.vtk_widget import build_default_vtk_renderer, build_default_vtk_widget
from src.window import WINDOW_HEIGHT, WINDOW_WIDTH


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("--value", type=int)
    parser.add_argument(
        "--clip",
        nargs=3,
        type=int,
        default=CLIPS_MAX,
    )
    return parser.parse_args()


def read_data(data_filename: str):
    reader = vtkXMLImageDataReader()
    reader.SetFileName(data_filename)
    reader.Update()
    return reader


# Use GUI widgets to store the state of the application.
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
        change_clip(vtk_widget, *(slider.value() for slider in clip_sliders))

    window = QMainWindow()
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    central = QWidget()
    layout = QGridLayout()

    vtk_widget, change_isovalue, change_clip = build_vtk_widget(
        central, reader, isovalue_default, clips_default
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

    clip_sliders = build_clip_sliders(layout, 2, clips_default, on_clip_changed)

    central.setLayout(layout)
    window.setCentralWidget(central)
    return window


# pylint: disable=too-many-locals
def build_vtk_widget(
    parent: QObject,
    reader: vtkXMLImageDataReader,
    isovalue_default: int | None,
    clips_default: list[int],
):
    def change_isovalue(value: int):
        contour_filter.SetValue(contour_index, value)
        widget.GetRenderWindow().Render()

    isovalue_range: tuple[float, float] = reader.GetOutput().GetScalarRange()

    _isovalue_default = get_default_isovalue(reader)

    contour_filter = vtkContourFilter()
    contour_index = 0

    # Force the filter to have initial value. If not, the filter will not
    # generate any output even if the value is changed.
    contour_filter.SetValue(contour_index, _isovalue_default)
    contour_filter.SetInputConnection(reader.GetOutputPort())

    clip_filter, change_clips = get_clip_filter(clips_default)
    clip_filter.SetInputConnection(contour_filter.GetOutputPort())

    isovalue_color_maps = COLOR_MAP_ISOVALUE_DEFAULT
    ctf = vtkColorTransferFunction()
    for mapping in isovalue_color_maps.values():
        ctf.AddRGBPoint(mapping["value"], *mapping["color"])

    mapper = vtkDataSetMapper()
    mapper.SetScalarRange(isovalue_range)
    mapper.SetLookupTable(ctf)
    mapper.SetInputConnection(clip_filter.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)

    scalar_bar = vtkScalarBarActor()
    scalar_bar.SetLookupTable(ctf)

    renderer = build_default_vtk_renderer([actor], [scalar_bar])

    widget = build_default_vtk_widget(parent, renderer)

    change_isovalue(isovalue_default if isovalue_default else _isovalue_default)

    return widget, change_isovalue, change_clips


def get_default_isovalue(reader: vtkXMLImageDataReader) -> int:
    isovalue_range: tuple[float, float] = reader.GetOutput().GetScalarRange()
    return int((isovalue_range[0] + isovalue_range[1]) / 2)


if __name__ == "__main__":
    import_for_rendering_core()
    args = parse_args()
    app = QApplication()
    gui = build_gui(read_data(args.input), args.value, args.clip)
    gui.show()
    sys.exit(app.exec())
