import argparse
import sys
from typing import TypedDict

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QGridLayout, QMainWindow, QWidget
from vtkmodules.vtkFiltersCore import vtkContourFilter, vtkProbeFilter
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
from src.color_map import get_inferno16_color_map
from src.vtk_side_effects import import_for_rendering_core
from src.vtk_widget import build_default_vtk_renderer, build_default_vtk_widget
from src.window import WINDOW_HEIGHT, WINDOW_WIDTH


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-g", "--grad", required=True)
    parser.add_argument("-v", "--value", required=True)
    parser.add_argument("--cmap")
    add_axes_clip_args(parser)
    return parser.parse_args()


def read_selected_isovalues(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        return [int(line) for line in f if line]


def read_color_map(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        return {
            int(line.split()[0]): tuple(float(x) for x in line.split()[1:])
            for line in f
            if line and not line.startswith("#")
        }


# Use GUI widgets to store the state of the application.
# pylint: disable=too-many-locals
def build_gui(
    isovalue_filename: str,
    gradient_filename: str,
    selected_isovalues: list[int],
    color_map: dict[int, tuple[float, float, float]] | None,
    clips_default: list[int],
):
    def on_clip_changed():
        change_clip(vtk_widget, *(slider.value() for slider in clip_sliders))

    window = QMainWindow()
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    central = QWidget()
    layout = QGridLayout()

    vtk_widget, change_clip = build_vtk_widget(
        central,
        isovalue_filename,
        gradient_filename,
        selected_isovalues,
        color_map,
        clips_default,
    )
    layout.addWidget(vtk_widget, 0, 0, 1, -1)

    clip_sliders = build_axes_clip_sliders(layout, 1, clips_default, on_clip_changed)

    central.setLayout(layout)
    window.setCentralWidget(central)
    return window


# pylint: disable=too-many-locals too-many-arguments
def build_vtk_widget(
    parent: QObject,
    isovalue_filename: str,
    gradient_filename: str,
    selected_isovalues: list[int],
    color_map: dict[int, tuple[float, float, float]] | None,
    axes_clips_default: list[int],
):
    isovalue_reader = vtkXMLImageDataReader()
    isovalue_reader.SetFileName(isovalue_filename)

    contour_filter = vtkContourFilter()
    for i, value in enumerate(selected_isovalues):
        contour_filter.SetValue(i, value)
    contour_filter.SetInputConnection(isovalue_reader.GetOutputPort())

    clip_filter, change_clips = get_axes_clip_filter()
    clip_filter.SetInputConnection(contour_filter.GetOutputPort())

    gradient_reader = vtkXMLImageDataReader()
    gradient_reader.SetFileName(gradient_filename)
    gradient_reader.Update()
    gradient_range: tuple[float, float] = gradient_reader.GetOutput().GetScalarRange()

    probe_filter = vtkProbeFilter()
    probe_filter.SetInputConnection(clip_filter.GetOutputPort())
    probe_filter.SetSourceConnection(gradient_reader.GetOutputPort())

    mapper = vtkDataSetMapper()
    mapper.SetInputConnection(probe_filter.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)

    scalar_bar = vtkScalarBarActor()

    if color_map is None:
        ctf = get_inferno16_color_map(gradient_range)
    else:
        ctf = vtkColorTransferFunction()
        for value, color in color_map.items():
            ctf.AddRGBPoint(value, *color)

    mapper.SetLookupTable(ctf)
    scalar_bar.SetLookupTable(ctf)

    renderer = build_default_vtk_renderer([actor], [scalar_bar])

    widget = build_default_vtk_widget(parent, renderer)

    # Set to user defined value after we have the widget.
    change_clips(widget, *axes_clips_default)

    return widget, change_clips


class IsovalueColorMapping(TypedDict):
    value: int
    color: tuple[float, float, float]


if __name__ == "__main__":
    import_for_rendering_core()
    args = parse_args()
    app = QApplication()
    gui = build_gui(
        args.input,
        args.grad,
        read_selected_isovalues(args.value),
        read_color_map(args.cmap) if args.cmap else None,
        args.clip,
    )
    gui.show()
    sys.exit(app.exec())
