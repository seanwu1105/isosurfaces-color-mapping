from typing import TypedDict

from vtkmodules.vtkRenderingCore import vtkColorTransferFunction


class IsovalueColorMapping(TypedDict):
    value: int
    color: tuple[float, float, float]


COLOR_MAP_ISOVALUE_DEFAULT: dict[str, IsovalueColorMapping] = {
    "skin": {
        "value": 400,
        "color": (229 / 255, 181 / 255, 161 / 255),
    },
    "skin_interval": {
        "value": 450,
        "color": (229 / 255, 181 / 255, 161 / 255),
    },
    "muscle": {
        "value": 1010,
        "color": (171 / 255, 54 / 255, 54 / 255),
    },
    "muscle_interval": {
        "value": 1060,
        "color": (171 / 255, 54 / 255, 54 / 255),
    },
    "bone": {
        "value": 1135,
        "color": (229 / 255, 229 / 255, 229 / 255),
    },
    "bone_interval": {
        "value": 1185,
        "color": (229 / 255, 229 / 255, 229 / 255),
    },
}


def get_inferno16_color_map(scale_range: tuple[float, float]):
    colors = (
        (0.001462, 0.000466, 0.013866),
        (0.046915, 0.030324, 0.150164),
        (0.142378, 0.046242, 0.308553),
        (0.258234, 0.038571, 0.406485),
        (0.366529, 0.071579, 0.431994),
        (0.472328, 0.110547, 0.428334),
        (0.578304, 0.148039, 0.404411),
        (0.682656, 0.189501, 0.360757),
        (0.780517, 0.243327, 0.299523),
        (0.865006, 0.316822, 0.226055),
        (0.929644, 0.411479, 0.145367),
        (0.970919, 0.522853, 0.058367),
        (0.987622, 0.64532, 0.039886),
        (0.978806, 0.774545, 0.176037),
        (0.950018, 0.903409, 0.380271),
        (0.988362, 0.998364, 0.644924),
    )
    ctf = vtkColorTransferFunction()
    for i, color in enumerate(colors):
        ctf.AddRGBPoint(
            scale_range[0] + i * (scale_range[1] - scale_range[0]) / (len(colors) - 1),
            *color
        )

    return ctf
