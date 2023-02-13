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
from vtkmodules.vtkFiltersCore import vtkClipPolyData, vtkContourFilter, vtkProbeFilter
from vtkmodules.vtkIOXML import vtkXMLImageDataReader
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import vtkActor, vtkDataSetMapper

from src.clipping import (
    add_axes_clip_args,
    build_axes_clip_sliders,
    get_axes_clip_filter,
)
from src.color_map import get_inferno16_color_map
from src.isovalue import get_isovalue_mid
from src.read_vti import read_vti
from src.vtk_side_effects import import_for_rendering_core
from src.vtk_widget import build_default_vtk_renderer, build_default_vtk_widget
from src.window import WINDOW_HEIGHT, WINDOW_WIDTH


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-g", "--grad", required=True)
    parser.add_argument("-v", "--value", type=int, required=True)
    add_axes_clip_args(parser)
    return parser.parse_args()


# Use GUI widgets to store the state of the application.
# pylint: disable=too-many-locals too-many-statements
def build_gui(
    isovalue_reader: vtkXMLImageDataReader,
    gradient_reader: vtkXMLImageDataReader,
    isovalue_default: int | None,
    axes_clip_default: list[int],
):
    def on_axes_clip_changed():
        change_axes_clip(vtk_widget, *(slider.value() for slider in axes_clip_sliders))

    def on_gradient_min_changed(value: int):
        change_gradmin(value)
        gradmin_label.setText(str(value))

    def on_gradient_max_changed(value: int):
        change_gradmax(value)
        gradmax_label.setText(str(value))

    window = QMainWindow()
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    central = QWidget()
    layout = QGridLayout()

    (
        vtk_widget,
        change_axes_clip,
        change_gradmin,
        change_gradmax,
    ) = build_vtk_widget(
        central, isovalue_reader, gradient_reader, isovalue_default, axes_clip_default
    )
    layout.addWidget(vtk_widget, 0, 0, 1, -1)

    grad_min: float
    grad_max: float
    grad_min, grad_max = gradient_reader.GetOutput().GetScalarRange()

    layout.addWidget(QLabel("gradmin"), 2, 0)
    gradmin_slider = QSlider(Qt.Orientation.Horizontal)
    gradmin_slider.setMinimum(int(grad_min))
    gradmin_slider.setMaximum(int(grad_max))
    gradmin_slider.setValue(int(grad_min))
    gradmin_slider.valueChanged.connect(on_gradient_min_changed)  # type: ignore
    layout.addWidget(gradmin_slider, 2, 1)
    gradmin_label = QLabel(str(int(grad_min)))
    layout.addWidget(gradmin_label, 2, 2)

    layout.addWidget(QLabel("gradmax"), 3, 0)
    gradmax_slider = QSlider(Qt.Orientation.Horizontal)
    gradmax_slider.setMinimum(int(grad_min))
    gradmax_slider.setMaximum(int(grad_max))
    gradmax_slider.setValue(int(grad_max))
    gradmax_slider.valueChanged.connect(on_gradient_max_changed)  # type: ignore
    layout.addWidget(gradmax_slider, 3, 1)
    gradmax_label = QLabel(str(int(grad_max)))
    layout.addWidget(gradmax_label, 3, 2)

    axes_clip_sliders = build_axes_clip_sliders(
        layout, 4, axes_clip_default, on_axes_clip_changed
    )

    central.setLayout(layout)
    window.setCentralWidget(central)
    return window


# pylint: disable=too-many-locals
def build_vtk_widget(
    parent: QObject,
    isovalue_reader: vtkXMLImageDataReader,
    gradient_reader: vtkXMLImageDataReader,
    isovalue_default: int | None,
    axes_clips_default: list[int],
):
    def change_isovalue(value: int):
        contour_filter.SetValue(contour_index, value)
        widget.GetRenderWindow().Render()

    def change_gradmin(value: int):
        gradmin_clip_filter.SetValue(value)
        widget.GetRenderWindow().Render()

    def change_gradmax(value: int):
        gradmax_clip_filter.SetValue(value)
        widget.GetRenderWindow().Render()

    isovalue_mid = get_isovalue_mid(isovalue_reader)

    contour_filter = vtkContourFilter()
    contour_index = 0

    # Force the filter to have initial value. If not, the filter will not
    # generate any output even if the value is changed.
    contour_filter.SetValue(contour_index, isovalue_mid)
    contour_filter.SetInputConnection(isovalue_reader.GetOutputPort())

    axes_clip_filter, change_axes_clips = get_axes_clip_filter()
    axes_clip_filter.SetInputConnection(contour_filter.GetOutputPort())

    probe_filter = vtkProbeFilter()
    probe_filter.SetInputConnection(axes_clip_filter.GetOutputPort())
    probe_filter.SetSourceConnection(gradient_reader.GetOutputPort())

    gradient_range: tuple[float, float] = gradient_reader.GetOutput().GetScalarRange()
    gradmin, gradmax = gradient_range

    gradmin_clip_filter = vtkClipPolyData()
    gradmin_clip_filter.SetValue(gradmin)
    gradmin_clip_filter.SetInputConnection(probe_filter.GetOutputPort())

    gradmax_clip_filter = vtkClipPolyData()
    gradmax_clip_filter.SetValue(gradmax)
    gradmax_clip_filter.SetInsideOut(True)
    gradmax_clip_filter.SetInputConnection(gradmin_clip_filter.GetOutputPort())

    mapper = vtkDataSetMapper()
    mapper.SetInputConnection(gradmax_clip_filter.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)

    scalar_bar = vtkScalarBarActor()
    ctf = get_inferno16_color_map(gradient_range)
    mapper.SetLookupTable(ctf)
    scalar_bar.SetLookupTable(ctf)

    renderer = build_default_vtk_renderer([actor], [scalar_bar])

    widget = build_default_vtk_widget(parent, renderer)

    # Set to user defined value if provided.
    change_isovalue(isovalue_default if isovalue_default else isovalue_mid)
    # Set to user defined value after we have the widget.
    change_axes_clips(widget, *axes_clips_default)

    return widget, change_axes_clips, change_gradmin, change_gradmax


if __name__ == "__main__":
    import_for_rendering_core()
    args = parse_args()
    app = QApplication()
    gui = build_gui(read_vti(args.input), read_vti(args.grad), args.value, args.clip)
    gui.show()
    sys.exit(app.exec())
