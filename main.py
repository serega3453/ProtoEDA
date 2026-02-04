from io_footprints import load_footprints
from io_board import load_board
from grid import check_placement, check_jumpers
from render_svg import render_svg
from cli import run

FOOTPRINTS_PATH = "footprints.yaml"
BOARD_PATH = "board.yaml"

def main():
    footprints = load_footprints(FOOTPRINTS_PATH)
    _, grid, components, jumpers = load_board(BOARD_PATH, footprints)

    errors = check_placement(grid, components)
    errors.extend(check_jumpers(grid, jumpers))
    for e in errors:
        print(e)

    render_svg(grid, components, errors, jumpers)

if __name__ == "__main__":
    run()
