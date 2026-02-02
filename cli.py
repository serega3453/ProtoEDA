from dataclasses import dataclass

from io_footprints import load_footprints
from io_board import load_board, save_board
from grid import check_placement
from render_svg import render_svg
from model import Coord, ComponentInstance


FOOTPRINTS_PATH = "footprints.yaml"
BOARD_PATH = "board.yaml"

@dataclass
class CLIState:
    board_data: dict
    grid: object
    components: list[ComponentInstance]
    selected: ComponentInstance | None = None


def cmd_help(state: CLIState, parts: list[str]) -> bool:
    print("Commands:")
    print("  list                 - list components")
    print("  select <ref>         - select component")
    print("  move <dx> <dy>       - move selected component")
    print("  render               - render board.svg")
    print("  save                 - save board.yaml")
    print("  quit                 - exit")
    return True


def cmd_list(state: CLIState, parts: list[str]) -> bool:
    for c in state.components:
        mark = "*" if c is state.selected else " "
        print(f"{mark} {c.ref} @ {c.origin}")
    return True


def cmd_select(state: CLIState, parts: list[str]) -> bool:
    if len(parts) != 2:
        print("usage: select <ref>")
        return True

    ref = parts[1]
    found = None
    for c in state.components:
        if c.ref == ref:
            found = c
            break

    if not found:
        print(f"component '{ref}' not found")
    else:
        state.selected = found
        print(f"selected {state.selected.ref}")
    return True


def cmd_move(state: CLIState, parts: list[str]) -> bool:
    if state.selected is None:
        print("no component selected")
        return True
    if len(parts) != 3:
        print("usage: move <dx> <dy>")
        return True

    try:
        dx = int(parts[1])
        dy = int(parts[2])
    except ValueError:
        print("dx and dy must be integers")
        return True

    state.selected.origin = Coord(
        state.selected.origin.x + dx,
        state.selected.origin.y + dy,
    )
    print(f"{state.selected.ref} moved to {state.selected.origin}")
    return True


def cmd_render(state: CLIState, parts: list[str]) -> bool:
    errors = check_placement(state.grid, state.components)
    for e in errors:
        print(e)
    render_svg(state.grid, state.components, errors)
    print("board.svg updated")
    return True


def cmd_save(state: CLIState, parts: list[str]) -> bool:
    save_board(BOARD_PATH, state.board_data, state.components)
    print("board.yaml saved")
    return True


def cmd_quit(state: CLIState, parts: list[str]) -> bool:
    return False


def run():
    footprints = load_footprints(FOOTPRINTS_PATH)
    board_data, grid, components = load_board(BOARD_PATH, footprints)
    state = CLIState(board_data=board_data, grid=grid, components=components)

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
            cmd_help(state, parts)
        elif name == "list":
            cmd_list(state, parts)
        elif name == "select":
            cmd_select(state, parts)
        elif name == "move":
            cmd_move(state, parts)
            cmd_render(state, parts)
        elif name == "render":
            cmd_render(state, parts)
        elif name == "save":
            cmd_save(state, parts)
        elif name in ("quit", "exit"):
            cmd_quit(state, parts)
            print("bye")
            return
        else:
            print(f"unknown command '{name}' (type 'help')")

    print("bye")
