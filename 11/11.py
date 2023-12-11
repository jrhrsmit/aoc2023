import typer
from itertools import combinations


class Node:
    def __init__(self, value, x, y, num=-1):
        self.value = value
        self.num = num
        self.x = x
        self.y = y
        self.x_distance = 1
        self.y_distance = 1


def insert_space_row(
    matrix: list[list[Node]], factor: int
) -> list[list[Node]]:
    for y, row in enumerate(matrix):
        if any([node.value == "#" for node in row]):
            continue
        for node in row:
            node.y_distance *= factor
    return matrix


def transpose(matrix: list[list[Node]]) -> list[list[Node]]:
    t = list(zip(*matrix))
    for row in t:
        for n in row:
            n.x, n.y = n.y, n.x
            n.x_distance, n.y_distance = n.y_distance, n.x_distance

    return [list(row) for row in t]


def insert_space(
    matrix: list[list[Node]], factor: int = 2
) -> list[list[Node]]:
    matrix = insert_space_row(matrix, factor)
    matrix = transpose(matrix)
    matrix = insert_space_row(matrix, factor)
    matrix = transpose(matrix)
    return matrix


def print_matrix(matrix: list[list[Node]]):
    for row in matrix:
        print("".join([node.value for node in row]))


def distance(node1: Node, node2: Node, matrix: list[list[Node]]) -> int:
    d = 0
    for x in range(node1.x, node2.x, 1 if node1.x < node2.x else -1):
        d += matrix[node1.y][x].x_distance
    for y in range(node1.y, node2.y, 1 if node1.y < node2.y else -1):
        d += matrix[y][node2.x].y_distance
    return d


def sum_of_all_distances(
    matrix: list[list[Node]], galaxies: list[Node]
) -> int:
    distances = []
    for node1, node2 in list(combinations(galaxies, 2)):
        distances.append(distance(node1, node2, matrix))
    return sum(distances)


def get_galaxies(matrix: list[list[Node]]) -> list[Node]:
    num = 0
    galaxies = []
    for row in matrix:
        for node in row:
            if node.value == "#":
                galaxies.append(node)
                node.num = num + 1
                num += 1
    return galaxies


def change_space(
    matrix: list[list[Node]], new_distance: int
) -> list[list[Node]]:
    for row in matrix:
        for n in row:
            if n.x_distance > 1:
                n.x_distance = new_distance
            if n.y_distance > 1:
                n.y_distance = new_distance
    return matrix


def main(input_file: typer.FileText):
    input = input_file.read().split("\n")

    matrix = []

    print("Reading input...")
    for y, row in enumerate(input):
        if not row:
            continue
        matrix_row = []
        for x, value in enumerate(row):
            node = Node(value, x, y)
            matrix_row.append(node)
        matrix.append(matrix_row)

    matrix = insert_space(matrix, 2)

    print("Input matrix:")
    print_matrix(matrix)

    galaxies = get_galaxies(matrix)

    print(f"Galaxies: {len(galaxies)}")
    d = sum_of_all_distances(matrix, galaxies)

    print(f"Part 1: {d}")

    matrix = change_space(matrix, 1000000)
    d = sum_of_all_distances(matrix, galaxies)

    print(f"Part 2: {d}")


if __name__ == "__main__":
    typer.run(main)
