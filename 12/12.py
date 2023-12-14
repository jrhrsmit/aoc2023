import typer
from itertools import combinations
import re


def spring_conditions_satisfies_group(
    spring_conditions: list[str], groups: list[int]
) -> bool:
    for s, i in zip(spring_conditions, groups):
        if len(s) != i:
            return False
    return True


def build_regex_from_groups(groups: list[int]) -> str:
    regex = r"^[?|\.]*"
    for i, group in enumerate(groups):
        if i > 0:
            regex += r"[?|\.]+"
        regex += rf"[#|?]{{{group}}}"
    regex += r"[?|\.]*$"
    return regex


def build_regex_from_group(group: int) -> str:
    regex = r"[^|[?|\.]+]"
    regex += rf"[#|?]{{{group}}}"
    regex += r"[?|\.]*$"
    return regex

def decipher_spring_conditions(
    spring_conditions: str, groups: list[int]
) -> str:
    # spring_conditions = [s for s in spring_conditions.split(".") if s != ""]
    # damaged_groups = [int(i) for i in damaged_groups.split(",")]

    s = "." + spring_conditions + "."

    for g in groups:



    return len(list(matches))


def main(input_file: typer.FileText):
    input = input_file.read().strip().split("\n")
    for i in input:
        i = i.split(" ")
        spring_conditions = i[0]
        groups = i[1]
        num_solutions = decipher_spring_conditions(
            spring_conditions, [int(g) for g in groups.split(",")]
        )
        print(f"Number of solutions: {num_solutions}")


if __name__ == "__main__":
    typer.run(main)
