from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Self


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def __add__(self, other: Self) -> Self:
        return Point(self.x + other.x, self.y + other.y)


class Direction(Point, Enum):
    N = 0, -1
    E = 1, 0
    S = 0, 1
    W = -1, 0
    NE = 1, -1
    SE = 1, 1
    SW = -1, 1
    NW = -1, -1


valid_directions = [
    [Direction.N, Direction.NE, Direction.NW],
    [Direction.S, Direction.SE, Direction.SW],
    [Direction.W, Direction.NW, Direction.SW],
    [Direction.E, Direction.NE, Direction.SE]
]


@dataclass()
class Grove:
    elves: set[Point]
    rounds: int = 0

    def __str__(self):
        l, h = self.bounds()
        s = ''
        for y in range(l.y, h.y + 1):
            for x in range(l.x, h.x + 1):
                s += '#' if Point(x, y) in self.elves else '.'
            s += '\n'
        return s

    def empty_ground(self) -> int:
        l, h = self.bounds()
        dx = h.x - l.x + 1
        dy = h.y - l.y + 1
        spaces = dx * dy
        return spaces - len(self.elves)

    def neighbours(self, p: Point) -> set[Direction]:
        return {d for d in Direction if (p + d) in self.elves}

    def bounds(self) -> tuple[Point, Point]:
        if not self.elves:
            return Point(0, 0), Point(0, 0)
        xs = {p.x for p in self.elves}
        ys = {p.y for p in self.elves}
        return Point(min(xs), min(ys)), Point(max(xs), max(ys))

    def do_round(self) -> bool:
        done = True
        moves = defaultdict(list)
        for elf in self.elves:
            neighbours = self.neighbours(elf)
            if neighbours:
                for x in range(4):
                    if not set(vd := valid_directions[(self.rounds + x) % 4]) & neighbours:
                        moves[elf + vd[0]].append(elf)
                        break
        for move, elves in moves.items():
            if len(elves) == 1:
                done = False
                self.elves.remove(elves[0])
                self.elves.add(move)
        self.rounds += 1
        # print(f'== End of Round {self.rounds} ==')
        # print(self)
        # print()
        return done


def parse_grove(filename: str) -> Grove:
    with open(filename) as f:
        file = f.readlines()
        f.close()
    points = {
        Point(x, y)
        for y, line in enumerate(file)
        for x, c in enumerate(line.strip('\n'))
        if c == '#'
    }
    return Grove(points)


if __name__ == '__main__':
    sample_grid = parse_grove('sample.txt')
    input_grid = parse_grove('input.txt')
    # print('== Initial State ==')
    # print(sample_grid)
    # print()
    for x in range(10):
        sample_grid.do_round()
        input_grid.do_round()
    p1s = sample_grid.empty_ground()
    p1i = input_grid.empty_ground()
    print(f'Part 1 sample: {p1s}')
    print(f'Part 1 input: {p1i}')
    assert p1s == 110
    assert p1i == 4172

    while True:
        if sample_grid.do_round():
            break
    p2s = sample_grid.rounds
    print(f'Part 2 sample: {p2s}')

    while True:
        if input_grid.do_round():
            break
    p2i = input_grid.rounds

    print(f'Part 2 input: {p2i}')
    assert p2s == 20
    assert p2i == 942
