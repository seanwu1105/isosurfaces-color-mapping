from typing import Callable, TypedDict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QSlider
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkCommonDataModel import vtkPlanes
from vtkmodules.vtkFiltersCore import vtkClipPolyData


class ClipConfig(TypedDict):
    min: int
    max: int


CLIPS_CONFIG: dict[str, ClipConfig] = {
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

CLIPS_MIN = [clip["min"] for clip in CLIPS_CONFIG.values()]
CLIPS_MAX = [clip["max"] for clip in CLIPS_CONFIG.values()]


def build_clip_sliders(
    layout: QGridLayout,
    clips_default: list[int],
    on_clip_changed: Callable[[], None],
):
    clip_widgets = {
        f"Clip {name}": (values["min"], values["max"], clips_default[i])
        for i, (name, values) in enumerate(CLIPS_CONFIG.items())
    }
    clip_sliders: list[QSlider] = []
    for i, (name, (min_value, max_value, default_value)) in enumerate(
        clip_widgets.items(), start=1
    ):
        clip_sliders.append(
            build_clip_row_widgets(
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


def get_clip_filter(clips_default: list[int]):
    def change_clips(widget: QVTKRenderWindowInteractor, x: float, y: float, z: float):
        clip_planes.SetBounds(
            CLIPS_MIN[0] - 1,
            x,
            CLIPS_MIN[1] - 1,
            y,
            CLIPS_MIN[2] - 1,
            z,
        )
        widget.GetRenderWindow().Render()

    clip_planes = vtkPlanes()
    clip_planes.SetBounds(
        CLIPS_MIN[0] - 1,
        clips_default[0],
        CLIPS_MIN[1] - 1,
        clips_default[1],
        CLIPS_MIN[2] - 1,
        clips_default[2],
    )

    clip_filter = vtkClipPolyData()
    clip_filter.SetClipFunction(clip_planes)
    clip_filter.SetInsideOut(True)
    return clip_filter, change_clips


# pylint: disable=too-many-arguments
def build_clip_row_widgets(
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
