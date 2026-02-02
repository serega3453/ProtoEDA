import yaml
from typing import Mapping

from model import Coord, ComponentInstance, Footprint
from grid import Grid


def load_board(path: str, footprints: Mapping[str, Footprint]):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    grid_def = data.get("grid")
    if not grid_def:
        raise ValueError("board.yaml missing 'grid' section")

    grid = Grid(
        width=int(grid_def["width"]),
        height=int(grid_def["height"]),
    )

    components: list[ComponentInstance] = []

    for c in data.get("components", []):
        for key in ("ref", "footprint", "x", "y"):
            if key not in c:
                raise ValueError(f"Component missing required field '{key}'")

        fp_name = c["footprint"]
        if fp_name not in footprints:
            raise ValueError(f"Unknown footprint '{fp_name}'")

        bbox = None
        if "bbox" in c:
            b = c["bbox"]
            if len(b) != 4:
                raise ValueError(f"Component '{c['ref']}': bbox must have 4 elements")
            bbox = tuple(int(v) for v in b)

        comp = ComponentInstance(
            ref=c["ref"],
            footprint=footprints[fp_name],
            origin=Coord(int(c["x"]), int(c["y"])),
            rotation=c.get("rotation", 0),
            bbox=bbox,
        )

        components.append(comp)

    return grid, components
