import typer
from typing import TypedDict
from enum import Enum
from functools import cmp_to_key

card_values = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}

card_values_joker = {
    "J": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "Q": 12,
    "K": 13,
    "A": 14,
}


class Hand:
    pass


class HandType(Enum):
    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    FULL_HOUSE = 4
    FOUR_OF_A_KIND = 5
    FIVE_OF_A_KIND = 6


def compare_first_card(hand1: Hand, hand2: Hand) -> int:
    for c1, c2 in zip(hand1.hand, hand2.hand):
        if card_values[c1] > card_values[c2]:
            return 1
        elif card_values[c1] < card_values[c2]:
            return -1
    return 0


def get_hand_type(hand: Hand) -> HandType:
    hand_type = HandType.HIGH_CARD
    print(f"hand: {hand.hand}")
    for card in hand.cards:
        print(f"card: {card}, num: {hand.cards_num[card]}")
        if hand.cards_num[card] == 5:
            return HandType.FIVE_OF_A_KIND
        elif hand.cards_num[card] == 4:
            return HandType.FOUR_OF_A_KIND
        elif hand.cards_num[card] == 3:
            for other_card in hand.cards:
                if hand.cards_num[other_card] == 2 and other_card != card:
                    return HandType.FULL_HOUSE
            return HandType.THREE_OF_A_KIND

    for card in hand.cards:
        if hand.cards_num[card] == 2:
            for other_card in hand.cards:
                if hand.cards_num[other_card] == 2 and other_card != card:
                    return HandType.TWO_PAIR
            return HandType.ONE_PAIR
    return HandType.HIGH_CARD


def compare_hands(hand1: Hand, hand2: Hand) -> int:
    if hand1.hand_type.value > hand2.hand_type.value:
        return 1
    elif hand1.hand_type.value < hand2.hand_type.value:
        return -1
    else:
        return compare_first_card(hand1, hand2)


class Hand:
    def __init__(self, hand: str, bid: int, joker: bool = False):
        self.hand = hand
        self.bid = int(bid)
        self.cards = set(hand)
        self.cards_num = dict()

        joker_key = None
        max_num = 0
        for card in self.cards:
            self.cards_num[card] = hand.count(card)
            if joker:
                if card == "J":
                    continue
                if self.cards_num[card] > max_num:
                    max_num = self.cards_num[card]
                    joker_key = card
                elif self.cards_num[card] == max_num:
                    if card_values[card] > card_values[joker_key]:
                        joker_key = card
        if joker and joker_key and "J" in self.cards:
            self.cards_num[joker_key] += self.cards_num["J"]
            self.cards_num["J"] = 0
        self.hand_type = get_hand_type(self)
        self.rank = -1
        self.winnings = -1


def main(input_file: typer.FileText):
    input = input_file.read().split("\n")
    hands = []

    for line in input:
        if line == "":
            continue
        line = line.split(" ")
        hand = Hand(line[0], line[1])
        hands.append(hand)

    hands.sort(key=cmp_to_key(compare_hands))

    total_winnings = 0
    for rank, hand in enumerate(hands):
        hand.rank = rank + 1
        hand.winnings = hand.bid * hand.rank
        total_winnings += hand.winnings
        print(
            f"Hand: {hand.hand},  bid: {hand.bid}, type: {hand.hand_type}, rank: {hand.rank}, winnings: {hand.winnings}"
        )

    print(f"Part 1 total winnings: {total_winnings}")
    
    hands = []
    global card_values
    global card_values_joker
    card_values = card_values_joker

    for line in input:
        if line == "":
            continue
        line = line.split(" ")
        hand = Hand(line[0], line[1], True)
        hands.append(hand)

    hands.sort(key=cmp_to_key(compare_hands))

    total_winnings = 0
    for rank, hand in enumerate(hands):
        hand.rank = rank + 1
        hand.winnings = hand.bid * hand.rank
        total_winnings += hand.winnings
        print(
            f"Hand: {hand.hand},  bid: {hand.bid}, type: {hand.hand_type}, rank: {hand.rank}, winnings: {hand.winnings}"
        )

    print(f"Part 2 total winnings: {total_winnings}")



if __name__ == "__main__":
    typer.run(main)
