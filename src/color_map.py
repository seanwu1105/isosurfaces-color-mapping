from typing import TypedDict


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
