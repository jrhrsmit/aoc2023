import typer
import re
import functools
from rich.logging import RichHandler
import logging
from rich.progress import track, Progress
import math
from enum import Enum

from multiprocessing import Pool, freeze_support

FORMAT = "%(message)s"
logging.basicConfig(
    level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")


class Heading(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


def new_pos(pos: tuple[int], heading: Heading) -> tuple[int]:
    if heading == Heading.NORTH:
        return (pos[0] - 1, pos[1])
    elif heading == Heading.EAST:
        return (pos[0], pos[1] + 1)
    elif heading == Heading.SOUTH:
        return (pos[0] + 1, pos[1])
    elif heading == Heading.WEST:
        return (pos[0], pos[1] - 1)


def print_energized(layout: list[str], positions: set[tuple]):
    for i, row in enumerate(layout):
        for j, col in enumerate(row):
            if (i, j) in positions:
                print("#", end="")
            else:
                print(".", end="")
        print()


def num_tiles_traversed(
    layout: list[str],
    pos: tuple[int] = (0, -1),
    heading: Heading = Heading.EAST,
    positions_traversed: set[tuple] | None = None,
) -> set[tuple[int]]:
    width = len(layout[0])
    height = len(layout)

    if positions_traversed is None:
        positions_traversed = set()

    while True:
        pos = new_pos(pos, heading)
        if pos[0] < 0 or pos[0] >= height or pos[1] < 0 or pos[1] >= width:
            log.debug(
                f"Out of bounds, positions traversed: {len(positions_traversed)}"
            )
            break
        if (pos, heading) in positions_traversed:
            log.debug(
                f"Loop detected, positions traversed: {len(positions_traversed)}"
            )
            break
        log.debug(f"New pos: {pos} ({heading} {layout[pos[0]][pos[1]]})")
        positions_traversed.add((pos, heading))
        if heading == Heading.NORTH:
            if layout[pos[0]][pos[1]] == "-":
                positions_traversed.update(
                    num_tiles_traversed(
                        layout, pos, Heading.WEST, positions_traversed
                    )
                )
                heading = Heading.EAST
            elif layout[pos[0]][pos[1]] == "/":
                heading = Heading.EAST
            elif layout[pos[0]][pos[1]] == "\\":
                heading = Heading.WEST
        elif heading == Heading.EAST:
            if layout[pos[0]][pos[1]] == "|":
                positions_traversed.update(
                    num_tiles_traversed(
                        layout, pos, Heading.NORTH, positions_traversed
                    )
                )
                heading = Heading.SOUTH
            elif layout[pos[0]][pos[1]] == "/":
                heading = Heading.NORTH
            elif layout[pos[0]][pos[1]] == "\\":
                heading = Heading.SOUTH
        elif heading == Heading.SOUTH:
            if layout[pos[0]][pos[1]] == "-":
                positions_traversed.update(
                    num_tiles_traversed(
                        layout, pos, Heading.WEST, positions_traversed
                    )
                )
                heading = Heading.EAST
            elif layout[pos[0]][pos[1]] == "/":
                heading = Heading.WEST
            elif layout[pos[0]][pos[1]] == "\\":
                heading = Heading.EAST
        elif heading == Heading.WEST:
            if layout[pos[0]][pos[1]] == "|":
                positions_traversed.update(
                    num_tiles_traversed(
                        layout, pos, Heading.NORTH, positions_traversed
                    )
                )
                heading = Heading.SOUTH
            elif layout[pos[0]][pos[1]] == "/":
                heading = Heading.SOUTH
            elif layout[pos[0]][pos[1]] == "\\":
                heading = Heading.NORTH

    return positions_traversed


def main(
    input_file: typer.FileText,
    log_level: str = "INFO",
    part1: bool = True,
    part2: bool = True,
):
    log.setLevel(log_level)
    layout = input_file.read().strip().split("\n")

    if part1:
        positions_traversed = num_tiles_traversed(layout)
        positions_traversed = {pos for pos, heading in positions_traversed}
        print_energized(layout, positions_traversed)
        num_tiles = len(positions_traversed)
        log.info(f"Part 1: {num_tiles}")

    if part2:
        positions_traversed = set()
        width = len(layout[0])
        height = len(layout)
        pt_max = 0
        for y in track(
            range(height),
            description="Traversing with light from top to bottom",
        ):
            positions_traversed = num_tiles_traversed(
                layout, (y, -1), Heading.EAST
            )
            pt_max = max(
                pt_max, len(set({pos for pos, heading in positions_traversed}))
            )
            positions_traversed = num_tiles_traversed(
                layout, (y, width), Heading.WEST
            )
            pt_max = max(
                pt_max, len(set({pos for pos, heading in positions_traversed}))
            )
        for x in track(
            range(width),
            description="Traversing with light from left to right",
        ):
            positions_traversed = num_tiles_traversed(
                layout, (-1, x), Heading.SOUTH
            )
            pt_max = max(
                pt_max, len(set({pos for pos, heading in positions_traversed}))
            )
            positions_traversed = num_tiles_traversed(
                layout, (height, x), Heading.NORTH
            )
            pt_max = max(
                pt_max, len(set({pos for pos, heading in positions_traversed}))
            )
        # num_tiles = len(positions_traversed)
        log.info(f"Part 2: {pt_max}")


if __name__ == "__main__":
    freeze_support()
    typer.run(main)
