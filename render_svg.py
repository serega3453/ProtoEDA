from model import Coord, ComponentInstance, Jumper
from grid import Grid

# ---------- config ----------

OUTER_MARGIN = 40   # отступ в пикселях вокруг платы
INNER_MARGIN = 20   # отступ в пикселях до рамки
SCALE = 20          # размер клетки в пикселях
R_HOLE = 3          # радиус отверстия
R_PIN = 5           # радиус пина компонента
BOX_PAD = 1         # визуальный отступ рамки внутрь, в пикселях

COLOR_BG = "#1e1e1e"
COLOR_BOARD = "#aaaaaa"
COLOR_HOLE = "#555"
COLOR_PIN_OK = "#55ff55"
COLOR_PIN_ERR = "#ff5555"
COLOR_BOX = "#888888"
COLOR_JUMPER = "#ffaa00"
JUMPER_WIDTH = 3
COLOR_AXIS_TEXT = "#cccccc"
AXIS_FONT_SIZE = 10
AXIS_TICK = 6


# ---------- helpers ----------

def _flip_coord(coord: Coord, grid: Grid) -> Coord:
    """Mirror X across center of the grid (0..width-1)."""
    return Coord(grid.width - 1 - coord.x, coord.y)


def grid_to_svg(coord: Coord, grid: Grid, flip: bool = False) -> tuple[int, int]:
    c = _flip_coord(coord, grid) if flip else coord
    x = OUTER_MARGIN + INNER_MARGIN + c.x * SCALE + SCALE // 2
    y = OUTER_MARGIN + INNER_MARGIN + c.y * SCALE + SCALE // 2
    return x, y


def grid_cell_top_left(coord: Coord, grid: Grid, flip: bool = False) -> tuple[int, int]:
    c = _flip_coord(coord, grid) if flip else coord
    x = OUTER_MARGIN + INNER_MARGIN + c.x * SCALE
    y = OUTER_MARGIN + INNER_MARGIN + c.y * SCALE
    return x, y


def extract_error_coords(errors: list[str]) -> set[Coord]:
    coords: set[Coord] = set()
    for e in errors:
        if "Coord(" not in e:
            continue
        part = e.split("Coord(")[1].split(")")[0]
        x, y = part.replace("x=", "").replace("y=", "").split(", ")
        coords.add(Coord(int(x), int(y)))
    return coords


def component_bbox(comp: ComponentInstance) -> tuple[int, int, int, int] | None:
    if comp.bbox is not None:
        min_x, min_y, max_x, max_y = comp.bbox
        return (
            min_x + comp.origin.x,
            min_y + comp.origin.y,
            max_x + comp.origin.x,
            max_y + comp.origin.y,
        )

    pins = comp.placed_pins()
    if not pins:
        return None

    return (
        min(p.x for p in pins),
        min(p.y for p in pins),
        max(p.x for p in pins),
        max(p.y for p in pins),
    )


def view_bbox(bbox: tuple[int, int, int, int], grid: Grid, flip: bool) -> tuple[int, int, int, int]:
    if not flip:
        return bbox
    min_x, min_y, max_x, max_y = bbox
    return (
        grid.width - 1 - max_x,
        min_y,
        grid.width - 1 - min_x,
        max_y,
    )


def bbox_to_svg_rect(bbox: tuple[int, int, int, int], grid: Grid, flip: bool) -> tuple[int, int, int, int]:
    min_x, min_y, max_x, max_y = view_bbox(bbox, grid, flip)
    # view_bbox already mirrored if needed; avoid double-flip in pixel mapping
    base_x, base_y = grid_cell_top_left(Coord(min_x, min_y), grid, False)
    x = base_x + BOX_PAD
    y = base_y + BOX_PAD
    w = (max_x - min_x + 1) * SCALE - 2 * BOX_PAD
    h = (max_y - min_y + 1) * SCALE - 2 * BOX_PAD
    return x, y, w, h


# ---------- render parts ----------

def render_background(f, width_px: int, height_px: int):
    f.write(
        f'<rect width="{width_px}" height="{height_px}" fill="{COLOR_BG}"/>\n'
    )


def render_board_frame(f, grid: Grid):
    board_x = OUTER_MARGIN
    board_y = OUTER_MARGIN
    board_w = grid.width * SCALE + 2 * INNER_MARGIN
    board_h = grid.height * SCALE + 2 * INNER_MARGIN

    f.write(
        f'<rect x="{board_x}" y="{board_y}" '
        f'width="{board_w}" height="{board_h}" '
        f'fill="none" stroke="{COLOR_BOARD}" stroke-width="2"/>\n'
    )


def render_axes(f, grid: Grid, flip: bool):
    board_x = OUTER_MARGIN
    board_y = OUTER_MARGIN
    board_w = grid.width * SCALE + 2 * INNER_MARGIN
    board_h = grid.height * SCALE + 2 * INNER_MARGIN

    # Column labels (top)
    for x in range(grid.width):
        cx, _ = grid_to_svg(Coord(x, 0), grid, flip)
        f.write(
            f'<line x1="{cx}" y1="{board_y}" '
            f'x2="{cx}" y2="{board_y - AXIS_TICK}" '
            f'stroke="{COLOR_AXIS_TEXT}" stroke-width="1"/>\n'
        )
        f.write(
            f'<text x="{cx}" y="{board_y - AXIS_TICK - 2}" '
            f'fill="{COLOR_AXIS_TEXT}" font-size="{AXIS_FONT_SIZE}" '
            f'text-anchor="middle" font-family="monospace">{x}</text>\n'
        )

    # Row labels (left)
    for y in range(grid.height):
        _, cy = grid_to_svg(Coord(0, y), grid, flip)
        f.write(
            f'<line x1="{board_x}" y1="{cy}" '
            f'x2="{board_x - AXIS_TICK}" y2="{cy}" '
            f'stroke="{COLOR_AXIS_TEXT}" stroke-width="1"/>\n'
        )
        f.write(
            f'<text x="{board_x - AXIS_TICK - 2}" y="{cy + 3}" '
            f'fill="{COLOR_AXIS_TEXT}" font-size="{AXIS_FONT_SIZE}" '
            f'text-anchor="end" font-family="monospace">{y}</text>\n'
        )


def render_board_holes(f, grid: Grid, flip: bool):
    for y in range(grid.height):
        for x in range(grid.width):
            cx, cy = grid_to_svg(Coord(x, y), grid, flip)
            f.write(
                f'<circle cx="{cx}" cy="{cy}" r="{R_HOLE}" '
                f'fill="{COLOR_HOLE}"/>\n'
            )


def render_component_boxes(f, components: list[ComponentInstance], grid: Grid, flip: bool):
    for comp in components:
        bbox = component_bbox(comp)
        if bbox is None:
            continue
        x, y, w, h = bbox_to_svg_rect(bbox, grid, flip)

        f.write(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="none" stroke="{COLOR_BOX}" stroke-width="1" '
            f'stroke-dasharray="4,3"/>\n'
        )


def render_pins(f, components: list[ComponentInstance], grid: Grid, flip: bool, error_coords: set[Coord]):
    for comp in components:
        for pin in comp.placed_pins():
            cx, cy = grid_to_svg(pin, grid, flip)
            color = COLOR_PIN_ERR if pin in error_coords else COLOR_PIN_OK
            f.write(
                f'<circle cx="{cx}" cy="{cy}" r="{R_PIN}" '
                f'fill="{color}" fill-opacity="0.8"/>\n'
            )


def render_jumpers(f, jumpers: list[Jumper], grid: Grid, flip: bool):
    for j in jumpers:
        ax, ay = grid_to_svg(j.a, grid, flip)
        bx, by = grid_to_svg(j.b, grid, flip)
        color = j.color or COLOR_JUMPER
        f.write(
            f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" '
            f'stroke="{color}" stroke-width="{JUMPER_WIDTH}" '
            f'stroke-linecap="round"/>\n'
        )


def render_refs(f, components: list[ComponentInstance], grid: Grid, flip: bool):
    for comp in components:
        tx, ty = grid_to_svg(comp.origin, grid, flip)
        ty -= 6

        f.write(
            f'<text x="{tx}" y="{ty}" '
            f'fill="#ffffff" font-size="10" '
            f'text-anchor="middle" '
            f'font-family="monospace">{comp.ref}</text>\n'
        )


# ---------- main render ----------

def render_svg(
    grid: Grid,
    components: list[ComponentInstance],
    errors: list[str],
    jumpers: list[Jumper] | None = None,
    filename: str = "board.svg",
    flip: bool = False,
):
    error_coords = extract_error_coords(errors)

    width_px  = grid.width * SCALE + 2 * (OUTER_MARGIN + INNER_MARGIN)
    height_px = grid.height * SCALE + 2 * (OUTER_MARGIN + INNER_MARGIN)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width_px}" height="{height_px}">\n'
        )

        render_background(f, width_px, height_px)
        render_board_frame(f, grid)
        render_axes(f, grid, flip)
        render_board_holes(f, grid, flip)

        render_component_boxes(f, components, grid, flip)
        if jumpers:
            render_jumpers(f, jumpers, grid, flip)
        render_pins(f, components, grid, flip, error_coords)
        render_refs(f, components, grid, flip)

        f.write("</svg>\n")
