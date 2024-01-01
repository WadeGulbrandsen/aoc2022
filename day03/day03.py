from functools import reduce
from itertools import chain
from typing import Tuple, Set

from more_itertools import chunked


def halve(pack: str) -> Tuple[str, str]:
    mid = len(pack) // 2
    return pack[:mid], pack[mid:]


def common_chars(str1: str, str2: str) -> Set[str]:
    common = set(str1) & set(str2)
    return common


def char_to_priority(char: str) -> int:
    if char.isupper():
        return ord(char) - 38
    else:
        return ord(char) - 96


def day03_2():
    results = []
    with open('day03input.txt') as f:
        for lines in chunked(f, 3):
            sets = [set(line.strip()) for line in lines]
            results.append(reduce(lambda x, y: x & y, sets))
    return sum(map(char_to_priority, chain.from_iterable(results)))


def day03_1():
    results = []
    with open('day03input.txt') as f:
        for line in f:
            results.append(common_chars(*halve(line.strip())))
    return sum(map(char_to_priority, chain.from_iterable(results)))


if __name__ == '__main__':
    print(day03_2())
