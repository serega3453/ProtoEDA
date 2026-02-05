import random
import yaml
from typing import Mapping

from model import Coord, ComponentInstance, Footprint, Jumper, Trace
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

    jumpers: list[Jumper] = []
    for j in board_data.get("jumpers", []):
        for key in ("id", "net", "a", "b"):
            if key not in j:
                raise ValueError(f"Jumper missing required field '{key}'")
        a = j["a"]
        b = j["b"]
        if len(a) != 2 or len(b) != 2:
            raise ValueError(f"Jumper '{j['id']}': a/b must be 2-element lists")
        jumper = Jumper(
            jid=str(j["id"]),
            net=str(j["net"]),
            a=Coord(int(a[0]), int(a[1])),
            b=Coord(int(b[0]), int(b[1])),
            color=str(j.get("color") or ""),
        )
        jumpers.append(jumper)

    traces: list[Trace] = []
    for t in board_data.get("traces", []):
        for key in ("id", "net", "points"):
            if key not in t:
                raise ValueError(f"Trace missing required field '{key}'")
        points = t["points"]
        if not isinstance(points, list) or len(points) < 2:
            raise ValueError(f"Trace '{t['id']}': points must be list of 2+ coords")
        coords: list[Coord] = []
        for p in points:
            if len(p) != 2:
                raise ValueError(f"Trace '{t['id']}': point must have 2 elements")
            coords.append(Coord(int(p[0]), int(p[1])))
        traces.append(Trace(tid=str(t["id"]), net=str(t["net"]), points=coords))

    # ВАЖНО: возвращаем board_data тоже
    return board_data, grid, components, jumpers, traces


def save_board(
    path: str,
    board_data: dict,
    components: list[ComponentInstance],
    jumpers: list[Jumper],
    traces: list[Trace],
):
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

    board_data["jumpers"] = []
    for j in jumpers:
        color = j.color
        if not color:
            # Assign once on save to avoid re-randomizing across runs.
            r = random.randint(64, 255)
            g = random.randint(64, 255)
            b = random.randint(64, 255)
            color = f"#{r:02x}{g:02x}{b:02x}"
            j.color = color
        board_data["jumpers"].append(
            {
                "id": j.jid,
                "net": j.net,
                "a": [j.a.x, j.a.y],
                "b": [j.b.x, j.b.y],
                "color": color,
            }
        )

    board_data["traces"] = [
        {
            "id": t.tid,
            "net": t.net,
            "points": [[p.x, p.y] for p in t.points],
        }
        for t in traces
    ]

    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(board_data, f, sort_keys=False)
