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


class Module:
    def __init__(self, name, next_modules):
        self.name = name
        self.next_modules = next_modules
        self.symbol = "?"
        self.inputs = []

    def __repr__(self):
        return f"{self.symbol}{self.name} -> {self.next_modules}"


class FF(Module):
    def __init__(self, name, next_modules):
        super().__init__(name, next_modules)
        self.state = None
        self.symbol = "%"

    def rx(self, origin, data):
        if not data:
            self.state = not self.state
            return (self.name, self.state, self.next_modules)


class Conjunction(Module):
    def __init__(self, name, next_modules):
        super().__init__(name, next_modules)
        self.symbol = "&"
        self.state_inputs = {}
        self.state = None

    def add_input(self, name, data):
        if not isinstance(name, str):
            raise ValueError(f"Type of name is: {type(name)}")
        self.state_inputs[name] = data
        # self.state = not all(self.state_inputs.values())

    def rx(self, origin, data):
        self.state_inputs[origin] = data
        self.state = not all(self.state_inputs.values())
        return (self.name, self.state, self.next_modules)


class Broadcaster(Module):
    def __init__(self, name, next_modules):
        super().__init__(name, next_modules)
        self.symbol = ""

    def rx(self, origin, data):
        return (self.name, data, self.next_modules)


def print_states(modules, last_conj, cc):
    states = [m.state for m in modules.values() if isinstance(m, FF)]
    states_str = "".join(["1" if s else "0" for s in states])
    states_req = [
        m.state for m in modules.values() if m.name in last_conj.inputs
    ]
    states_req_str = "".join(["1" if s else "0" for s in states_req])
    log.debug(f"CC: {cc}, States: {states_str}, Req: {states_req_str}")


def run_sim_part2(modules):
    last_conj = [m for m in modules.values() if "rx" in m.next_modules]
    if len(last_conj) != 1:
        raise ValueError(f"Expected one last conjunction, got: {last_conj}")
    last_conj = last_conj[0]
    log.info(f"Last conjunction: {last_conj}, inputs: {last_conj.inputs}")

    req_states = dict([(n, True) for n in last_conj.inputs])
    log.info(f"Required states: {req_states}")
    req_periods = {}

    for button_presses in track(range(1, 2**12)):
        tx_queue = [("button", False, ["broadcaster"])]
        while tx_queue:
            origin, data, next_modules = tx_queue.pop(0)
            if origin in req_states and data == req_states[origin]:
                log.info(
                    f"Found {data} state on {next_module} at button: {button_presses}"
                )
                req_periods[origin] = button_presses
                if len(req_periods) == len(req_states):
                    log.info(f"Found all periods: {req_periods}")
                    lcm = np.lcm.reduce(list(req_periods.values()))
                    log.info(f"LCM: {lcm}")
                    log.info(f"Button press: {lcm}")
                    return lcm
            for next_module in next_modules:
                if next_module == "rx":
                    continue
                tx = modules[next_module].rx(origin, data)
                if tx:
                    tx_queue.append(tx)

    log.error("No solution found")
    return -1


def run_sim_part1(button_presses, modules):
    pulses_sum = [0, 0]
    t_start = time.time()
    for i in track(range(0, button_presses)):
        log.debug(f"Button press {i + 1}")
        tx_queue = [("button", False, ["broadcaster"])]
        while tx_queue:
            origin, data, next_modules = tx_queue.pop(0)
            for next_module in next_modules:
                log.debug(
                    f"{origin} -{'high' if data else 'low'}-> {next_module}"
                )
                pulses_sum[data] += 1
                if next_module in modules:
                    tx = modules[next_module].rx(origin, data)
                    if tx:
                        tx_queue.append(tx)

    t_end = time.time()
    log.info(f"Simulation took {t_end - t_start:.2f} seconds")
    log.info(f"States per second: {button_presses / (t_end - t_start):.2f}")

    return pulses_sum


def load(rows):
    modules = {}
    for row in rows:
        name = row.split(" -> ")[0]
        next_modules = row.split(" -> ")[1].split(", ")
        if name.startswith("%"):
            name = name.strip("%")
            modules[name.strip("%")] = FF(name, next_modules)
        elif name.startswith("&"):
            name = name.strip("&")
            modules[name] = Conjunction(name, next_modules)
        elif name == "broadcaster":
            modules[name] = Broadcaster(name, next_modules)
        else:
            raise ValueError(f"Unknown module type: {name}")

    for m in modules.values():
        for n in m.next_modules:
            if n not in modules:
                log.warning(f"Module {n} not found, skipping")
                continue
            modules[n].inputs.append(m.name)
            if isinstance(modules[n], Conjunction):
                modules[n].add_input(m.name, False)
                # modules[n].add_input(m.name, modules[m.name].state)
    return modules


def main(
    input_file: typer.FileText,
    log_level: str = "INFO",
    part1: bool = True,
    part2: bool = True,
):
    log.setLevel(log_level)
    rows = input_file.read().strip().split("\n")

    if part1:
        modules = load(rows)

        button_presses = 1000
        pulses_sum = run_sim_part1(button_presses, modules)
        log.info(f"Part 1 answer: {pulses_sum[True] * pulses_sum[False]}")

    if part2:
        modules = load(rows)
        ans = run_sim_part2(modules)
        log.info(f"Part 2 answer: {ans}")


if __name__ == "__main__":
    # cProfile.run("typer.run(main)")
    typer.run(main)
