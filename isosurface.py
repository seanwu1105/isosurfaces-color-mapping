import argparse
import sys

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkIOXML import vtkXMLImageDataReader
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkColorTransferFunction,
    vtkDataSetMapper,
)

from src.clipping import (
    add_axes_clip_args,
    build_axes_clip_sliders,
    get_axes_clip_filter,
)
from src.color_map import COLOR_MAP_ISOVALUE_DEFAULT
from src.isovalue import build_isovalue_slider, get_isovalue_mid
from src.read_vti import read_vti
from src.vtk_side_effects import import_for_rendering_core
from src.vtk_widget import build_default_vtk_renderer, build_default_vtk_widget
from src.window import build_default_window


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("--value", type=int)
    add_axes_clip_args(parser)
    return parser.parse_args()


# Use GUI widgets to store the state of the application.
# pylint: disable=too-many-locals
def build_gui(
    reader: vtkXMLImageDataReader,
    isovalue_default: int | None,
    clips_default: list[int],
):
    def on_clip_changed():
        change_clip(vtk_widget, *(slider.value() for slider in clip_sliders))

    window, central, layout = build_default_window()

    vtk_widget, change_isovalue, change_clip = build_vtk_widget(
        central, reader, isovalue_default, clips_default
    )
    layout.addWidget(vtk_widget, 0, 0, 1, -1)

    _isovalue_default = (
        isovalue_default if isovalue_default else get_isovalue_mid(reader)
    )
    build_isovalue_slider(layout, 1, reader, _isovalue_default, change_isovalue)

    clip_sliders = build_axes_clip_sliders(layout, 2, clips_default, on_clip_changed)

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

    isovalue_mid = get_isovalue_mid(reader)

    contour_filter = vtkContourFilter()
    contour_index = 0

    # Force the filter to have initial value. If not, the filter will not
    # generate any output even if the value is changed.
    contour_filter.SetValue(contour_index, isovalue_mid)
    contour_filter.SetInputConnection(reader.GetOutputPort())

    clip_filter, change_clips = get_axes_clip_filter()
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

    # Set to user defined value if provided.
    change_isovalue(isovalue_default if isovalue_default else isovalue_mid)
    # Set to user defined value after we have the widget.
    change_clips(widget, *clips_default)

    return widget, change_isovalue, change_clips


if __name__ == "__main__":
    import_for_rendering_core()
    args = parse_args()
    app = QApplication()
    gui = build_gui(read_vti(args.input), args.value, args.clip)
    gui.show()
    sys.exit(app.exec())
