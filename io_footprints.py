import yaml

from model import Footprint, Coord, line_pins


def load_footprints(path: str) -> dict[str, Footprint]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    footprints: dict[str, Footprint] = {}

    for name, fpdef in data.items():
        pins = []

        lines = fpdef.get("lines")
        if not lines:
            raise ValueError(f"Footprint '{name}' has no lines")

        for line in lines:
            try:
                start = Coord(int(line["start"][0]), int(line["start"][1]))
                axis = line["axis"]
                count = int(line["count"])
                pitch = int(line.get("pitch", 1))
                start_index = int(line.get("start_index", 1))
            except KeyError as e:
                raise ValueError(f"Footprint '{name}' missing field {e}")

            if axis not in ("x", "y"):
                raise ValueError(f"Footprint '{name}': invalid axis '{axis}'")
            if count <= 0:
                raise ValueError(f"Footprint '{name}': count must be > 0")

            pins.extend(
                line_pins(
                    start=start,
                    axis=axis,
                    count=count,
                    pitch=pitch,
                    start_index=start_index,
                )
            )

        footprints[name] = Footprint(pins=pins)

    return footprints
