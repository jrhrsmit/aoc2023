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


class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.neighbors = []
        self.lowest_steps = math.inf

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)
        neighbor.neighbors.append(self)


def load(rows: list[str], wrap: bool = False) -> tuple[dict, Node]:
    nodes = {}
    width = len(rows[0])
    height = len(rows)

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


def run_part1(nodes: dict, start: Node, max_steps: int = 64) -> int:
    visited = set()
    end_nodes = set()
    queue = [(start, 0)]
    while queue:
        node, steps = queue.pop(0)
        # log.debug(f"Node: {node.row}, {node.col}, steps: {steps}")
        if (node, steps) in visited:
            continue
        elif steps == max_steps:
            end_nodes.add(node)
        elif steps < max_steps:
            for neighbor in node.neighbors:
                if (neighbor, steps + 1) in visited:
                    continue
                queue.append((neighbor, steps + 1))
        visited.add((node, steps))
    return len(end_nodes)


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
        ans = run_part1(nodes, start, 64)
        log.info(f"Part 1 answer: {ans}")

    if part2:
        nodes, start = load(rows, True)
        ans = run_part1(nodes, start, 500)
        log.info(f"Part 2 answer: {ans}")


if __name__ == "__main__":
    # cProfile.run("typer.run(main)")
    typer.run(main)
