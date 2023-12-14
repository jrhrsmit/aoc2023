import typer
from itertools import combinations, groupby


def transpose(matrix: list[str]) -> list[str]:
    t = list(zip(*matrix))
    return ["".join(row) for row in t]


def rotate_right(matrix: list[str]) -> list[str]:
    return transpose(matrix[::-1])


def rotate_left(matrix: list[str]) -> list[str]:
    return transpose(matrix)[::-1]


def tilt_west(matrix: list[str]) -> list[str]:
    new_matrix = []
    for row in matrix:
        rock = 0
        new_row = ""

        row_rocks = row.split("#")
        for i, part in enumerate(row.split("#")):
            if i > 0:
                new_row += "#"
            new_row += "".join([c for c in part if c == "O"])
            new_row += "".join([c for c in part if c == "."])

        new_matrix.append(new_row)
    return new_matrix


def tilt_north(matrix: list[str]) -> list[str]:
    matrix = rotate_left(matrix)
    matrix = tilt_west(matrix)
    matrix = rotate_right(matrix)
    return matrix


def tilt_east(matrix: list[str]) -> list[str]:
    matrix = rotate_left(rotate_left(matrix))
    matrix = tilt_west(matrix)
    matrix = rotate_right(rotate_right(matrix))
    return matrix


def tilt_south(matrix: list[str]) -> list[str]:
    matrix = rotate_right(matrix)
    matrix = tilt_west(matrix)
    matrix = rotate_left(matrix)
    return matrix


def get_load(matrix: list[str]) -> int:
    return sum(
        [row.count("O") * (i + 1) for i, row in enumerate(reversed(matrix))]
    )


def print_matrix(matrix: list[str]) -> None:
    for row in matrix:
        print(row)


def cycle_matrix(matrix: list[str]) -> int:
    matrix = tilt_north(matrix)
    matrix = tilt_west(matrix)
    matrix = tilt_south(matrix)
    matrix = tilt_east(matrix)
    return matrix


def find_offset_period(matrix: list[str]) -> int:
    seen = []
    seen.append(hash(tuple(matrix)))
    while True:
        matrix = cycle_matrix(matrix)
        h = hash(tuple(matrix))
        if h in seen:
            return (seen.index(h), len(seen) - seen.index(h))
        seen.append(h)


def main(input_file: typer.FileText):
    dish = input_file.read().strip().split("\n")

    print_matrix(dish)
    print()
    d = tilt_north(dish)
    print_matrix(d)

    print(f"Part 1: load: {get_load(d)}")

    offset, period = find_offset_period(dish)
    print(f"offset: {offset}, period: {period}")
    
    d = dish
    print(f"Cycling for {offset} times")
    for _ in range(offset):
        d = cycle_matrix(d)

    print(f"Cycling for {(1000000000 - offset) % period} times")
    for _ in range((1000000000 - offset) % period):
        d = cycle_matrix(d)

    print("Final state:")
    print_matrix(d)

    print(f"Part 2: load: {get_load(d)}")


if __name__ == "__main__":
    typer.run(main)
