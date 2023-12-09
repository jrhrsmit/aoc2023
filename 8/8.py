import typer
import math


def part1(nodes, instructions):
    current_node = "AAA"
    instructions_traversed = 0
    if "AAA" not in nodes:
        return
    while True:
        for instruction in instructions:
            current_node = nodes[current_node][instruction]
            instructions_traversed += 1
            if current_node == "ZZZ":
                break
        if current_node == "ZZZ":
            break

    print(f"Part 1: instructions traversed: {instructions_traversed}")


def part2(nodes, instructions):
    current_nodes = [node for node in nodes if node.endswith("A")]
    periods = []
    for current_node in current_nodes:
        instructions_traversed = 0
        period = None
        while True:
            for instruction in instructions:
                current_node = nodes[current_node][instruction]
                instructions_traversed += 1
                if current_node.endswith("Z"):
                    periods.append(instructions_traversed)
                    break
            if current_node.endswith("Z"):
                break

    gcd = math.gcd(*periods)
    periods = [p // gcd for p in periods]
    product = math.prod(periods)
    instructions_traversed = product * gcd
    print(f"Part2: {instructions_traversed}")


def main(input_file: typer.FileText):
    input = input_file.read().split("\n")

    nodes = {}
    instructions = ""
    for row in input:
        if row == "":
            continue
        elif "=" in row:
            values = row.split("=")
            name = values[0].strip()
            directions = values[1].strip("(), ").split(", ")
            left = directions[0]
            right = directions[1]
            nodes[name] = {"L": directions[0], "R": directions[1]}
        else:
            instructions = row.strip()

    part1(nodes, instructions)
    part2(nodes, instructions)


if __name__ == "__main__":
    typer.run(main)
