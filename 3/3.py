import typer
import re
from typing import TypedDict
from enum import Enum


class Set(TypedDict):
    red: int
    green: int
    blue: int


class Game(TypedDict):
    game: int
    sets: list[Set]

def is_possible(game: Game, bag: Set):
    for s in game["sets"]:
        if s["red"] > bag["red"] or s["green"] > bag["green"] or s["blue"] > bag["blue"]:
            return False 
    return True 

def maximum(game: Game) -> Set:
    max: Set = {"red": 0, "green": 0, "blue": 0}
    for s in game["sets"]:
        if s["red"] > max["red"]:
            max["red"] = s["red"]
        if s["green"] > max["green"]:
            max["green"] = s["green"]
        if s["blue"] > max["blue"]:
            max["blue"] = s["blue"]
    return max

def power(s: Set) -> int:
    return s["red"] * s["green"] * s["blue"]


def main(input_file: typer.FileText):
    input = input_file.read().split("\n")
    bag: Set = {"red": 12, "green": 13, "blue": 14}

    games : list[Game] = []
    for i in input:
        game = int(re.findall(r"\d+", i)[0])
        details = i.split(":")[1]
        sets = []
        for j in details.split(";"):
            s: Set = {"red": 0, "green": 0, "blue": 0}
            for k in j.split(","):
                num = int(re.findall(r"\d+", k)[0])
                color = re.findall(r"red|green|blue", k)[0]
                print(f"{game=} {num=} {color=}")
                s[color] = num
            sets.append(s)
        games.append(Game(game=game, sets=sets))
    print(f"{games=}")

    sum = 0
    sum_power = 0
    for g in games:
        if is_possible(g, bag):
            print(f"{g['game']=}")
            sum += g["game"]
        sum_power += power(maximum(g))
    print(f"{sum=}")
    print(f"{sum_power=}")



if __name__ == "__main__":
    typer.run(main)
