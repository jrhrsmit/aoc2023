import typer
from typing import TypedDict


class Race:
    def __init__(self, time, record_distance) -> None:
        self.time = time
        self.record_distance = record_distance
        self.num_ways_to_win = 0


def get_races_part_1(input) -> list[Race]:
    for row in input:
        if row.startswith("Time:"):
            times = row.split(" ")[1:]
            times = [int(time) for time in times if time != ""]
        if row.startswith("Distance:"):
            distances = row.split(" ")[1:]
            distances = [int(distance) for distance in distances if distance != ""]

    races = []
    for time, distance in zip(times, distances):
        races.append(Race(time, distance))
    
    return races


def get_races_part_2(input) -> list[Race]:
    for row in input:
        if row.startswith("Time:"):
            time = row.split(":")[1]
            time = time.replace(" ", "")
            time = int(time)
        if row.startswith("Distance:"):
            distance = row.split(":")[1]
            distance = distance.replace(" ", "")
            distance = int(distance)

    races = []
    races.append(Race(time, distance))
    
    return races

def bruteforce_num_ways_to_win(races: list[Race]) -> list[Race]:
    for i, race in enumerate(races):
        for t_button_pressed in range(0, race.time):
            t_left = race.time - t_button_pressed
            speed = t_button_pressed
            distance = speed * t_left
            if distance > race.record_distance:
                race.num_ways_to_win += 1
        print(f"Race {i}: num ways to win: {race.num_ways_to_win}")
    return races

def main(input_file: typer.FileText):
    input = input_file.read().split("\n")

    races = get_races_part_1(input)
    races = bruteforce_num_ways_to_win(races)
    part_1_ans = 1
    for race in races:
        part_1_ans *= race.num_ways_to_win

    print(f"Part 1: {part_1_ans}")

    races = get_races_part_2(input)
    races = bruteforce_num_ways_to_win(races)
    part_2_ans = races[0].num_ways_to_win
    print(f"Part 2: {part_2_ans}")


if __name__ == "__main__":
    typer.run(main)
