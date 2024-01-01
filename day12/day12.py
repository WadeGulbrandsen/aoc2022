from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import List, NamedTuple, Tuple, Callable, TypeVar, Generic, Set, Dict

from more_itertools import partition, flatten

T = TypeVar("T")
U = TypeVar("U")


class Point(NamedTuple):
    x: int
    y: int


class Vector(Point):
    def move(self, p: Point) -> Point:
        return Point(p.x + self.x, p.y + self.y)


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

    def __repr__(self):
        return f'Grid(type={self.cell_type}, height={self.height}, width={self.width})'

    def get_cell(self, p: Point) -> str:
        return self.grid[p.y][p.x]

    def get_all_cells(self) -> List[str]:
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

    def neighbours(self, p: Point, diagonals: bool = False) -> List[Point]:
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


class HeightMap(Grid[str]):
    start: Point
    end: Point

    def __init__(self, grid: List[List[T]]):
        super().__init__(grid)
        start, end = None, None
        points = (Point(x, y) for y in range(self.height) for x in range(self.width))
        for p in points:
            if (c := self.get_cell(p)) in 'SE':
                if c == 'S':
                    start = p
                else:
                    end = p
                if start and end:
                    break
        self.start = start
        self.end = end

    def __repr__(self):
        return f'HeightMap(height={self.height}, width={self.width})'

    @staticmethod
    def height_to_int(h: str) -> int:
        if h == 'S':
            h = 'a'
        elif h == 'E':
            h = 'z'
        return ord(h) - 97

    def get_cell_height(self, p: Point) -> int:
        return self.height_to_int(self.get_cell(p))

    def valid_step(self, a: Point, b: Point) -> bool:
        source = self.get_cell_height(a)
        target = self.get_cell_height(b)
        return target <= (source + 1)

    def steps(self, p: Point) -> List[Point]:
        neighbours = self.neighbours(p)
        steps = list(filter(lambda n: self.valid_step(p, n), neighbours))
        return steps


def get_board() -> HeightMap:
    with open('day12input.txt') as f:
        return HeightMap([list(line.strip()) for line in f])


def shortest_path(graph: Dict[T, List[U]], start: T, end: T) -> List[T]:
    if start == end:
        return [start]
    visited = set()
    queue = deque([[start]])
    while queue:
        path = queue.popleft()
        node = path[-1]

        if node not in visited:
            visited.add(node)
            next_nodes = graph[node]
            for n in next_nodes:
                new_path = path + [n]
                if n == end:
                    return new_path
                queue.append(new_path)
    return []


def day12_1():
    def __get_edges(b: HeightMap, p: Point) -> Set[int]:
        return [b.point_to_index(s) for s in b.steps(p)]
    board = get_board()
    graph = dict(enumerate(board.grid_map(__get_edges).get_all_cells()))
    sp = shortest_path(graph, board.point_to_index(board.start), board.point_to_index(board.end))
    paths = [board.index_to_point(i) for i in sp]
    return len(paths) - 1


def day12_2():
    def __get_edges(b: HeightMap, p: Point) -> Set[int]:
        return [b.point_to_index(s) for s in b.steps(p)]
    board = get_board()
    end = board.point_to_index(board.end)
    starts = map(board.point_to_index,
                 filter(None,
                        (board.grid_map(lambda b, p: p if b.get_cell(p) in 'Sa' else None).get_all_cells())))
    graph = dict(enumerate(board.grid_map(__get_edges).get_all_cells()))
    paths_lengths = [len(path) - 1 for start in starts if (path := shortest_path(graph, start, end))]
    return min(paths_lengths)


if __name__ == '__main__':
    result = day12_2()
    print(result)
