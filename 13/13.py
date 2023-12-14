import typer
from itertools import combinations, groupby


def print_matrix(matrix: list[str], title: str | None = None, details: bool =
                 False) -> None:
    if title:
        print(title)
    if details:
        print(f"Rows: {len(matrix)}, Columns: {len(matrix[0])}")
    if details:
        for i, row in enumerate(matrix):
            print(f"{row} {i}")
    else:
        for row in matrix:
            print(row)

    print()


def transpose(matrix: list[str]) -> list[str]:
    t = list(zip(*matrix))
    return ["".join(row) for row in t]


def find_reflection(pattern: list[str]) -> int | None:
    for r in range(1, len(pattern)):
        side_a = pattern[:r]
        side_b = pattern[r:]
        side_a = side_a[-len(side_b) :]
        side_b = side_b[: len(side_a)]
        side_b.reverse()
        # print_matrix(side_a, "Side A:", True)
        # print_matrix(side_b, "Side B:", True)
        if side_a == side_b:
            return r
    return None


def find_reflection_with_smudge(pattern: list[str]) -> int | None:
    for r in range(1, len(pattern)):
        side_a = pattern[:r]
        side_b = pattern[r:]
        side_a = side_a[-len(side_b) :]
        side_b = side_b[: len(side_a)]
        side_b.reverse()
        inequalities = 0
        for row_a, row_b in zip(side_a, side_b):
            inequalities += sum(a != b for a, b in zip(row_a, row_b))
            if inequalities > 1:
                break
        if inequalities == 1:
            #print_matrix(side_a, "Side A:", True)
            #print_matrix(side_a, "Side B:", True)
            return r
    return None

def calc_magic_sum_for_patterns(patterns: list[list[str]], fn) -> int:
    sum = 0
    for pattern in patterns:
        # print_matrix(pattern, "Finding reflection for pattern:")
        reflection = fn(pattern)
        if reflection:
            print(f"Reflection found on row {reflection}")
            sum += reflection * 100
            continue
        reflection = fn(transpose(pattern))
        if reflection:
            print(f"Reflection found on column {reflection}")
            sum += reflection
            continue
        raise "Reflection not found"
    return sum


def main(input_file: typer.FileText):
    input = input_file.read().strip().split("\n")
    patterns = [list(g) for k, g in groupby(input, key=bool) if k]
    
    sum = calc_magic_sum_for_patterns(patterns, find_reflection)
    print(f"Part 1: Sum: {sum}")
    
    sum = calc_magic_sum_for_patterns(patterns, find_reflection_with_smudge)
    print(f"Part 2: Sum: {sum}")


if __name__ == "__main__":
    typer.run(main)
