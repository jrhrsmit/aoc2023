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

memo = {}


def get_spaces(
    input_string: str,
    groups: tuple[int],
) -> int:
    global memo
    if (input_string, groups) in memo:
        return memo[(input_string, groups)]

    num_solutions = 0

    if not groups:
        if "#" in input_string:
            return 0
        else:
            return 1

    for space in range(0, len(input_string) - sum(groups) - len(groups) + 2):
        if "#" in input_string[:space]:
            break
        if "." in input_string[space : space + groups[0]]:
            continue
        if "#" == input_string[space + groups[0] : space + groups[0] + 1]:
            continue

        num_solutions += get_spaces(
            input_string[space + groups[0] + 1 :],
            groups[1:],
        )
    memo[(input_string, groups)] = num_solutions
    return num_solutions


def lmao(args) -> list[str]:
    spring_conditions = args[0]
    groups = args[1]

    log.debug(f"Processing {spring_conditions} {groups}")
    num_solutions = get_spaces(spring_conditions, groups)

    return num_solutions


def multi_lmao(lmao_args: list[tuple], nproc: int = 1) -> int:
    ans = 0
    with Progress() as progress:
        task_id = progress.add_task("Working...", total=len(lmao_args))
        with Pool(processes=nproc) as p:
            for result in p.imap(lmao, lmao_args):
                ans += result
                progress.advance(task_id)

    return ans


def main(
    input_file: typer.FileText,
    log_level: str = "INFO",
    part1: bool = True,
    part2: bool = True,
    n: int = -1,
    nproc: int = 10,
):
    log.setLevel(log_level)

    input = input_file.read().strip().split("\n")

    if n >= 0:
        input = [input[n]]

    if part1:
        part1_input = []
        for line in input:
            i = line.split(" ")
            spring_conditions = i[0]
            groups = tuple([int(g) for g in i[1].split(",")])
            part1_input.append((spring_conditions, groups))

        ans = multi_lmao(part1_input, nproc)
        log.info(f"Part 1: Answer: {ans}")

    if part2:
        part2_input = []
        for line in input:
            i = line.split(" ")
            spring_conditions = (i[0] + "?") * 4 + i[0]
            groups = tuple([int(g) for g in i[1].split(",")] * 5)
            part2_input.append((spring_conditions, groups))

        ans = multi_lmao(part2_input, nproc)
        log.info(f"Part 2: Answer: {ans}")


if __name__ == "__main__":
    freeze_support()
    typer.run(main)
