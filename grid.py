from dataclasses import dataclass
from model import Coord, ComponentInstance

@dataclass(frozen=True)
class Grid:
    width: int
    height: int

    def contains(self, coord: Coord) -> bool:
        return (
            0 <= coord.x < self.width and
            0 <= coord.y < self.height
        )
    
def check_placement(grid: Grid, components: list[ComponentInstance]) -> list[str]:
    errors: list[str] = []
    occupied: dict[Coord, str] = {}

    for comp in components:
        for pin in comp.placed_pins():
            if not grid.contains(pin):
                errors.append(
                    f"{comp.ref}: pin outside grid at {pin}"
                )
                continue

            if pin in occupied:
                errors.append(
                    f"conflict at {pin}: {comp.ref} overlaps {occupied[pin]}"
                )
            else:
                occupied[pin] = comp.ref

    return errors