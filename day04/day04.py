from typing import Tuple


def contains(pairs: Tuple[Tuple[int, int], Tuple[int, int]]) -> bool:
    a, b = pairs
    return (a[0] >= b[0] and a[1] <= b[1]) or (b[0] >= a[0] and b[1] <= a[1])


def overlaps(pairs: Tuple[Tuple[int, int], Tuple[int, int]]) -> bool:
    a, b = pairs
    return not (a[0] > b[1] or b[0] > a[1])


def day04_2():
    with open('day04input.txt') as f:
        results = [
            x for line in f
            if overlaps(x := tuple([
                tuple(sorted(map(int, r.split('-')))) for r in line.strip().split(',')
            ]))
        ]
    return len(results)


def day04_1():
    with open('day04input.txt') as f:
        results = [
            x for line in f
            if contains(x := tuple([
                tuple(sorted(map(int, r.split('-')))) for r in line.strip().split(',')
            ]))
        ]
    return len(results)


if __name__ == '__main__':
    print(day04_2())
