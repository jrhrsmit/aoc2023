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


# @functools.lru_cache(maxsize=2**8)
def get_spaces(
    spaces_len: int,
    spaces_sum: int,
    input_string: str,
    groups: tuple[int],
) -> int:
    num_solutions = 0

    if spaces_len == 1 or spaces_sum == 0:
        return 1

    for space in range(0, spaces_sum + 1):
        if "#" in input_string[:space]:
            break
        if "." in input_string[space : space + groups[0]]:
            continue
        if "#" == input_string[space + groups[0] : space + groups[0] + 1]:
            continue

        num_solutions += get_spaces(
            spaces_len - 1,
            spaces_sum - space,
            input_string[space + groups[0] + 1 :],
            groups[1:],
        )
    return num_solutions


def lmao(args) -> list[str]:
    spring_conditions = args[0]
    groups = args[1]

    total_len = len(spring_conditions)
    len_hashtags = sum(groups) + len(groups) - 1
    len_spaces = len(groups) + 1

    num_solutions = get_spaces(
        len_spaces, total_len - len_hashtags, spring_conditions, groups
    )

    return num_solutions


def multi_lmao(lmao_args: list[tuple]) -> int:
    ans = 0
    with Progress() as progress:
        task_id = progress.add_task("Working...", total=len(lmao_args))
        with Pool(processes=1) as p:
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

        ans = multi_lmao(part1_input)
        log.info(f"Part 1: Answer: {ans}")

    if part2:
        part2_input = []
        for line in input:
            i = line.split(" ")
            spring_conditions = (i[0] + "?") * 4 + i[0]
            groups = tuple([int(g) for g in i[1].split(",")] * 5)
            part2_input.append((spring_conditions, groups))

        ans = multi_lmao(part2_input)
        log.info(f"Part 2: Answer: {ans}")


if __name__ == "__main__":
    freeze_support()
    typer.run(main)
