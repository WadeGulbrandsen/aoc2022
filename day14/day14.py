from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from itertools import starmap
from operator import add, attrgetter
from typing import TypeVar, Generic, Optional, NamedTuple

from more_itertools import flatten, first

T = TypeVar("T")
U = TypeVar("U")

rock_pattern = re.compile(r'(?P<x>\d+),(?P<y>\d+)')


class Point(NamedTuple):
    x: int
    y: int

    @staticmethod
    def fill(a: Point, b: Point) -> list[Point]:
        x_range = range(*starmap(add, enumerate(sorted((a.x, b.x)))))
        y_range = range(*starmap(add, enumerate(sorted((a.y, b.y)))))
        return [Point(x, y) for x in x_range for y in y_range]


class Vector(Point):
    def move(self, p: Point) -> Point:
        return Point(p.x + self.x, p.y + self.y)


@dataclass
class Grid(Generic[T]):
    grid: list[list[T]]
    height: int
    width: int
    cell_type: str

    def __init__(self, grid: list[list[T]]):
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])
        self.cell_type = type(grid[0][0])

    def __repr__(self):
        return f'Grid(type={self.cell_type}, height={self.height}, width={self.width})'

    def get_cell(self, p: Point) -> str:
        return self.grid[p.y][p.x]

    def get_all_cells(self) -> list[str]:
        return flatten(self.grid)

    def grid_map(self, f: Callable[[Grid[T], Point], U]) -> Grid[U]:
        return Grid(
            [[f(self, Point(x, y)) for x in range(self.width)] for y in range(self.height)]
        )

    def to_mls(self):
        pad = max([len(str(c)) for c in self.get_all_cells()])
        strings = [' '.join([f'{str(c):{pad}}' for c in row]) for row in self.grid]
        return '\n'.join(strings)

    def in_bounds(self, p: Point) -> bool:
        return (0 <= p.x < self.width) and (0 <= p.y < self.height)

    def neighbours(self, p: Point, diagonals: bool = False) -> list[Point]:
        directions = [Vector(0, 1), Vector(0, -1), Vector(1, 0), Vector(-1, 0)]
        if diagonals:
            directions.extend([Vector(1, 1), Vector(1, -1), Vector(-1, 1), Vector(-1, -1)])
        neighbours = [n for v in directions if self.in_bounds(n := v.move(p))]
        return neighbours

    def point_to_index(self, p: Point) -> int:
        return (p.y * self.width) + p.x

    def index_to_point(self, i: str) -> Point:
        y, x = divmod(i, self.width)
        return Point(x, y)


def get_rocks() -> set[Point]:
    rocks = set()
    with open('day14.txt') as f:
        rock_paths = [[Point(*map(int, p.groupdict().values())) for p in rock_pattern.finditer(line)] for line in f]
        for path in rock_paths:
            rock_points = list(map(Point.fill, path[:-1], path[1:]))
            rocks.update(flatten(rock_points))
    return rocks


def draw_cave(source: Point, rocks: set[Point], sand: set[Point], overflow: set[Point]):
    def __get_char(p: Point) -> str:
        if p in sand:
            return 'o'
        if p == source:
            return '+'
        if p in rocks:
            return '#'
        if p in overflow:
            return '~'
        return '.'
    all_points = {source} | rocks | sand | overflow
    xs, ys = zip(*all_points)
    x_range = range(min(xs), max(xs) + 1)
    y_range = range(min(ys), max(ys) + 1)
    lines = [''.join([__get_char(Point(x, y)) for x in x_range]) for y in y_range]
    print('\n'.join(lines))


def draw_cave_with_floor(source: Point, rocks: set[Point], sand: set[Point]):
    def __get_char(p: Point) -> str:
        if p in sand:
            return 'o'
        if p == source:
            return '+'
        if p in all_rocks:
            return '#'
        return '.'
    y_max = max(map(attrgetter('y'), rocks)) + 2
    all_points = {source} | rocks | sand
    xs, ys = zip(*all_points)
    x_range = range(min(xs) - 2, max(xs) + 3)
    y_range = range(min(ys), y_max + 1)
    all_rocks = {Point(x, y_max) for x in x_range} | rocks
    lines = [''.join([__get_char(Point(x, y)) for x in x_range]) for y in y_range]
    print('\n'.join(lines))


def drop_sand(source: Point, rocks: set[Point], sand: set[Point]) -> tuple[Optional[Point], set[Point]]:
    def __next_point(c: Point) -> Optional[Point]:
        potential_points = [
            new_point for x in [c.x, c.x - 1, c.x + 1]
            if (new_point := Point(x, c.y + 1)) not in all_points
        ]
        return first(potential_points, None)

    all_points = {source} | rocks | sand
    _xs, ys = zip(*all_points)
    y_max = max(ys) + 3
    path = {source}
    current = source
    while next_point := __next_point(current):
        path.add(next_point)
        if next_point.y > y_max:
            return None, path
        current = next_point

    return current, set()


def drop_sand_to_the_floor(source: Point, rocks: set[Point], sand: set[Point]) -> Point:
    def __next_point(c: Point) -> Optional[Point]:
        if c.y >= y_max:
            return None
        potential_points = [
            new_point for x in [c.x, c.x - 1, c.x + 1]
            if (new_point := Point(x, c.y + 1)) not in all_points
        ]
        return first(potential_points, None)

    all_points = {source} | rocks | sand
    _xs, ys = zip(*rocks)
    y_max = max(ys) + 1
    current = source
    while next_point := __next_point(current):
        current = next_point

    return current


def day14_1():
    source = Point(500, 0)
    rocks = get_rocks()
    sand: set[Point] = set()
    overflow: set[Point] = set()
    print('=== Start ===')
    draw_cave(source, rocks, sand, overflow)
    print()
    unit = 0
    while True:
        p, overflow = drop_sand(source, rocks, sand)
        if overflow:
            break
        if p:
            sand.add(p)
        unit += 1
        print(f'=== Unit {unit:03d} ===')
        draw_cave(source, rocks, sand, overflow)
        print()

    print(f'=== Overflow ===')
    draw_cave(source, rocks, sand, overflow)
    print()
    return unit


def day14_2():
    source = Point(500, 0)
    rocks = get_rocks()
    sand: set[Point] = set()
    print('=== Start ===')
    draw_cave_with_floor(source, rocks, sand)
    print()
    unit = 0
    while True:
        p = drop_sand_to_the_floor(source, rocks, sand)
        sand.add(p)
        unit += 1
        if p == source:
            break
        # print(f'=== Unit {unit:03d} ===')
        # draw_cave_with_floor(source, rocks, sand)
        # print()

    print(f'=== Full ===')
    draw_cave_with_floor(source, rocks, sand)
    print()
    return unit


if __name__ == '__main__':
    print(day14_2())
