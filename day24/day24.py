import math
from dataclasses import dataclass
from enum import Enum, IntFlag
from functools import reduce
from heapq import heappush, heappop
from typing import Self

import numpy as np


class Tile(IntFlag):
    F = 0  # Free   '.'
    X = 1  # Wall   '#'
    N = 2  # Up     '^'
    E = 4  # Right  '>'
    S = 8  # Down   'v'
    W = 16  # Left   '<'


StringToTile = {
    '.': Tile.F,
    '#': Tile.X,
    '^': Tile.N,
    '>': Tile.E,
    'v': Tile.S,
    '<': Tile.W,
}

TileToString = {v: k for k, v in StringToTile.items()}


@dataclass(frozen=True, order=True)
class Point:
    x: int
    y: int

    def __add__(self, other: Self) -> Self:
        return Point(self.x + other.x, self.y + other.y)

    def distance(self, other: Self) -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)


class Move(Point, Enum):
    NORTH = 0, -1
    EAST = 1, 0
    SOUTH = 0, 1
    WEST = -1, 0
    WAIT = 0, 0


@dataclass()
class Grove:
    grove: np.ndarray
    size: Point
    wind_maps: list[np.ndarray]

    def __init__(self, arr: np.ndarray):
        self.size = Point(arr.shape[1], arr.shape[0])
        top = arr[0][1:-1]
        bottom = arr[-1][1:-1]
        left = arr[:, [0]]
        right = arr[:, [-1]]
        wind = arr[1:-1, 1:-1]
        north, east, south, west = [
            np.ma.filled(np.ma.masked_not_equal(wind, d, copy=True), 0)
            for d in [Tile.N, Tile.E, Tile.S, Tile.W]
        ]
        self.wind_maps = []
        for x in range(math.lcm(self.size.x - 2, self.size.y - 2)):
            winds = reduce(np.bitwise_or, [north, east, south, west])
            stacked = np.hstack([left, np.vstack([top, winds, bottom]), right])
            self.wind_maps.append(stacked)
            north = np.vstack([north[1:], north[:1]])
            east = np.hstack([east[:, -1:], east[:, :-1]])
            south = np.vstack([south[-1:], south[:-1]])
            west = np.hstack([west[:, 1:], west[:, :1]])
        self.grove = arr

    def str_for(self, minute: int) -> str:
        s = ''
        wind_map = self.wind_maps[minute % len(self.wind_maps)]
        for row in wind_map:
            for x in row:
                ts = [t for t in Tile if t & x]
                if len(ts) == 1:
                    s += TileToString[ts[0]]
                elif len(ts) > 1:
                    s += str(len(ts))
                else:
                    s += '.'
            s += '\n'
        return s

    def __str__(self):
        return self.str_for(0)

    def in_bounds(self, p: Point) -> bool:
        return 0 <= p.x < self.size.x and 0 <= p.y < self.size.y

    def valid_move(self, p: Point, wind_map: np.ndarray) -> bool:
        return self.in_bounds(p) and wind_map[p.y, p.x] == Tile.F

    def moves(self, p: Point, minute: int) -> list[Point]:
        wind_map = self.wind_maps[minute % len(self.wind_maps)]
        return [x for m in Move if self.valid_move(x := p + m, wind_map)]


def find_shortest_path(g: Grove, source: Point, target: Point, time: int) -> int:
    pq = []
    heappush(pq, (target.distance(source) + time, time, source))
    seen = {(time, source)}
    while pq:
        _, minute, current = heappop(pq)
        if current == target:
            return minute - 1
        for p in g.moves(current, minute):
            if (minute + 1, p) not in seen:
                seen.add((minute + 1, p))
                heappush(pq, (target.distance(p) + minute + 1, minute + 1, p))
    return 0


def parse_array(filename: str) -> Grove:
    with open(filename) as f:
        file = f.readlines()
        f.close()
    a = []
    for line in file:
        r = []
        for c in line.strip('\n'):
            r.append(StringToTile[c])
        a.append(r)
    arr = np.array(a, dtype=np.uint8)
    return Grove(arr)


if __name__ == '__main__':
    start = Point(1, 0)
    sample_grove = parse_array("sample2.txt")
    sample_goal = Point(sample_grove.size.x - 2, sample_grove.size.y - 1)
    sample_path = find_shortest_path(sample_grove, start, sample_goal, 0)
    print(f'Part 1 sample: {sample_path}')
    assert sample_path == 18
    return_to_start_sample = find_shortest_path(sample_grove, sample_goal, start, sample_path)
    return_to_goal_sample = find_shortest_path(sample_grove, start, sample_goal, return_to_start_sample)
    print(f'Part 2 sample: {return_to_goal_sample}')
    assert return_to_goal_sample == 54

    input_grove = parse_array("input.txt")
    input_goal = Point(input_grove.size.x - 2, input_grove.size.y - 1)
    input_path = find_shortest_path(input_grove, start, input_goal, 0)
    print(f'Part 1 input: {input_path}')
    assert input_path == 308
    return_to_start_input = find_shortest_path(input_grove, input_goal, start, input_path)
    return_to_goal_input = find_shortest_path(input_grove, start, input_goal, return_to_start_input)
    print(f'Part 2 input: {return_to_goal_input}')
    assert return_to_goal_input == 908
