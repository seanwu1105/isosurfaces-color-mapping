import argparse

from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOXML import vtkXMLImageDataReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from src.vtk_side_effects import import_for_rendering_core


def main(
    data_filename: str, value: float, clip: list[float]
):  # pylint: disable=unused-argument
    reader = vtkXMLImageDataReader()
    reader.SetFileName(data_filename)

    mapper = vtkDataSetMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)

    renderer = vtkRenderer()
    renderer.AddActor(actor)
    colors = vtkNamedColors()
    renderer.SetBackground(colors.GetColor3d("Gray"))  # type: ignore

    window = vtkRenderWindow()
    window.AddRenderer(renderer)
    window.SetSize(640, 480)

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)
    interactor.Initialize()
    interactor.Start()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input")
    parser.add_argument("--value", type=float, default=0.0)
    parser.add_argument("--clip", nargs=3, type=float, default=[0.0, 0.0, 0.0])
    return parser.parse_args()


if __name__ == "__main__":
    import_for_rendering_core()

    args = parse_args()

    main(args.input, args.value, args.clip)
