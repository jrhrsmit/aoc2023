import typer
from enum import Enum


class Direction(Enum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4


def get_opposite_direction(direction: Direction):
    if direction == Direction.NORTH:
        return Direction.SOUTH
    elif direction == Direction.SOUTH:
        return Direction.NORTH
    elif direction == Direction.WEST:
        return Direction.EAST
    elif direction == Direction.EAST:
        return Direction.WEST
    else:
        raise Exception(f"Unknown direction: {direction}")


def get_coordinates_in_direction(x: int, y: int, direction: Direction):
    if direction == Direction.NORTH:
        return x, y - 1
    elif direction == Direction.SOUTH:
        return x, y + 1
    elif direction == Direction.WEST:
        return x - 1, y
    elif direction == Direction.EAST:
        return x + 1, y
    else:
        raise Exception(f"Unknown direction: {direction}")


class Node:
    pass


class Node:
    def NodeType(enum):
        LOOP: 1
        LEFT: 2
        RIGHT: 3

    def connect(self, other: Node, direction: Direction) -> bool:
        direction_reverse = get_opposite_direction(direction)
        if (
            direction in self.can_connect
            and direction_reverse in other.can_connect
        ):
            if other not in self.connected:
                self.connected.append(other)
            if other not in self.connected:
                other.connected.append(self)
            return True
        return False

    def connect_in_matrix(
        self,
        matrix: list[list[Node]],
        tgt_x: int,
        tgt_y: int,
        direction: Direction,
    ):
        try:
            self.connect(matrix[tgt_y][tgt_x], direction)
        except IndexError:
            pass

    def connect_direction(self, matrix: list[list[Node]]):
        for direction in self.can_connect:
            self.connect_in_matrix(
                matrix,
                *get_coordinates_in_direction(self.x, self.y, direction),
                direction,
            )

    def __init__(self, value: str, x: int, y: int):
        self.value = value
        if value == ".":
            self.can_connect = []
        elif value == "|":
            self.can_connect = [Direction.SOUTH, Direction.NORTH]
        elif value == "-":
            self.can_connect = [Direction.WEST, Direction.EAST]
        elif value == "F":
            self.can_connect = [Direction.SOUTH, Direction.EAST]
        elif value == "J":
            self.can_connect = [Direction.NORTH, Direction.WEST]
        elif value == "7":
            self.can_connect = [Direction.SOUTH, Direction.WEST]
        elif value == "S":
            self.can_connect = [
                Direction.NORTH,
                Direction.EAST,
                Direction.SOUTH,
                Direction.WEST,
            ]
        elif value == "L":
            self.can_connect = [Direction.NORTH, Direction.EAST]
        else:
            raise Exception(f"Unknown node value: {value}")
        self.x = x
        self.y = y
        self.connected = []
        self.type = None
        self.side = None


def find_connected_nodes(start: Node, matrix: list[list[Node]]):
    connected = []
    queue = start.connected.copy()
    while len(queue) > 0:
        n = queue.pop(0)
        if n not in connected:
            connected.append(n)
            queue.extend(n.connected)
    return connected


def get_adjacent_nodes(node: Node, matrix: list[list[Node]]):
    adjacent = []
    for direction in Direction:
        x, y = get_coordinates_in_direction(node.x, node.y, direction)
        try:
            adjacent.append(matrix[y][x])
        except IndexError:
            pass
    return adjacent


def node_in_list(node: Node, l: list[Node]):
    for n in l:
        if n.x == node.x and n.y == node.y:
            return True
    return False


def print_matrix_sides(
    matrix: list[list[Node]],
    left: list[Node],
    right: list[Node],
    loop: list[Node],
):
    i = 0
    o = 0
    for row in matrix:
        for node in row:
            if node_in_list(node, loop):
                if node.value == "7":
                    print("┐", end="")
                elif node.value == "J":
                    print("┘", end="")
                elif node.value == "F":
                    print("┌", end="")
                elif node.value == "L":
                    print("└", end="")
                elif node.value == "|":
                    print("│", end="")
                elif node.value == "-":
                    print("─", end="")
                else:
                    print(node.value, end="")
            elif node_in_list(node, left):
                print("O", end="")
                o += 1
            elif node_in_list(node, right):
                print("I", end="")
                i += 1
            else:
                print(".", end="")
        print()

    print(f"Num I: {i}, Num O: {o}")


def get_node_in_matrix(x: int, y: int, matrix: list[list[Node]]):
    try:
        return matrix[y][x]
    except IndexError:
        return None


def get_right_nodes(node: Node, prev_node: Node, matrix: list[list[Node]]):
    right = []
    if node.x < prev_node.x and node.y == prev_node.y:
        right.append(get_node_in_matrix(node.x, node.y - 1, matrix))
        right.append(get_node_in_matrix(prev_node.x, node.y - 1, matrix))
    elif node.x > prev_node.x and node.y == prev_node.y:
        right.append(get_node_in_matrix(node.x, node.y + 1, matrix))
        right.append(get_node_in_matrix(prev_node.x, node.y + 1, matrix))
    elif node.y < prev_node.y and node.x == prev_node.x:
        right.append(get_node_in_matrix(node.x + 1, node.y, matrix))
        right.append(get_node_in_matrix(node.x + 1, prev_node.y, matrix))
    elif node.y > prev_node.y and node.x == prev_node.x:
        right.append(get_node_in_matrix(node.x - 1, node.y, matrix))
        right.append(get_node_in_matrix(node.x - 1, prev_node.y, matrix))
    else:
        raise Exception(
            f"Unknown direction, from x: {prev_node.x}, y: {prev_node.y} to x: {node.x}, y: {node.y}"
        )
    return right


def find_sides(loop: list[Node], matrix: list[list[Node]]):
    side_left = []
    side_right = []
    start_node = loop[0]

    prev_node = start_node
    current_node = start_node.connected[1]

    while current_node != start_node:
        r = get_right_nodes(current_node, prev_node, matrix)
        for n in r:
            if n not in loop and n not in side_right:
                side_right.append(n)

        next_node = (
            current_node.connected[0]
            if current_node.connected[0] != prev_node
            else current_node.connected[1]
        )
        prev_node = current_node
        current_node = next_node

    print_matrix_sides(matrix, side_left, side_right, loop)

    queue = side_right.copy()
    processed = []
    while len(queue) > 0:
        node = queue.pop(0)
        adjacent = get_adjacent_nodes(node, matrix)
        for a in adjacent:
            if a in loop or a in processed:
                continue
            elif a in side_left:
                raise Exception("Node in both sides")
            side_right.append(a)
            queue.append(a)
            processed.append(node)

    print_matrix_sides(matrix, side_left, side_right, loop)


def main(input_file: typer.FileText):
    input = input_file.read().split("\n")

    nodes = []
    node_matrix = []

    print("Reading input...")
    for y, row in enumerate(input):
        node_row = []
        for x, value in enumerate(row):
            node = Node(value, x, y)
            if value != ".":
                nodes.append(node)
            node_row.append(node)
        node_matrix.append(node_row)

    print("Connecting nodes...")
    start_node = None
    for row in node_matrix:
        for node in row:
            if node.value == "S":
                start_node = node
            node.connect_direction(node_matrix)

    print("Finding connected nodes in loop...")
    loop = find_connected_nodes(start_node, node_matrix)
    print(f"Part 1: Farthest node distance: {len(loop) //2}")


    print("Finding sides...")
    find_sides(loop, node_matrix)


if __name__ == "__main__":
    typer.run(main)
