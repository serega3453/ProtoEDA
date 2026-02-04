from dataclasses import dataclass
import random

from io_footprints import load_footprints
from io_board import load_board, save_board
from grid import check_placement, check_jumpers
from render_svg import render_svg
from model import Coord, ComponentInstance, Jumper


FOOTPRINTS_PATH = "footprints.yaml"
BOARD_PATH = "board.yaml"

@dataclass
class CLIState:
    board_data: dict
    grid: object
    components: list[ComponentInstance]
    jumpers: list[Jumper]
    selected: ComponentInstance | None = None


def cmd_help(state: CLIState, parts: list[str]) -> bool:
    print("Commands:")
    print("  list                 - list components")
    print("  select <ref>         - select component")
    print("  move <dx> <dy>       - move selected component")
    print("  render               - render board.svg")
    print("  save                 - save board.yaml")
    print("  jumper-list          - list jumpers")
    print("  jumper-add <id> <net> <x1> <y1> <x2> <y2> [color]")
    print("  jumper-del <id>")
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
    errors.extend(check_jumpers(state.grid, state.jumpers))
    for e in errors:
        print(e)
    render_svg(state.grid, state.components, errors, state.jumpers)
    print("board.svg updated")
    return True


def cmd_save(state: CLIState, parts: list[str]) -> bool:
    save_board(BOARD_PATH, state.board_data, state.components, state.jumpers)
    print("board.yaml saved")
    return True


def cmd_jumper_list(state: CLIState, parts: list[str]) -> bool:
    if not state.jumpers:
        print("no jumpers")
        return True
    for j in state.jumpers:
        print(f"{j.jid} {j.net}: {j.a} -> {j.b}")
    return True


def cmd_jumper_add(state: CLIState, parts: list[str]) -> bool:
    if len(parts) not in (7, 8):
        print("usage: jumper-add <id> <net> <x1> <y1> <x2> <y2> [color]")
        return True
    jid = parts[1]
    if any(j.jid == jid for j in state.jumpers):
        print(f"jumper '{jid}' already exists")
        return True
    net = parts[2]
    try:
        x1 = int(parts[3])
        y1 = int(parts[4])
        x2 = int(parts[5])
        y2 = int(parts[6])
    except ValueError:
        print("x/y must be integers")
        return True

    if len(parts) == 8:
        color = parts[7]
    else:
        r = random.randint(64, 255)
        g = random.randint(64, 255)
        b = random.randint(64, 255)
        color = f"#{r:02x}{g:02x}{b:02x}"
    jumper = Jumper(jid=jid, net=net, a=Coord(x1, y1), b=Coord(x2, y2), color=color)
    state.jumpers.append(jumper)
    print(f"jumper {jid} added")
    return True


def cmd_jumper_del(state: CLIState, parts: list[str]) -> bool:
    if len(parts) != 2:
        print("usage: jumper-del <id>")
        return True
    jid = parts[1]
    before = len(state.jumpers)
    state.jumpers = [j for j in state.jumpers if j.jid != jid]
    if len(state.jumpers) == before:
        print(f"jumper '{jid}' not found")
    else:
        print(f"jumper {jid} deleted")
    return True


def cmd_quit(state: CLIState, parts: list[str]) -> bool:
    return False


def run():
    footprints = load_footprints(FOOTPRINTS_PATH)
    board_data, grid, components, jumpers = load_board(BOARD_PATH, footprints)
    state = CLIState(
        board_data=board_data,
        grid=grid,
        components=components,
        jumpers=jumpers,
    )

    print("ProtoBoard CLI")
    print("Type 'help' for commands")
    print("Commands:")
    print("  list                 - list components")
    print("  select <ref>         - select component")
    print("  move <dx> <dy>       - move selected component")
    print("  render               - render board.svg")
    print("  save                 - save board.yaml")
    print("  jumper-list          - list jumpers")
    print("  jumper-add <id> <net> <x1> <y1> <x2> <y2> [color]")
    print("  jumper-del <id>")
    print("  quit                 - exit")

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
        elif name == "jumper-list":
            cmd_jumper_list(state, parts)
        elif name == "jumper-add":
            cmd_jumper_add(state, parts)
            cmd_render(state, parts)
        elif name == "jumper-del":
            cmd_jumper_del(state, parts)
            cmd_render(state, parts)
        elif name in ("quit", "exit", "q"):
            cmd_quit(state, parts)
            print("bye")
            return
        else:
            print(f"unknown command '{name}' (type 'help')")

    print("bye")
