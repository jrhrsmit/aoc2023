import typer
import math
from itertools import pairwise



def predict(sequence: list[int]) -> int:
    if all([x == 0 for x in sequence]):
        return 0
    else:
        next_sequence = []
        for i in pairwise(sequence):
            next_sequence.append(i[1] - i[0])
        return i[-1] + predict(next_sequence)

def sum_predictions(sequence: list[int]) -> int:
    sum_predictions = 0
    for s in sequence:
        sum_predictions += predict(s)
    return sum_predictions


def main(input_file: typer.FileText):
    input = input_file.read().split("\n")

    sequences = []
    for row in input:
        if row == "":
            continue
        sequence = [int(x) for x in row.split(" ") if x != ""]
        sequences.append(sequence)

    print(f"Part 1: {sum_predictions(sequences)}")

    sequences_reversed = sequences
    for s in sequences_reversed:
        s.reverse()
    print(f"Part 2: {sum_predictions(sequences_reversed)}")


if __name__ == "__main__":
    typer.run(main)
