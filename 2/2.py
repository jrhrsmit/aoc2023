import typer
import re

digits = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

def main(input_file: typer.FileText):
    input = input_file.read().split("\n")

    ans = 0
    for i in input:
        res = re.finditer(r"(?=(\d|one|two|three|four|five|six|seven|eight|nine))", i)
        res = [i.group(1) for i in res]
        if res == []:
            continue
        if res[0] in digits:
            res[0] = digits.index(res[0]) + 1
        if res[-1] in digits:
            res[-1] = digits.index(res[-1]) + 1
        print(f"{i=} {res=}")
        num = int(f"{res[0]}{res[-1]}")
        print(f"{num=}")
        ans += num

    print(ans)

if __name__ == "__main__":
    typer.run(main)
