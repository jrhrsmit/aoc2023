import typer


class Card:
    winning: list[int]
    numbers: list[int]
    num_winning: int
    score: int
    copies: int = 0


def main(input_file: typer.FileText):
    input = input_file.read().split("\n")

    # assume that the last card is on the last line
    num_cards = int(input[-1].split(":")[0].split(" ")[-1])

    cards = [Card() for _ in range(num_cards)]

    total_score = 0

    for row in input:
        info = row.split(":")
        card_info = info[0]
        numbers_info = info[1].split("|")

        card_num = int(card_info.strip().split(" ")[-1]) - 1
        card = cards[card_num]

        card.winning = [int(x) for x in numbers_info[0].split(" ") if x]
        card.numbers = [int(x) for x in numbers_info[1].split(" ") if x]

        card.num_winning = len([x for x in card.numbers if x in card.winning])
        card.score = 2 ** (card.num_winning - 1) if card.num_winning > 0 else 0

        cards[card_num] = card

        # print(
        #     f"Card {card_num+1}: {card.winning=}, {card.numbers=}, {card.num_winning=}, {card.score=}, {card.copies=}"
        # )

        for idx in range(card_num + 1, card_num + card.num_winning + 1):
            cards[idx].copies += card.copies + 1

        total_score += card.score

    print("Part 1:")
    print(f"{total_score=}")

    print("Part 2:")
    total_num_cards = len(cards) + sum([c.copies for c in cards])
    print(f"{total_num_cards=}")


if __name__ == "__main__":
    typer.run(main)
