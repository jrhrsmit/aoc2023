import typer
import re
import functools
from rich.logging import RichHandler
import logging
from rich.progress import track, Progress
import math
from enum import Enum

from itertools import pairwise

import numpy as np


def polygon_area(vertices):
    """
    Return the area of the polygon enclosed by vertices using the shoelace
    algorithm.

    """

    a = np.vstack((vertices, vertices[0]))
    S1 = sum(a[:-1, 0] * a[1:, 1])
    S2 = sum(a[:-1, 1] * a[1:, 0])
    return abs(S1 - S2) / 2


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


def get_left_heading(heading: Heading) -> Heading:
    return Heading((heading.value - 1) % 4)


def get_right_heading(heading: Heading) -> Heading:
    return Heading((heading.value + 1) % 4)


def direction_to_heading(direction: str) -> Heading:
    if direction == "R":
        return Heading.EAST
    elif direction == "L":
        return Heading.WEST
    elif direction == "U":
        return Heading.NORTH
    elif direction == "D":
        return Heading.SOUTH


def walk_direction(
    pos: tuple[int],
    prev_heading: Heading,
    heading: Heading,
    next_heading: Heading,
    distance: int,
) -> tuple[int]:
    if prev_heading:
        rheading = get_right_heading(prev_heading)
        lheading = get_left_heading(prev_heading)
        if heading == lheading:
            log.debug(f"Went left last time, so distance -= 1")
            distance -= 1
    if next_heading:
        rheading = get_right_heading(heading)
        lheading = get_left_heading(heading)
        if next_heading == rheading:
            log.debug(f"Going right next time, so distance += 1")
            distance += 1
    if heading == Heading.EAST:
        pos = (pos[0], pos[1] + distance)
    elif heading == Heading.WEST:
        pos = (pos[0], pos[1] - distance)
    elif heading == Heading.NORTH:
        pos = (pos[0] - distance, pos[1])
    elif heading == Heading.SOUTH:
        pos = (pos[0] + distance, pos[1])

    return pos


def loop_area(plan: list[tuple]) -> int:
    pos = (0, 0)

    vertces = [pos]

    h = [heading for heading, _ in plan] + [plan[0][0]]
    headings = zip(h[:-1], h[1:])
    distances = [distance for _, distance in plan]
    p = zip(headings, distances)
    prev_heading = plan[0][0]
    for (heading, next_heading), distance in track(
        p, description="Walking path"
    ):
        log.debug(
            f"pos: {pos}, "
            f"prev_heading: {prev_heading.name}, "
            f"heading: {heading.name}, "
            f"next_heading: {next_heading}, "
            f"distance: {distance}"
        )
        pos = walk_direction(
            pos, prev_heading, heading, next_heading, distance
        )
        vertces.append(pos)
        prev_heading = heading

    return int(polygon_area(vertces))


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
        distances = [distance for _, distance in dig_plan]
        area = loop_area(dig_plan)
        log.info(f"Part 1: {area}")


if __name__ == "__main__":
    typer.run(main)
