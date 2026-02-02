import yaml
from typing import Mapping

from model import Coord, ComponentInstance, Footprint
from grid import Grid


def load_board(path: str, footprints: Mapping[str, Footprint]):
    with open(path, "r", encoding="utf-8") as f:
        board_data = yaml.safe_load(f)

    grid_def = board_data.get("grid")
    if not grid_def:
        raise ValueError("board.yaml missing 'grid' section")

    grid = Grid(
        width=int(grid_def["width"]),
        height=int(grid_def["height"]),
    )

    components: list[ComponentInstance] = []

    for c in board_data.get("components", []):
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
            rotation=int(c.get("rotation", 0)),
            bbox=bbox,
        )

        components.append(comp)

    # ВАЖНО: возвращаем board_data тоже
    return board_data, grid, components


def save_board(path: str, board_data: dict, components: list[ComponentInstance]):
    comps_by_ref = {c.ref: c for c in components}

    for c in board_data.get("components", []):
        ref = c["ref"]
        if ref not in comps_by_ref:
            continue

        inst = comps_by_ref[ref]
        c["x"] = inst.origin.x
        c["y"] = inst.origin.y
        c["rotation"] = inst.rotation

        if inst.bbox is not None:
            c["bbox"] = list(inst.bbox)
        else:
            c.pop("bbox", None)

    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(board_data, f, sort_keys=False)
