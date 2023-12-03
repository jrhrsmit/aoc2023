import typer
import re

def main(input_file: typer.FileText):
    input = input_file.read().split("\n")

    ans = 0
    for i in input:
        res = re.findall("\d", i)
        if res == []:
            continue
        print(f"{i=} {res=}")
        num = int(f"{res[0]}{res[-1]}")
        print(f"{num=}")
        ans += num

    print(ans)

if __name__ == "__main__":
    typer.run(main)
