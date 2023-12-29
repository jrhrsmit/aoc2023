import typer
import re
import functools
from rich.logging import RichHandler
import logging
from rich.progress import track, Progress, TransferSpeedColumn
import math
from enum import Enum
import cProfile
import time

from itertools import pairwise

import numpy as np

FORMAT = "%(message)s"
logging.basicConfig(
    level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


def get_coordinates_in_direction(x, y, direction: Direction):
    if direction == Direction.UP:
        return (x - 1, y)
    elif direction == Direction.RIGHT:
        return (x, y + 1)
    elif direction == Direction.DOWN:
        return (x + 1, y)
    else:
        return (x, y - 1)


class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col

        self.neighbors = []

        self.lowest_steps_even = math.inf
        self.lowest_steps_odd = math.inf

        self.steps_to_saturation = -1
        self.page_nodes_on_saturation = -1
        self.steps_to_side = dict([(d, (0, None)) for d in Direction])

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)
        neighbor.neighbors.append(self)

    def __repr__(self):
        return f"Node({self.row}, {self.col})"


def get_lowest_node(nodes: dict, side: Direction, r: int) -> Node:
    if side == Direction.UP:
        ns = [nodes[(0, c)] for c in range(r)]
    elif side == Direction.RIGHT:
        ns = [nodes[(c, r - 1)] for c in range(r)]
    elif side == Direction.DOWN:
        ns = [nodes[(r - 1, c)] for c in range(r)]
    else:
        ns = [nodes[(c, 0)] for c in range(r)]

    lowest_node = ns[0]
    for n in ns[1:]:
        if n.lowest_steps_even < lowest_node.lowest_steps_even:
            lowest_node = n
        elif n.lowest_steps_odd < lowest_node.lowest_steps_odd:
            lowest_node = n
    if (
        min(lowest_node.lowest_steps_even, lowest_node.lowest_steps_odd)
        == math.inf
    ):
        return None
    return lowest_node


def load(rows: list[str], wrap: bool = False) -> tuple[dict, Node]:
    nodes = {}
    width = len(rows[0])
    height = len(rows)
    log.debug(f"width: {width}, height: {height}")
    assert height % 2 == 1, "Height must be odd"
    assert width == height, "Width must equal height"

    for row, r in enumerate(rows):
        for col, char in enumerate(r):
            if char == "." or char == "S":
                node = Node(row, col)
                nodes[(row, col)] = node
                neighbors = [
                    (row - 1, col),
                    (row + 1, col),
                    (row, col - 1),
                    (row, col + 1),
                ]
                for n in neighbors:
                    if wrap:
                        if n[0] < 0:
                            n = (height - 1, n[1])
                        elif n[0] >= height:
                            n = (0, n[1])
                        if n[1] < 0:
                            n = (n[0], width - 1)
                        elif n[1] >= width:
                            n = (n[0], 0)
                    if n in nodes:
                        node.add_neighbor(nodes[n])
                if char == "S":
                    start = node
                    start.lowest_steps = 0
    return nodes, start


def find_saturation_point(nodes: dict, n: Node, r: int):
    max_steps = 0
    max_nodes = 0
    num_last_visited = 0
    for s in range(200):
        visited = end_positions_per_page(nodes, n, s)
        if visited == num_last_visited:
            if s > max_steps:
                max_steps = s
                max_nodes = visited
                break
    return (max_steps, max_nodes)


memo = dict()


# @functools.lru_cache(maxsize=None)
def end_positions_per_page(nodes: dict, start: Node, max_steps) -> int:
    if (start, max_steps) in memo:
        return memo[(start, max_steps)]
    visited_even = set()
    visited_odd = set()
    end_nodes = set()
    queue = [(start, 0)]
    while queue:
        node, steps = queue.pop(0)
        if steps % 2 == 0:
            if steps >= node.lowest_steps_even and node in visited_even:
                continue
            node.lowest_steps_even = steps
            visited_even.add(node)
        else:
            if steps >= node.lowest_steps_odd and node in visited_odd:
                continue
            node.lowest_steps_odd = steps
            visited_odd.add((node, steps))
        if steps < max_steps:
            for neighbor in node.neighbors:
                queue.append((neighbor, steps + 1))

    memo[(start, max_steps)] = len(visited_even)
    return len(visited_even)


# per page:
# voor elke entry node bepalen wat het aantal steps is om m te saturaten
# voor elke entry node bepalen wat per kant de optimale exit node is en hoeveel
# steps dat nodig heeft
# dan per page in de queue exit nodes bepalen per side, en dan


def get_neighbor_in_direction(nodes, node, direction, r) -> Node:
    row, col = get_coordinates_in_direction(node.row, node.col, direction)
    if row < 0:
        row = r - 1
    elif row >= r:
        row = 0
    if col < 0:
        col = r - 1
    elif col >= r:
        col = 0
    return nodes[(row, col)]


def end_positions_inf_grid(
    nodes: dict, start: Node, max_steps: int, r: int
) -> int:
    nodes_edge = [
        nodes[n]
        for n in nodes
        if n[0] == 0 or n[1] == 0 or n[1] == r - 1 or n[1] == r - 1
    ] + [start]
    for n in nodes_edge:
        (
            n.steps_to_saturation,
            n.page_nodes_on_saturation,
        ) = find_saturation_point(nodes, n, r)
        nc = nodes.copy()

        for side in Direction:
            lowest_node = get_lowest_node(nc, side, r)
            ln = nodes[(lowest_node.row, lowest_node.col)]
            min_steps = min(
                lowest_node.lowest_steps_even, lowest_node.lowest_steps_odd
            )
            next_entry = get_neighbor_in_direction(nodes, ln, side, r)
            n.steps_to_side[side] = (min_steps, next_entry)

    pages = set()
    sum_end_positions = 0
    queue = [(0, 0, start, max_steps)]
    log.debug(f"r: {r}")
    while queue:
        x, y, entry, steps_left = queue.pop(0)
        log.debug(f"Processing page: {x=}, {y=}, {entry=}, {steps_left=}")
        if steps_left >= entry.steps_to_saturation:
            sum_end_positions += entry.page_nodes_on_saturation
            steps_left -= entry.page_nodes_on_saturation
            for side in Direction:
                xa, ya = get_coordinates_in_direction(x, y, side)
                if (xa, ya) in pages:
                    continue
                pages.add((x, y))
                s, new_entry = entry.steps_to_side[side]
                new_steps_left = steps_left - s
                queue.append((xa, ya, new_entry, new_steps_left))
        else:
            nc = nodes.copy()
            sum_end_positions += end_positions_per_page(nc, entry, steps_left)
            for side in Direction:
                lowest_node = get_lowest_node(nc, side, r)
                if not lowest_node:
                    continue
                xa, ya = get_coordinates_in_direction(x, y, side)
                if (xa, ya) in pages:
                    continue
                if ms <= 0:
                    continue

                pages.add((x, y))
                ms, new_entry = entry.steps_to_side[side]
                queue.append((xa, ya, new_entry, ms))

    return sum_end_positions


def main(
    input_file: typer.FileText,
    log_level: str = "INFO",
    part1: bool = True,
    part2: bool = True,
):
    log.setLevel(log_level)
    rows = input_file.read().strip().split("\n")

    if part1:
        nodes, start = load(rows)
        ans = end_positions_per_page(nodes, start, 64)
        log.info(f"Part 1 answer: {ans}")

    if part2:
        nodes, start = load(rows, True)
        ans = end_positions_inf_grid(nodes, start, 100, len(rows))
        log.info(f"Part 2 answer: {ans}")


if __name__ == "__main__":
    # cProfile.run("typer.run(main)")
    typer.run(main)
