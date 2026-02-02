from io_footprints import load_footprints
from io_board import load_board, save_board
from grid import check_placement
from render_svg import render_svg
from model import Coord


FOOTPRINTS_PATH = "footprints.yaml"
BOARD_PATH = "board.yaml"


def run():
    footprints = load_footprints(FOOTPRINTS_PATH)
    board_data, grid, components = load_board(BOARD_PATH, footprints)

    selected = None

    print("ProtoBoard CLI")
    print("Type 'help' for commands")

    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue

        parts = cmd.split()
        name = parts[0]

        if name == "help":
            print("Commands:")
            print("  list                 - list components")
            print("  select <ref>         - select component")
            print("  move <dx> <dy>       - move selected component")
            print("  render               - render board.svg")
            print("  quit                 - exit")

        elif name == "list":
            for c in components:
                mark = "*" if c is selected else " "
                print(f"{mark} {c.ref} @ {c.origin}")

        elif name == "select":
            if len(parts) != 2:
                print("usage: select <ref>")
                continue

            ref = parts[1]
            found = None
            for c in components:
                if c.ref == ref:
                    found = c
                    break

            if not found:
                print(f"component '{ref}' not found")
            else:
                selected = found
                print(f"selected {selected.ref}")

        elif name == "move":
            if selected is None:
                print("no component selected")
                continue
            if len(parts) != 3:
                print("usage: move <dx> <dy>")
                continue

            try:
                dx = int(parts[1])
                dy = int(parts[2])
            except ValueError:
                print("dx and dy must be integers")
                continue

            selected.origin = Coord(
                selected.origin.x + dx,
                selected.origin.y + dy,
            )
            print(f"{selected.ref} moved to {selected.origin}")

        elif name == "render":
            errors = check_placement(grid, components)
            for e in errors:
                print(e)
            render_svg(grid, components, errors)
            print("board.svg updated")

        elif name == "save":
            save_board(BOARD_PATH, board_data, components)
            print("board.yaml saved")

        elif name in ("quit", "exit"):
            break

        else:
            print(f"unknown command '{name}' (type 'help')")

    print("bye")
