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


def get_val(layout: list[str], pos: tuple[int]) -> str:
    return layout[pos[0]][pos[1]]


def get_left_heading(heading: Heading) -> Heading:
    return Heading((heading.value - 1) % 4)


def get_right_heading(heading: Heading) -> Heading:
    return Heading((heading.value + 1) % 4)


def get_next_nodes(
    layout: list[str],
    pos: tuple[int],
    heading: Heading,
    line_len: int,
    line_len_min_max: tuple[int] = (0, 3),
) -> list[tuple[int]]:
    width = len(layout[0])
    height = len(layout)

    next_nodes = []

    if line_len < line_len_min_max[1]:
        next_nodes.append((new_pos(pos, heading), heading, line_len + 1))

    if line_len >= line_len_min_max[0]:
        rheading = get_right_heading(heading)
        next_nodes.append((new_pos(pos, rheading), rheading, 1))
        lheading = get_left_heading(heading)
        next_nodes.append((new_pos(pos, lheading), lheading, 1))

    filtered_nodes = []
    for npos, nheading, nline_len in next_nodes:
        if npos[0] < 0 or npos[0] >= height or npos[1] < 0 or npos[1] >= width:
            continue
        filtered_nodes.append((npos, nheading, nline_len))

    return filtered_nodes


def find_shortest_path(
    layout: list[str], line_len_min_max: tuple[int] = (0, 3)
) -> int:
    traversed = {
        ((0, 0), Heading.EAST, 0): 0,
        ((0, 0), Heading.NORTH, 0): 0,
        ((0, 0), Heading.WEST, 0): 0,
        ((0, 0), Heading.SOUTH, 0): 0,
    }
    pos = (0, 0)
    line_len = 0

    queue = [(pos, Heading.EAST, 0), (pos, Heading.SOUTH, 0)]
    while queue:
        current_node = queue.pop(0)
        next_nodes = get_next_nodes(layout, *current_node, line_len_min_max)

        for n in next_nodes:
            n_pos = n[0]
            n_y = n_pos[0]
            n_x = n_pos[1]
            val = traversed[current_node] + layout[n_y][n_x]
            if n not in traversed:
                traversed[n] = val
                queue.append(n)
            elif traversed[n] > val:
                traversed[n] = val
                queue.append(n)

    end_pos = (len(layout) - 1, len(layout[0]) - 1)

    end_nodes = []
    for heading in Heading:
        for line_len in range(line_len_min_max[0], line_len_min_max[1] + 1):
            if (end_pos, heading, line_len) in traversed:
                log.debug(
                    f"{end_pos} {heading} {line_len} {traversed[(end_pos, heading, line_len)]}"
                )
                end_nodes.append(traversed[(end_pos, heading, line_len)])
    return min(end_nodes)


def main(
    input_file: typer.FileText,
    log_level: str = "INFO",
    part1: bool = True,
    part2: bool = True,
):
    log.setLevel(log_level)
    layout = [
        [int(c) for c in row] for row in input_file.read().strip().split("\n")
    ]

    if part1:
        heat_loss = find_shortest_path(layout)
        log.info(f"Part 1: {heat_loss}")

    if part2:
        heat_loss = find_shortest_path(layout, (4, 10))
        log.info(f"Part 2: {heat_loss}")


if __name__ == "__main__":
    freeze_support()
    typer.run(main)
