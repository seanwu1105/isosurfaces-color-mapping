from PySide6.QtCore import QObject
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkRenderingCore import vtkActor, vtkActor2D, vtkRenderer


def build_default_vtk_renderer(actors: list[vtkActor], actor_2d: list[vtkActor2D]):
    renderer = vtkRenderer()
    for actor in actors:
        renderer.AddActor(actor)
    for actor in actor_2d:
        renderer.AddActor2D(actor)
    colors = vtkNamedColors()
    renderer.SetBackground(colors.GetColor3d("Gray"))  # type: ignore

    return renderer


def build_default_vtk_widget(parent: QObject, renderer: vtkRenderer):
    widget = QVTKRenderWindowInteractor(parent)
    widget.GetRenderWindow().AddRenderer(renderer)
    widget.GetRenderWindow().GetInteractor().Initialize()

    return widget
