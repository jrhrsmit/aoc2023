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
        self.cc_offset = None
        self.cc_period = None

    def __repr__(self):
        modules = [f"{sym}, " for sym in self.next_modules]
        return f"{self.symbol}{self.name} -> {modules}"


class FF(Module):
    def __init__(self, name, next_modules):
        super().__init__(name, next_modules)
        self.state = False
        self.symbol = "%"

    # @functools.lru_cache(maxsize=None)
    def rx(self, origin, data):
        if not data:
            self.state = not self.state
            return (self.name, self.state, self.next_modules)

    def get_output(self):
        return self.state


class Conjunction(Module):
    def __init__(self, name, next_modules):
        super().__init__(name, next_modules)
        self.symbol = "&"
        self.state = {}

    def add_input(self, name):
        if not isinstance(name, str):
            raise ValueError(f"Type of name is: {type(name)}")
        self.state[name] = False

    def get_output(self):
        return not all(self.state.values())

    # @functools.lru_cache(maxsize=None)
    def rx(self, origin, data):
        self.state[origin] = data
        return (self.name, not all(self.state.values()), self.next_modules)


class Broadcaster(Module):
    def __init__(self, name, next_modules):
        super().__init__(name, next_modules)
        self.symbol = ""

    # @functools.lru_cache(maxsize=None)
    def rx(self, origin, data):
        return (self.name, data, self.next_modules)


def run_sim_part2(modules):
    t_start = time.time()
    i = 0

    last_conj = [m for m in modules.values() if "rx" in m.next_modules][0]
    log.debug(f"Last conjunction: {last_conj}, inputs: {last_conj.inputs}")
    req_all_high = last_conj.inputs
    req_periods = {}

    for button_presses in track(range(2**48)):
        i += 1
        tx_queue = [("button", False, ["broadcaster"])]
        while tx_queue:
            origin, data, next_modules = tx_queue.pop(0)
            for next_module in next_modules:
                if next_module == "rx":
                    if not data:
                        log.info(f"Low pulse on rx at button: {i}")
                        return pulses_log, period, offset
                    continue
                elif next_module == "output":
                    continue
                tx = modules[next_module].rx(origin, data)
                if tx:
                    tx_queue.append(tx)

        for n in req_all_high:
            m = modules[n]
            if m.get_output():
                log.info(f"Found high pulse on {n} at button: {i}")
                req_periods[next_module] = button_presses
                if len(req_periods) == len(req_all_high):
                    log.info(f"Found all periods: {req_periods}")
                    lcm = np.lcm.reduce(list(req_periods.values()))
                    log.info(f"LCM: lcm")
                    return lcm
        if i % 1000000 == 0:
            t_end = time.time()
            speed = (i + 1) / (t_end - t_start)
            log.info(f"State: {i}, S/s: {speed:.2f}")

    t_end = time.time()
    log.info(f"Simulation took {t_end - t_start:.2f} seconds")
    log.info(f"States per second: {len(states) / (t_end - t_start):.2f}")

    return pulses_sum


def find_period(inputs, modules):
    ms = [modules[i] for i in inputs]
    cc_offset = None
    for cc in range(1**20):
        if all([(cc - m.cc_offset) % m.cc_period == 0 for m in ms]):
            cc_offset = cc
    for cc in range(cc_offset, 1**20):
        if all([(cc - m.cc_offset) % m.cc_period == 0 for m in ms]):
            cc_period = cc - cc_offset
    if cc_offset == cc_period:
        return (0, cc_offset)

    cc = cc_offset + 2 * cc_period
    if all([(cc - m.cc_offset) % m.cc_period == 0 for m in ms]):
        return (cc_offset, cc_period)

    raise ValueError("No period found")


def calc_cycles_part2(modules):
    tx_queue = [("button", False, ["broadcaster"])]
    clock_cycles = 0
    while tx_queue:
        origin, data, next_modules = tx_queue.pop(0)
        for n in next_modules:
            m = modules[n]
            if isinstance(m, Broadcaster):
                m.cc_offset = clock_cycles
                m.cc_period = 1
            elif isinstance(m, Conjunction):
                m.cc_offset = clock_cycles
                if not all([p.cc_period for p in m.inputs]):
                    tx_queue.append((origin, data, next_modules))
                    log.debug(f"Not all inputs of {n} have a period, skipping")
                    continue
                else:
                    m.cc_offset, m.cc_period = find_period(m.inputs, modules)
            elif isinstance(m, FF):
                m.cc_offset = clock_cycles
                if len(m.inputs) != 1:
                    log.error(
                        f"FF {n} has more than one input, inputs: {m.inputs}"
                    )
                m.cc_period = m.inputs[0] * 2
            log.debug(f"{n} -> {m.cc_offset}, {m.cc_period}")
            tx_queue.append((n, data, m.next_modules))
            if "rx" in m.next_modules:
                if m.cc_offset and m.cc_period:
                    log.info(
                        f"Clock cycles to reach rx: {m.cc_offset + m.cc_period}"
                    )

        clock_cycles += 1


def run_sim_part1(button_presses, modules):
    pulses_sum = [0, 0]
    t_start = time.time()
    for i in track(range(0, button_presses)):
        # log.debug(f"Button press {i + 1}")

        tx_queue = [("button", False, ["broadcaster"])]
        while tx_queue:
            origin, data, next_modules = tx_queue.pop(0)
            for next_module in next_modules:
                # log.debug(
                #    f"{origin} -{'high' if data else 'low'}-> {next_module}"
                # )
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
                modules[n].add_input(m.name)
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
        # calc_cycles_part2(modules)
        # exit()

        # rx_modules = {}
        # queue = [(m.name, "rx") for m in modules.values() if "rx" in m.next_modules]
        # while queue:
        #    (name, orig) = queue.pop(0)
        #    log.debug(f"RX modules: {name} -> {orig}, appending {modules[name].inputs}")
        #    if name not in rx_modules:
        #        rx_modules[name] = modules[name]
        #        rx_modules[name].next_modules = [orig]
        #    else:
        #        log.debug(f"Loop at {name} -> {orig}")
        #        rx_modules[name].next_modules.append(orig)

        #    queue += [(i, name) for i in modules[name].inputs if i not in rx_modules]

        # log.debug(
        #    f"Size all modules: {len(modules)}, size rx modules: {len(rx_modules)}"
        # )
        # log.debug(
        #    f"Size all links: {sum([len(modules[m].next_modules) for m in modules])}, size rx modules: {sum([len(rx_modules[m].next_modules) for m in rx_modules])}"
        # )

        # button_presses = 1000000000
        pulses_log = run_sim_part2(modules)
        # log.info(f"Part 2 answer: {len(pulses_log)}")


if __name__ == "__main__":
    # cProfile.run("typer.run(main)")
    typer.run(main)
