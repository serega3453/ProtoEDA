from typing import Iterable
from model import Coord, ComponentInstance
from grid import Grid

OUTER_MARGIN = 40   # отступ в пикселях вокруг платы
INNER_MARGIN = 20   # отступ в пикселях до рамки
SCALE = 20      # размер клетки в пикселях
R_HOLE = 3      # радиус отверстия
R_PIN = 5       # радиус пина компонента
BOX_PAD = 1  # визуальный отступ рамки внутрь, в пикселях

def render_component_boxes(f, components):
    for comp in components:
        if comp.bbox is not None:
            min_x, min_y, max_x, max_y = comp.bbox
            # переносим bbox в мировые координаты
            ox = comp.origin.x
            oy = comp.origin.y

            min_x += ox
            max_x += ox
            min_y += oy
            max_y += oy
        else:
            pins = comp.placed_pins()
            if not pins:
                continue

            min_x = min(p.x for p in pins)
            max_x = max(p.x for p in pins)
            min_y = min(p.y for p in pins)
            max_y = max(p.y for p in pins)

        x = OUTER_MARGIN + INNER_MARGIN + min_x * SCALE + BOX_PAD
        y = OUTER_MARGIN + INNER_MARGIN + min_y * SCALE + BOX_PAD
        w = (max_x - min_x + 1) * SCALE - 2 * BOX_PAD
        h = (max_y - min_y + 1) * SCALE - 2 * BOX_PAD

        f.write(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="none" stroke="#888888" stroke-width="1" '
            f'stroke-dasharray="4,3"/>\n'
        )

def render_refs(f, components):
    for comp in components:
        tx = OUTER_MARGIN + INNER_MARGIN + comp.origin.x * SCALE + SCALE // 2
        ty = OUTER_MARGIN + INNER_MARGIN + comp.origin.y * SCALE - 6

        f.write(
            f'<text x="{tx}" y="{ty}" '
            f'fill="#ffffff" font-size="10" '
            f'text-anchor="middle" '
            f'font-family="monospace">{comp.ref}</text>\n'
        )

def render_svg(
    grid: Grid,
    components: list[ComponentInstance],
    errors: list[str],
    filename: str = "board.svg",
):
    # собираем координаты пинов с ошибками
    error_coords: set[Coord] = set()
    for e in errors:
        if "Coord(" in e:
            part = e.split("Coord(")[1].split(")")[0]
            x, y = part.replace("x=", "").replace("y=", "").split(", ")
            error_coords.add(Coord(int(x), int(y)))

    width_px  = grid.width * SCALE + 2 * (OUTER_MARGIN + INNER_MARGIN)
    height_px = grid.height * SCALE + 2 * (OUTER_MARGIN + INNER_MARGIN)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{width_px}" height="{height_px}">\n')

        # фон
        f.write(f'<rect width="100%" height="100%" fill="#1e1e1e"/>\n')

        # рамки
        board_x = OUTER_MARGIN
        board_y = OUTER_MARGIN
        board_w = grid.width * SCALE + 2 * INNER_MARGIN
        board_h = grid.height * SCALE + 2 * INNER_MARGIN

        f.write(
            f'<rect x="{board_x}" y="{board_y}" '
            f'width="{board_w}" height="{board_h}" '
            f'fill="none" stroke="#aaaaaa" stroke-width="2"/>\n'
        )

        # дырки платы
        for y in range(grid.height):
            for x in range(grid.width):
                cx = OUTER_MARGIN + INNER_MARGIN + x * SCALE + SCALE // 2
                cy = OUTER_MARGIN + INNER_MARGIN + y * SCALE + SCALE // 2
                f.write(
                    f'<circle cx="{cx}" cy="{cy}" r="{R_HOLE}" '
                    f'fill="#555"/>\n'
                )

        render_component_boxes(f, components)

        # пины компонентов
        for comp in components:
            for pin in comp.placed_pins():
                cx = OUTER_MARGIN + INNER_MARGIN + pin.x * SCALE + SCALE // 2
                cy = OUTER_MARGIN + INNER_MARGIN + pin.y * SCALE + SCALE // 2

                color = "#ff5555" if pin in error_coords else "#55ff55"

                f.write(
                    f'<circle cx="{cx}" cy="{cy}" r="{R_PIN}" '
                    f'fill="{color}" fill-opacity="0.8"/>\n'
                )
        render_refs(f, components)

        f.write("</svg>\n")
