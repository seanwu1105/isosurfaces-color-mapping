import argparse
from typing import Callable, TypedDict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QSlider
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkCommonDataModel import vtkPlanes
from vtkmodules.vtkFiltersCore import vtkClipPolyData


class AxesClipConfig(TypedDict):
    min: int
    max: int


AXES_CLIP_CONFIG: dict[str, AxesClipConfig] = {
    "X": {
        "min": 1,
        "max": 250,
    },
    "Y": {
        "min": 1,
        "max": 250,
    },
    "Z": {
        "min": 1,
        "max": 270,
    },
}

AXES_CLIP_MIN = [clip["min"] for clip in AXES_CLIP_CONFIG.values()]
AXES_CLIP_MAX = [clip["max"] for clip in AXES_CLIP_CONFIG.values()]


def add_axes_clip_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--clip",
        nargs=3,
        metavar=("X", "Y", "Z"),
        type=int,
        default=AXES_CLIP_MAX,
        help="Set the axes clip values",
    )


def build_axes_clip_sliders(
    layout: QGridLayout,
    start_row: int,
    clips_default: list[int],
    on_clip_changed: Callable[[], None],
):
    clip_widgets = {
        f"Clip {name}": (values["min"], values["max"], clips_default[i])
        for i, (name, values) in enumerate(AXES_CLIP_CONFIG.items())
    }
    clip_sliders: list[QSlider] = []
    for i, (name, (min_value, max_value, default_value)) in enumerate(
        clip_widgets.items(), start=start_row
    ):
        clip_sliders.append(
            build_axes_clip_row_widgets(
                layout,
                i,
                name,
                min_value,
                max_value,
                default_value,
                on_clip_changed,
            )
        )

    return clip_sliders


def get_axes_clip_filter():
    def change_axes_clips(
        widget: QVTKRenderWindowInteractor, x: float, y: float, z: float
    ):
        clip_planes.SetBounds(
            AXES_CLIP_MIN[0] - 1,
            x,
            AXES_CLIP_MIN[1] - 1,
            y,
            AXES_CLIP_MIN[2] - 1,
            z,
        )
        widget.GetRenderWindow().Render()

    clip_planes = vtkPlanes()
    clip_planes.SetBounds(
        AXES_CLIP_MIN[0] - 1,
        AXES_CLIP_MAX[0],
        AXES_CLIP_MIN[1] - 1,
        AXES_CLIP_MAX[1],
        AXES_CLIP_MIN[2] - 1,
        AXES_CLIP_MAX[2],
    )

    clip_filter = vtkClipPolyData()
    clip_filter.SetClipFunction(clip_planes)
    clip_filter.SetInsideOut(True)
    clip_filter.SetGenerateClipScalars(False)

    return clip_filter, change_axes_clips


# pylint: disable=too-many-arguments
def build_axes_clip_row_widgets(
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
