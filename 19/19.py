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


FORMAT = "%(message)s"
logging.basicConfig(
    level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")


class Condition:
    def __init__(self, var: str | None, min: int, max: int, tgt: str):
        self.var = var
        self.min = min
        self.max = max
        self.tgt = tgt

    def check(self, xmas: dict[str, int]):
        if self.var is None:
            return self.tgt
        if self.min <= xmas[self.var] <= self.max:
            return self.tgt
        return None

    def __contains__(self, item: int):
        return self.min <= item <= self.max

    def __repr__(self):
        return f"{self.var}:{self.min}-{self.max} -> {self.tgt}"

    def intersection(self, other):
        if self.var != other.var and self.var is not None and other.var is not None:
            return None
        if self.max < other.min or self.min > other.max:
            return None
        return Condition(
            self.var,
            max(self.min, other.min),
            min(self.max, other.max),
            other.tgt,
        )

    def __sub__(self, other):
        if other.max > self.max and other.min < self.min:
            raise ValueError(f"Cannot subtract {other} from {self}")
        if self.min == other.min:
            return Condition(
                self.var,
                min(other.max, self.max) + 1,
                max(self.max, other.max),
                self.tgt,
            )
        if self.max == other.max:
            return Condition(
                self.var,
                min(self.min, other.min),
                max(other.min, self.min) - 1,
                self.tgt,
            )
        if self.min < other.min:
            return Condition(self.var, self.min, other.min - 1, self.tgt)
        if self.max > other.max:
            return Condition(self.var, other.max + 1, self.max, self.tgt)
        return None


def parse_rule(rules: dict[str, str]) -> dict[str, list]:
    rules_parsed = {}
    for name, rule in rules.items():
        conditions = []
        for r in rule:
            if ":" in r:
                cond, tgt = r.split(":")
                if "<" in cond:
                    cond = cond.split("<")
                    var = cond[0]
                    max_val = int(cond[1]) - 1
                    cond = Condition(var, 0, max_val, tgt)
                elif ">" in cond:
                    cond = cond.split(">")
                    var = cond[0]
                    min_val = int(cond[1]) + 1
                    cond = Condition(var, min_val, math.inf, tgt)
                else:
                    raise ValueError(f"Unknown condition {cond}")
            else:
                tgt = r
                cond = Condition(None, 0, math.inf, tgt)
            conditions.append(cond)
        rules_parsed[name] = conditions
    return rules_parsed

def calc_accepted(conditions :dict[str, Condition]):
    accepted = 1
    for cond in conditions.values():
        accepted *= cond.max - cond.min + 1
    return accepted

def get_num_accepted(
    rule_key: str,
    rules: dict[str, list],
    prev_conditions: dict[str, Condition],
) -> int:
    num_accepted = 0
    rule = rules[rule_key]
    log.debug(f"Prev conditions: {prev_conditions}")
    log.debug(f"Rule: {rule}")

    conditions = prev_conditions.copy()
    for cond in rule:
        log.debug(f"Rule {rule_key}: condition: {cond}")
        if cond.var:
            intersection = conditions[cond.var].intersection(cond)
            if intersection:
                conditions_int = conditions.copy()
                conditions_int[cond.var].min = intersection.min
                conditions_int[cond.var].max = intersection.max
            
                remaining = conditions[cond.var] - cond
                conditions = conditions.copy()
                conditions[cond.var].min = remaining.min
                conditions[cond.var].max = remaining.max
        else:
            intersection = cond
            conditions_int = conditions.copy()
            conditions = [None] * len(conditions)

        if intersection:
            rule_key = cond.tgt
            if cond.tgt == "R":
                continue


            if cond.tgt == "A":
                num_accepted += calc_accepted(conditions_int)
                continue
            
            if not cond.tgt:
                num_accepted += get_num_accepted(cond.tgt, rules, conditions_int)
                continue
            
            num_accepted += get_num_accepted(cond.tgt, rules, conditions_int)

        if None in conditions:
            return num_accepted 
    return num_accepted


def check_part(parts: dict[str, int], rules: dict[str, list]) -> int:
    tgt = "in"
    while True:
        rule = rules[tgt]
        for cond in rule:
            tgt = cond.check(parts)
            if tgt == "R":
                return 0
            if tgt == "A":
                return sum(parts.values())
            if tgt is not None:
                break
    raise ValueError(f"Unknown target {tgt}")


def main(
    input_file: typer.FileText,
    log_level: str = "INFO",
    part1: bool = True,
    part2: bool = True,
):
    log.setLevel(log_level)
    rows = input_file.read().strip().split("\n")

    rules = rows[: rows.index("")]
    parts = rows[rows.index("") + 1 :]

    parts_txt = [p.strip("{}").split(",") for p in parts]
    parts = []
    for t in parts_txt:
        part = {}
        for p in t:
            p = p.split("=")
            part[p[0]] = int(p[1])
        parts.append(part)

    rules_txt = [r.strip("}").split("{") for r in rules]
    rules = {}
    for r in rules_txt:
        rules[r[0]] = r[1].split(",")

    rules = parse_rule(rules)


    if part1:
        accepted_parts_sum = 0
        for p in parts:
            accepted_parts_sum += check_part(p, rules)
        log.info(f"Part 1: {accepted_parts_sum}")

    if part2:
        accepted = 1
        prev_conditions = {}
        for var in "xmas":
            prev_conditions[var] = Condition(var, 1, 4000, "in")
        accepted_conditions = get_num_accepted("in", rules, prev_conditions)
        log.info(f"Part 2: {accepted_conditions}")


if __name__ == "__main__":
    typer.run(main)
