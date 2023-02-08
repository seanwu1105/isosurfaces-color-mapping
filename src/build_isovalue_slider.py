from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QSlider
from vtkmodules.vtkIOXML import vtkXMLImageDataReader


def build_isovalue_slider(
    layout: QGridLayout,
    row: int,
    reader: vtkXMLImageDataReader,
    default_value: int,
    on_changed: Callable[[int], None],
):
    def on_slide_value_changed(value: int):
        isovalue_label.setText(str(value))
        on_changed(value)

    isovalue_min: float
    isovalue_max: float
    isovalue_min, isovalue_max = reader.GetOutput().GetScalarRange()
    layout.addWidget(QLabel("Isovalue"), row, 0)
    isovalue_slider = QSlider(Qt.Orientation.Horizontal)
    isovalue_slider.setMinimum(int(isovalue_min))
    isovalue_slider.setMaximum(max(int(isovalue_max), default_value))
    isovalue_slider.setValue(default_value)
    isovalue_slider.valueChanged.connect(on_slide_value_changed)  # type: ignore
    layout.addWidget(isovalue_slider, row, 1)
    isovalue_label = QLabel(str(default_value))
    layout.addWidget(isovalue_label, row, 2)
