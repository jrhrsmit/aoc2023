import typer
import re
import functools
from rich.logging import RichHandler
import logging
from rich.progress import track

FORMAT = "%(message)s"
logging.basicConfig(
    level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")


def check_spring_conditions(
    input_str: str, check_me: str, groups: list[int]
) -> bool:
    """
    Checks if check_me satisfies the spring conditions in input_str, given the groups

    input_str: string of spring conditions
    check_me: string to check
    groups: list of group lengths

    returns: True if check_me satisfies the spring conditions, False otherwise
    """

    assert len(input_str) == len(
        check_me
    ), f"Lengths do not match: {input_str} != {check_me}"
    groups_check = [len(g) for g in check_me.split(".") if g]
    assert (
        groups_check == groups
    ), f"Groups do not match: {groups_check} != {groups}"
    assert "?" not in check_me, f"Check me contains ?: {check_me}"

    for c, d in zip(input_str, check_me):
        if c == "#" and d != "#":
            log.debug(f"# don't match up {input_str}, {check_me}")
            return False
        elif c == "." and d != ".":
            log.debug(f". don't match up {input_str}, {check_me}")
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


@functools.cache
def build_regex_from_group(group: int, eol: bool) -> str:
    regex = rf"(#|\?){{{group}}}"
    if eol:
        regex += r"(\?|\.|$)"
    else:
        regex += r"(\?|\.)"
    return regex


def to_spring_condition(groups: list[int], spaces: list[int]) -> str:
    """
    Convert a list of groups and spaces to a spring condition

    must satisfy len(spaces) == len(groups) + 1

    groups: list of group lengths
    spaces: list of space lengths

    returns: string of spring conditions
    """
    spaces = [spaces[0]] + [s + 1 for s in spaces[1:-1]] + [spaces[-1]]
    spring_condition = "." * spaces[0]
    for s, g in zip(spaces[1:], groups):
        spring_condition += "#" * g + "." * s
    return spring_condition


@functools.cache
def get_spaces(
    spaces_len: int, spaces_sum: int, depth: int = 0
) -> list[list[int]]:
    """
    Get all possible combinations of spaces that satisfy the conditions

    Conditions: len(spaces) == spaces_len, and sum(spaces) == spaces_sum

    spaces_len: number of groups of spaces
    spaces_sum: sum of all spaces

    returns: list of lists of spaces
    """
    dbg = "\t" * depth
    spaces = []
    log.debug(dbg + f"spaces_len: {spaces_len}, spaces_sum: {spaces_sum}")
    if spaces_len == 1:
        log.debug(dbg + f"Returning: {[[spaces_sum]]}")
        return [[spaces_sum]]
    elif spaces_sum == 0:
        log.debug(dbg + f"Returning: {[[0] * spaces_len]}")
        return [[0] * spaces_len]
    for space in range(0, spaces_sum + 1):
        log.debug(
            dbg
            + f"Space: {space}; calling get_spaces({spaces_len - 1}, {spaces_sum - space})"
        )
        for r in get_spaces(spaces_len - 1, spaces_sum - space):
            spaces.append([space] + r)
    return spaces


def get_options(groups: list[int], total_len: int) -> list[str]:
    """
    Get all possible combinations of spaces that satisfy the conditions

    groups: list of group lengths
    total_len: total length of the string

    returns: list of strings of spring conditions
    """
    len_hashtags = sum(groups) + len(groups) - 1
    len_spaces = len(groups) + 1
    log.debug(f"Finding spaces for groups: {groups}, total_len: {total_len}")
    log.debug(f"Calling get_spaces({len_spaces}, {total_len - len_hashtags})")
    # spaces_options = [[0] * len_spaces] + get_spaces(
    spaces_options = get_spaces(len_spaces, total_len - len_hashtags)
    options = []
    # log.debug(f"Finding options for groups: {groups}, total_len: {total_len}")
    for spaces in spaces_options:
        s = to_spring_condition(groups, spaces)
        options.append(s)
    log.debug(f"Spaces options: {spaces_options}")
    log.debug(f"Options: {options}")
    return options


def lmao(spring_conditions: str, groups: list[int]) -> list[str]:
    log.debug(
        f"Finding options for groups: {groups}, spring_conditions: {spring_conditions}"
    )
    options = get_options(groups, len(spring_conditions))
    # num_solutions = sum(
    #     [1 for o in options if check_spring_conditions(spring_conditions, o, groups)]
    # )
    num_solutions = 0
    for o in options:
        valid = check_spring_conditions(spring_conditions, o, groups)
        log.debug(
            f"Input: {spring_conditions}, option: {o}, groups: {groups}, valid: {valid}"
        )
        if valid:
            num_solutions += 1
    return num_solutions


@functools.lru_cache(maxsize=10*2**20)
def find_matches(
    search_string: str, regex: str, group: int
) -> tuple[tuple[str]]:
    match = re.search(regex, search_string)

    remainders = []

    span_sum = 0
    while match:
        span = match.span()
        # if there is a rock in the string before the match, it is illegal
        span_sum += span[0]
        if "#" in search_string[: span[0]]:
            break
        search_match = "#" * group + "." * (span[1] - span[0] - group)
        search_prefix = "." * span_sum + search_match

        remainders.append((search_prefix, search_string[span[1] :]))

        # continue next iteration from 1 character after the match
        span_sum += 1
        if "#" in search_string[: span[0] + 1]:
            break
        search_string = search_string[span[0] + 1 :]
        match = re.search(regex, search_string)

    return remainders


def find_first_occurrence_rec(
    string: str, groups: list[int], prefix: str = "", depth: int = 0
) -> int:
    dbg = "\t" * depth

    log.debug(
        dbg
        + f"Prefix: {prefix}\n"
        + dbg
        + f"Remainder: {string}\n"
        + dbg
        + f"groups: {groups}"
    )

    if not groups:
        log.debug(dbg + "Solution: " + prefix + string)
        log.debug(dbg + "No more groups, all matched, return 1 solution")
        return 1

    if sum(groups) + len(groups) - 1 == len(string):
        s = to_spring_condition(groups, [0] * (len(groups) + 1))
        log.debug(dbg + f"Only one solution fits for this branch: {s}")
        if check_spring_conditions(string, s, groups):
            log.debug(dbg + "Solution: " + prefix + s)
            return 1
        else:
            log.debug(dbg + "No match, 0 solutions for this branch")
            return 0

    remainder_end_len = sum(groups[1:]) + len(groups[1:]) - 1
    if remainder_end_len > 0:
        search_string = string[:-remainder_end_len]
        remainder_end = string[-remainder_end_len:]
        regex = build_regex_from_group(groups[0], False)
    else:
        search_string = string
        remainder_end = ""
        regex = build_regex_from_group(groups[0], True)

    log.debug(
        dbg
        + f"rem_end_len: {remainder_end_len} "
        + f"search_string: {search_string} "
        + f"regex: {regex}"
    )

    matches = find_matches(search_string, regex, groups[0])
    remainders = []
    for match in matches:
        remainders.append((prefix + match[0], match[1] + remainder_end))

    log.debug(dbg + f"Remainders: {remainders}")
    groups = groups[1:]

    if not remainders and not groups:
        log.debug(dbg + "Solution: " + prefix + string)
        log.debug(
            dbg + "No more remainders, no more groups, return 1 solution"
        )
        return 1

    k = 0
    for p, s in remainders:
        l = find_first_occurrence_rec(s, groups, p, depth + 1)
        k += l

    log.debug(dbg + f"Found {k} solutions for this branch")
    return k


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

    part1_input = []

    if part1:
        ans = []

        for line in track(
            input, description="Calculating solutions for part 1"
        ):
            i = line.split(" ")
            spring_conditions = i[0]
            groups = [int(g) for g in i[1].split(",")]
            # num_solutions = lmao(spring_conditions, groups)
            num_solutions = find_first_occurrence_rec(
                spring_conditions, groups
            )
            log.debug(f"Number of solutions: {num_solutions}")
            ans.append(num_solutions)

        log.debug(f"Part 1: num solutions: {ans}")
        log.info(f"Part 1: Answer: {sum(ans)}")

    if part2:
        ans = []

        for line in track(
            input, description="Calculating solutions for part 2"
        ):
            i = line.split(" ")
            spring_conditions = (i[0] + "?") * 4 + i[0]
            groups = [int(g) for g in i[1].split(",")] * 5
            log.info(f"Processing: {spring_conditions}, {groups}")
            # num_solutions = lmao(spring_conditions, groups)
            num_solutions = find_first_occurrence_rec(
                spring_conditions, groups
            )
            log.info(f"Number of solutions: {num_solutions}")
            ans.append(num_solutions)

        log.debug(f"Part 2: num solutions: {ans}")
        log.info(f"Part 2: Answer: {sum(ans)}")


if __name__ == "__main__":
    typer.run(main)
