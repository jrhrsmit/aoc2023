import typer
import re
import functools
from rich.logging import RichHandler
import logging
from rich.progress import track, Progress
import math
from enum import Enum

from itertools import pairwise

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


def int_to_heading(direction: int) -> Heading:
    return Heading((direction + 1) % 4)


def direction_to_heading(direction: str) -> Heading:
    if direction == "R":
        return Heading.EAST
    elif direction == "L":
        return Heading.WEST
    elif direction == "U":
        return Heading.NORTH
    elif direction == "D":
        return Heading.SOUTH


def new_pos(pos: tuple[int], heading: Heading) -> tuple[int]:
    if heading == Heading.NORTH:
        return (pos[0] - 1, pos[1])
    elif heading == Heading.EAST:
        return (pos[0], pos[1] + 1)
    elif heading == Heading.SOUTH:
        return (pos[0] + 1, pos[1])
    elif heading == Heading.WEST:
        return (pos[0], pos[1] - 1)


def get_left_heading(heading: Heading) -> Heading:
    return Heading((heading.value - 1) % 4)


def get_right_heading(heading: Heading) -> Heading:
    return Heading((heading.value + 1) % 4)


def get_min_max(path: dict[set[int]]) -> tuple[int]:
    min_y = min([item[0] for item in path.items()])
    max_y = max([item[0] for item in path.items()])
    min_x = min([min(item[1]) for item in path.items()])
    max_x = max([max(item[1]) for item in path.items()])
    return (min_y, max_y, min_x, max_x)


def get_side_in(
    path: dict[set[int]], side_r: dict[set[int]], side_l: dict[set[int]]
) -> set[tuple[int]]:
    min_y, max_y, min_x, max_x = get_min_max(path)

    log.debug(
        f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}"
    )

    side_in = side_r

    for y, xs in side_r.items():
        if y < min_y or y > max_y:
            side_in = side_l
            break

        if any([x < min_x or x > max_x for x in xs]):
            side_in = side_l
            break

    if side_in == side_r:
        log.debug(f"Set side_in to side_r")
    else:
        log.debug(f"Set side_in to side_l")
    return side_in


def fill_area(path: dict[set[int]], side_in: dict[set[int]]) -> int:
    filled_area = side_in.copy()
    # for y, xs in side_in.items():
    #     for x in xs.copy():
    #         for dy in range(y - 1, y + 2):
    #             for dx in range(x - 1, x + 2):
    #                 if dx == x and dy == y:
    #                     continue
    #                 if dy in path and dx in path[dy]:
    #                     continue
    #                 if dy not in filled_area:
    #                     filled_area[dy] = set()
    #                 filled_area[dy].add(dx)

    min_y, max_y, min_x, max_x = get_min_max(path)

    filled_area_size = 0
    for y in track(range(min_y, max_y + 1), description="Calculting area"):
        filled_area_size += len(path[y])
        if y not in filled_area:
            continue
        xs_filled = sorted(list(filled_area[y]))
        xs_path = sorted(list(path[y]))
        for x1, x2 in pairwise(xs_path):
            if x2 - x1 > 1:
                if x1 + 1 in xs_filled:
                    filled_area_size += (x2 - x1) - 1

    return filled_area_size


def print_area(path: dict[set[int]], side_in: dict[set[int]]):
    min_y, max_y, min_x, max_x = get_min_max(path)

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if y in path and x in path[y]:
                print("#", end="")
            elif y in side_in and x in side_in[y]:
                print("I", end="")
            else:
                print(".", end="")
        print()


def print_from_edges(path: dict[set[int]]):
    log.debug(f"path.items(): {path.items()}")
    min_y, max_y, min_x, max_x = get_min_max(path)

    log.debug(
        f"min_y: {min_y}, max_y: {max_y}, min_x: {min_x}, max_x: {max_x}"
    )
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if y in path and x in path[y]:
                print("#", end="")
            else:
                print(".", end="")
        print()


def add_to_path(path: dict[set[int]], pos: tuple[int]):
    if pos[0] not in path:
        path[pos[0]] = set()
    path[pos[0]].add(pos[1])


def loop_area(plan: list[tuple]) -> int:
    pos = (0, 0)

    path = {}
    path[0] = set()
    path[0].add(0)

    side_r = {}
    side_l = {}

    old_heading = None
    for heading, distance in track(plan, description="Walking path"):
        for _ in range(distance):
            old_pos = pos
            pos = new_pos(pos, heading)
            add_to_path(path, pos)

            heading_l = get_left_heading(heading)
            pos_l1 = new_pos(old_pos, heading_l)
            add_to_path(side_l, pos_l1)
            pos_l2 = new_pos(pos, heading_l)
            add_to_path(side_l, pos_l2)

            heading_r = get_right_heading(heading)
            pos_r1 = new_pos(old_pos, heading_r)
            add_to_path(side_r, pos_r1)
            pos_r2 = new_pos(pos, heading_r)
            add_to_path(side_r, pos_r2)

    for y, xs in path.items():
        if y in side_r:
            side_r[y] = side_r[y].difference(path[y])
        if y in side_l:
            side_l[y] = side_l[y].difference(path[y])

    log.debug("Finding inside side")
    side_in = get_side_in(path, side_r, side_l)
    # print_area(path, side_in)

    log.debug("Filling area")
    filled_area_size = fill_area(path, side_in)

    return filled_area_size


def main(
    input_file: typer.FileText,
    log_level: str = "INFO",
    part1: bool = True,
    part2: bool = True,
):
    log.setLevel(log_level)
    rows = input_file.read().strip().split("\n")

    if part1:
        dig_plan = [
            (
                direction_to_heading(row.split(" ")[0]),
                int(row.split(" ")[1]),
            )
            for row in rows
        ]
        area = loop_area(dig_plan)
        log.info(f"Part 1: {area}")

    if part2:
        dig_plan = [
            (
                int_to_heading(int(row.split(" ")[2].strip("(#)")[-1])),
                int(row.split(" ")[2].strip("(#)")[:-1], 16),
            )
            for row in rows
        ]
        area = loop_area(dig_plan)
        log.info(f"Part 1: {area}")


if __name__ == "__main__":
    freeze_support()
    typer.run(main)
