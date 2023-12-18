import typer
import re
import functools
from rich.logging import RichHandler
import logging
from rich.progress import track, Progress

from multiprocessing import Pool, freeze_support

FORMAT = "%(message)s"
logging.basicConfig(
    level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")


def clac_hash(string: str) -> int:
    current_value = 0
    for c in string:
        current_value += ord(c)
        current_value *= 17
        current_value %= 256
    log.debug(f"{string} -> {current_value}")
    return current_value


def calc_focussing_power(boxes: list) -> int:
    fp_sum = 0
    for i, box in enumerate(boxes):
        if not box:
            continue
        for j, (lens, focal_length) in enumerate(box.items()):
            fp = 1 + i
            fp *= j + 1
            fp *= focal_length
            fp_sum += fp
    return fp_sum


def print_boxes(boxes: list):
    for i, box in enumerate(boxes):
        if not box:
            continue
        log.debug(f"Box {i}:")
        for j, (lens, focal_length) in enumerate(box.items()):
            log.debug(f"  slot {j}: {lens} {focal_length}")


def main(
    input_file: typer.FileText,
    log_level: str = "INFO",
    part1: bool = True,
    part2: bool = True,
):
    log.setLevel(log_level)
    line = input_file.read().strip().replace("\n", "").replace("\r", "")

    if part1:
        current_value = 0
        for step in track(line.split(",")):
            current_value += clac_hash(step)
        log.info(f"Part1: {current_value}")

    if part2:
        boxes = [None] * 256
        for step in track(line.split(",")):
            if "-" in step:
                lens = step.split("-")[0]
                box = clac_hash(lens)
                if boxes[box] and lens in boxes[box]:
                    boxes[box].pop(lens)
                log.debug(f"Step: {step} -> Box {box}: {boxes[box]}")
            elif "=" in step:
                lens = step.split("=")[0]
                strength = int(step.split("=")[1])
                box = clac_hash(lens)
                if not boxes[box]:
                    boxes[box] = {}
                boxes[box][lens] = strength
                log.debug(f"Step: {step} -> Box {box}: {boxes[box]}")
            else:
                raise ValueError(f"Unknown step: {step}")
        print_boxes(boxes)
        fp = calc_focussing_power(boxes)
        log.info(f"Part2: {fp}")


if __name__ == "__main__":
    freeze_support()
    typer.run(main)
