import yaml

from model import Coord, ComponentInstance
from grid import Grid

def load_board(path: str, footprints: dict):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # grid
    grid_def = data.get("grid")
    if not grid_def:
        raise ValueError("board.yaml missing 'grid' section")

    grid = Grid(
        width=grid_def["width"],
        height=grid_def["height"],
    )

    # components
    components = []

    for c in data.get("components", []):
        try:
            fp_name = c["footprint"]
            footprint = footprints[fp_name]
        except KeyError:
            raise ValueError(f"Unknown footprint '{c.get('footprint')}'")

        bbox = None
        if "bbox" in c:
            b = c["bbox"]
            if len(b) != 4:
                raise ValueError(f"Component '{c.get('ref')}': bbox must have 4 elements")
            bbox = tuple(int(v) for v in b)

        comp = ComponentInstance(
            ref=c["ref"],
            footprint=footprint,
            origin=Coord(c["x"], c["y"]),
            rotation=c.get("rotation", 0),
            bbox=bbox,
        )

        components.append(comp)

    return grid, components
