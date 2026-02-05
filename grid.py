from dataclasses import dataclass
from model import Coord, ComponentInstance, Jumper, Trace

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


def check_jumpers(grid: Grid, jumpers: list[Jumper]) -> list[str]:
    errors: list[str] = []
    for j in jumpers:
        for label, coord in (("a", j.a), ("b", j.b)):
            if not grid.contains(coord):
                errors.append(
                    f"jumper {j.jid}: endpoint {label} outside grid at {coord}"
                )
    return errors


def check_traces(grid: Grid, traces: list[Trace]) -> list[str]:
    errors: list[str] = []
    for t in traces:
        if len(t.points) < 2:
            errors.append(f"trace {t.tid}: must have at least 2 points")
            continue

        visited: set[Coord] = set()

        prev = t.points[0]
        if not grid.contains(prev):
            errors.append(f"trace {t.tid}: point outside grid at {prev}")
        visited.add(prev)

        for nxt in t.points[1:]:
            if not grid.contains(nxt):
                errors.append(f"trace {t.tid}: point outside grid at {nxt}")

            dx = nxt.x - prev.x
            dy = nxt.y - prev.y
            if dx == 0 and dy == 0:
                errors.append(f"trace {t.tid}: duplicate consecutive point {nxt}")
                prev = nxt
                continue
            if dx != 0 and dy != 0:
                errors.append(f"trace {t.tid}: non-orthogonal segment {prev}->{nxt}")
                prev = nxt
                continue

            step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
            step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
            steps = abs(dx) + abs(dy)

            x = prev.x
            y = prev.y
            for _ in range(steps):
                x += step_x
                y += step_y
                coord = Coord(x, y)
                if coord in visited:
                    errors.append(
                        f"trace {t.tid}: self-intersection at {coord}"
                    )
                visited.add(coord)

            prev = nxt

    return errors
