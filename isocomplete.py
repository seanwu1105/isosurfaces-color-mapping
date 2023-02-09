import argparse
import sys
from typing import Callable, TypedDict

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkFiltersCore import vtkClipPolyData, vtkContourFilter, vtkProbeFilter
from vtkmodules.vtkIOXML import vtkXMLImageDataReader
from vtkmodules.vtkRenderingCore import vtkActor, vtkDataSetMapper

from src.clipping import (
    add_axes_clip_args,
    build_axes_clip_sliders,
    get_axes_clip_filter,
)
from src.vtk_side_effects import import_for_rendering_core
from src.vtk_widget import build_default_vtk_renderer, build_default_vtk_widget
from src.window import build_default_window


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-g", "--grad", required=True)
    parser.add_argument("-p", "--params", required=True)
    add_axes_clip_args(parser)
    return parser.parse_args()


def read_params(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        rows = [line.split() for line in f if line and not line.startswith("#")]
    return [
        IsovalueParams(
            value=int(row[0]),
            gradient_range=tuple(map(float, row[1:3])),
            color=tuple(map(float, row[3:])),
        )
        for row in rows
    ]


class IsovalueParams(TypedDict):
    value: int
    gradient_range: tuple[float, float]
    color: tuple[float, float, float]


# Use GUI widgets to store the state of the application.
# pylint: disable=too-many-locals
def build_gui(
    isovalue_filename: str,
    gradient_filename: str,
    params_list: list[IsovalueParams],
    clips_default: list[int],
):
    def on_clip_changed():
        change_clip(vtk_widget, *(slider.value() for slider in clip_sliders))

    window, central, layout = build_default_window()

    vtk_widget, change_clip = build_vtk_widget(
        central,
        isovalue_filename,
        gradient_filename,
        params_list,
        clips_default,
    )
    layout.addWidget(vtk_widget, 0, 0, 1, -1)

    clip_sliders = build_axes_clip_sliders(layout, 1, clips_default, on_clip_changed)

    return window


# pylint: disable=too-many-locals too-many-arguments
def build_vtk_widget(
    parent: QObject,
    isovalue_filename: str,
    gradient_filename: str,
    params_list: list[IsovalueParams],
    axes_clips_default: list[int],
):
    def change_all_actor_clips(
        widget: QVTKRenderWindowInteractor, x: float, y: float, z: float
    ):
        for change_clip in change_clips_list:
            change_clip(widget, x, y, z)

    isovalue_reader = vtkXMLImageDataReader()
    isovalue_reader.SetFileName(isovalue_filename)

    gradient_reader = vtkXMLImageDataReader()
    gradient_reader.SetFileName(gradient_filename)

    actors: list[vtkActor] = []
    change_clips_list: list[
        Callable[[QVTKRenderWindowInteractor, float, float, float], None]
    ] = []
    for params in params_list:
        actor, change_clips = build_isosurface_actor(
            params,
            isovalue_reader,
            gradient_reader,
        )
        actors.append(actor)
        change_clips_list.append(change_clips)

    renderer = build_default_vtk_renderer(actors, [])

    widget = build_default_vtk_widget(parent, renderer)

    # Set to user defined value after we have the widget.
    change_all_actor_clips(widget, *axes_clips_default)

    # Enable depth peeling.
    widget.GetRenderWindow().SetAlphaBitPlanes(True)
    widget.GetRenderWindow().SetMultiSamples(0)
    renderer.SetUseDepthPeeling(True)
    renderer.SetMaximumNumberOfPeels(100)
    renderer.SetOcclusionRatio(0.0)

    return widget, change_all_actor_clips


def build_isosurface_actor(
    params: IsovalueParams,
    isovalue_reader: vtkXMLImageDataReader,
    gradient_reader: vtkXMLImageDataReader,
):
    contour_filter = vtkContourFilter()
    contour_filter.SetValue(0, params["value"])
    contour_filter.SetInputConnection(isovalue_reader.GetOutputPort())

    axes_clip_filter, change_axes_clips = get_axes_clip_filter()
    axes_clip_filter.SetInputConnection(contour_filter.GetOutputPort())

    probe_filter = vtkProbeFilter()
    probe_filter.SetInputConnection(axes_clip_filter.GetOutputPort())
    probe_filter.SetSourceConnection(gradient_reader.GetOutputPort())

    gradmin_clip_filter = vtkClipPolyData()
    gradmin_clip_filter.SetValue(params["gradient_range"][0])
    gradmin_clip_filter.SetInputConnection(probe_filter.GetOutputPort())

    gradmax_clip_filter = vtkClipPolyData()
    gradmax_clip_filter.SetValue(params["gradient_range"][1])
    gradmax_clip_filter.SetInsideOut(True)
    gradmax_clip_filter.SetInputConnection(gradmin_clip_filter.GetOutputPort())

    lut = vtkLookupTable()
    lut.SetNumberOfTableValues(1)
    lut.SetTableValue(0, *params["color"])
    lut.Build()

    mapper = vtkDataSetMapper()
    mapper.SetLookupTable(lut)
    mapper.SetInputConnection(gradmax_clip_filter.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)

    return actor, change_axes_clips


if __name__ == "__main__":
    import_for_rendering_core()
    args = parse_args()
    app = QApplication()
    gui = build_gui(
        args.input,
        args.grad,
        read_params(args.params),
        args.clip,
    )
    gui.show()
    sys.exit(app.exec())
