from __future__ import annotations
from dataclasses import dataclass
from itertools import takewhile
from typing import List, TypeVar, Generic, Tuple, Callable

from more_itertools import partition, flatten

T = TypeVar("T")
U = TypeVar("U")

@dataclass
class Grid(Generic[T]):
    grid: List[List[T]]
    height: int
    width: int
    cell_type: str

    def __init__(self, grid: List[List[T]]):
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])
        self.cell_type = type(grid[0][0])

    def get_cell(self, x: int, y: int) -> T:
        return self.grid[y][x]

    def get_between(self, x: int, y: int) -> Tuple[List[T], List[T], List[T], List[T]]:
        a, b = map(lambda loi: [self.get_cell(x, i) for i in loi],
                   partition(y.__lt__, [i for i in range(self.height) if i != y]))
        l, r = map(lambda loj: [self.get_cell(j, y) for j in loj],
                   partition(x.__lt__, [j for j in range(self.width) if j != x]))
        return list(reversed(a)), b, list(reversed(l)), r

    def get_all_cells(self) -> List[T]:
        return flatten(self.grid)

    def __repr__(self):
        return f'Grid(type={self.cell_type}, height={self.height}, width={self.width})'

    def to_mls(self):
        pad = max([len(str(c)) for c in self.get_all_cells()])
        strings = [' '.join([f'{str(c):{pad}}' for c in row]) for row in self.grid]
        return '\n'.join(strings)

    def grid_map(self, f: Callable[[Grid[T], int, int], U]) -> Grid[U]:
        return Grid(
            [[f(self, x, y) for x in range(self.height)] for y in range(self.height)]
        )


def get_grid() -> Grid:
    with open('day08input.txt') as f:
        grid = Grid([[int(c) for c in line.strip()] for line in f])
    return grid


def is_visible(grid: Grid, x: int, y: int) -> bool:
    cell = grid.get_cell(x, y)
    for direction in grid.get_between(x, y):
        if not any([tree >= cell for tree in direction]):
            return True
    return False


def view_score(grid: Grid, x: int, y: int) -> int:
    score = 1
    cell = grid.get_cell(x, y)
    directions = grid.get_between(x, y)
    if not all(directions):
        return 0
    for direction in directions:
        visible_trees = []
        for c in direction:
            visible_trees.append(c)
            if c >= cell:
                break
        if not visible_trees:
            return 0
        score *= len(visible_trees)
    return score


def day08_1():
    grid = get_grid()
    visible_grid = grid.grid_map(is_visible)
    printable_grid = visible_grid.grid_map(lambda g, x, y: 'T' if g.get_cell(x, y) else 'F')
    print(printable_grid.to_mls())
    return len(list(filter(None, visible_grid.get_all_cells())))


def day08_2():
    grid = get_grid()
    scored_grid = grid.grid_map(view_score)
    print(scored_grid.to_mls())
    return max(scored_grid.get_all_cells())


if __name__ == '__main__':
    print(day08_2())
