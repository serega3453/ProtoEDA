import yaml

from model import Footprint, Pin, Coord, line_pins

def load_footprints(path: str) -> dict[str, Footprint]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    footprints: dict[str, Footprint] = {}

    for name, fpdef in data.items():
        pins: list[Pin] = []

        lines = fpdef.get("lines", [])
        if not lines:
            raise ValueError(f"Footprint '{name}' has no lines")

        for line in lines:
            try:
                start = Coord(*line["start"])
                axis = line["axis"]
                count = line["count"]
                pitch = line.get("pitch", 1)
                start_index = line.get("start_index", 1)
            except KeyError as e:
                raise ValueError(
                    f"Footprint '{name}' missing field {e}"
                )

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
