from io_footprints import load_footprints
from io_board import load_board
from grid import check_placement
from render_svg import render_svg

FOOTPRINTS_PATH = "footprints.yaml"
BOARD_PATH = "board.yaml"

def main():
    footprints = load_footprints(FOOTPRINTS_PATH)
    grid, components = load_board(BOARD_PATH, footprints)

    errors = check_placement(grid, components)
    for e in errors:
        print(e)

    render_svg(grid, components, errors)

if __name__ == "__main__":
    main()
