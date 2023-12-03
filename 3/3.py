import typer
import re
from typing import TypedDict
from enum import Enum


class Number:
    pass


class Symbol(TypedDict):
    row: int
    column: int
    value: str
    numbers_adjacent: list[Number]


class Number(TypedDict):
    row: int
    column_start: int
    column_end: int
    value: int
    symbol_adjacent: list[Symbol]


def main(input_file: typer.FileText):
    input = input_file.read().split("\n")

    symbols: list[Symbol] = []
    numbers: list[Number] = []

    for row_num, row in enumerate(input):
        row_numbers = re.finditer(r"\d+", row)

        # match all symbols except whitespace, dots, and numbers
        row_symbols = re.finditer(r"[^\s\d\.]", row)

        for match in row_symbols:
            symbols.append(
                {"row": row_num, "column": match.start(), "value": match.group(), "numbers_adjacent": []}
            )

        for match in row_numbers:
            numbers.append(
                {
                    "row": row_num,
                    "column_start": match.start(),
                    "column_end": match.end(),
                    "value": int(match.group()),
                    "symbol_adjacent": [],
                }
            )

    for number in numbers:
        for symbol in symbols:
            if (
                symbol["row"] >= number["row"] - 1
                and symbol["row"] <= number["row"] + 1
                and symbol["column"] >= number["column_start"] - 1
                and symbol["column"] <= number["column_end"]
            ):
                number["symbol_adjacent"].append(symbol)
                symbol["numbers_adjacent"].append(number)

    # for number in numbers:
    #     print(f"Number: {number['value']}")
    #     print(f"Row: {number['row']}")
    #     print(f"Column start: {number['column_start']}")
    #     print(f"Column end: {number['column_end']}")
    #     print(f"Symbols adjacent: {number['symbol_adjacent']}")
    #     print("")

    partnumber_sum = 0
    for number in numbers:
        if number["symbol_adjacent"]:
            partnumber_sum += number["value"]

    print(f"Partnumber sum: {partnumber_sum}")
    print(f"Num symbols: {len(symbols)}")
    unique_symbols = []
    for symbol in symbols:
        if symbol["value"] not in unique_symbols:
            unique_symbols.append(symbol["value"])
    print(f"Unique symbols: {unique_symbols}")
    print(f"Num unique symbols: {len(unique_symbols)}")
    print(f"Num numbers: {len(numbers)}")

    gear_ratio_sum = 0
    for symbol in symbols:
        if symbol["value"] == "*" and len(symbol["numbers_adjacent"]) == 2:
            gear_ratio = (
                symbol["numbers_adjacent"][0]["value"]
                * symbol["numbers_adjacent"][1]["value"]
            )
            gear_ratio_sum += gear_ratio
            # print(
            #     f"Gear ratio of {symbol['numbers_adjacent'][0]['value']} {symbol['numbers_adjacent'][1]['value']}: {gear_ratio}"
            # )
    
    print(f"Gear ratio sum: {gear_ratio_sum}")


if __name__ == "__main__":
    typer.run(main)
