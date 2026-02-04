from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Coord:
    x: int
    y: int

    def add(self, other: "Coord") -> "Coord":
        return Coord(self.x + other.x, self.y + other.y)

    def rotate(self, rotation: int) -> "Coord":
        if not isinstance(rotation, int):
            raise TypeError("rotation must be int")
        if rotation == 0:
            return self
        if rotation == 90:
            return Coord(-self.y, self.x)
        if rotation == 180:
            return Coord(-self.x, -self.y)
        if rotation == 270:
            return Coord(self.y, -self.x)
        raise ValueError("rotation must be one of 0, 90, 180, 270")


@dataclass(frozen=True)
class Pin:
    name: str
    offset: Coord

@dataclass(frozen=True)
class Footprint:
    pins: list[Pin]

    def pins_at(self, origin: Coord, rotation: int) -> list[Coord]:
        return [
            origin.add(pin.offset.rotate(rotation))
            for pin in self.pins
        ]

@dataclass
class ComponentInstance:
    ref: str
    footprint: Footprint
    origin: Coord
    rotation: int  # 0, 90, 180, 270
    bbox: Optional[tuple[int, int, int, int]] = None  # (min_x, min_y, max_x, max_y)

    def placed_pins(self) -> list[Coord]:
        return self.footprint.pins_at(self.origin, self.rotation)


@dataclass
class Jumper:
    jid: str
    net: str
    a: Coord
    b: Coord
    color: str
    
def line_pins(
    start: Coord,
    axis: str,
    count: int,
    pitch: int = 1,
    start_index: int = 1,
) -> list[Pin]:
    pins: list[Pin] = []

    for i in range(count):
        if axis == "x":
            offset = Coord(start.x + i * pitch, start.y)
        elif axis == "y":
            offset = Coord(start.x, start.y + i * pitch)
        else:
            raise ValueError("axis must be 'x' or 'y'")

        name = str(start_index + i)
        pins.append(Pin(name, offset))

    return pins
