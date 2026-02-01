from io_footprints import load_footprints
from io_board import load_board
from grid import check_placement
from render_svg import render_svg

def main():
    footprints = load_footprints("footprints.yaml")
    grid, components = load_board("board.yaml", footprints)

    errors = check_placement(grid, components)

    for e in errors:
        print(e)

    render_svg(grid, components, errors)


if __name__ == "__main__":
    main()
