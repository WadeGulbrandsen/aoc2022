import math
import re

from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from typing import TypeAlias, Self


class Tile(StrEnum):
    SPACE = ' '
    OPEN = '.'
    WALL = '#'
    UP = '^'
    DOWN = 'v'
    LEFT = '<'
    RIGHT = '>'
    END = 'x'


class Turn(IntEnum):
    L = 3
    R = 1


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def __add__(self, other: Self) -> Self:
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, other: Self) -> Self:
        return Point(self.x * other.x, self.y * other.y)


class Direction(IntEnum):
    E = 0
    S = 1
    W = 2
    N = 3

    def horizontal(self) -> bool:
        return self % 2 == 0

    def vertical(self) -> bool:
        return self % 2 == 1

    def rotate(self, turn: Turn):
        return Direction((self + turn) % 4)


direction_to_move = {
    Direction.E: Point(1, 0),
    Direction.S: Point(0, 1),
    Direction.W: Point(-1, 0),
    Direction.N: Point(0, -1)
}

direction_to_tile = {
    Direction.E: Tile.RIGHT,
    Direction.S: Tile.DOWN,
    Direction.W: Tile.LEFT,
    Direction.N: Tile.UP
}

Instruction: TypeAlias = int | Turn

Instructions: TypeAlias = list[Instruction]


def get_instructions(string: str) -> Instructions:
    instruction_pattern = re.compile(r'(\d+|[LR])')
    return [int(i[0]) if i[0].isdigit() else Turn[i[0]] for i in instruction_pattern.finditer(string)]


@dataclass()
class TileLine:
    start: int
    end: int
    walls: list[int] = field(default_factory=list)


@dataclass()
class Board:
    tiles: dict[Point, Tile]
    size: Point
    rows: dict[int, TileLine]
    cols: dict[int, TileLine]

    def __str__(self):
        s = ''
        for y in range(1, self.size.y + 1):
            for x in range(1, self.size.x + 1):
                s += self.tiles.get(Point(x, y), Tile.SPACE)
            s += '\n'
        return s

    def start(self) -> Point:
        return Point(self.rows[1].start, 1)

    def advance(self, position: Point, direction: Direction, distance: int) -> Point:
        p = position
        line = self.rows[position.y] if direction.horizontal() else self.cols[position.x]
        for i in range(0, distance):
            self.tiles[p] = direction_to_tile[direction]
            new_p = p + direction_to_move[direction]
            match direction.horizontal():
                case True if new_p.x < line.start:
                    new_p = Point(line.end, new_p.y)
                case True if new_p.x > line.end:
                    new_p = Point(line.start, new_p.y)
                case False if new_p.y < line.start:
                    new_p = Point(new_p.x, line.end)
                case False if new_p.y > line.end:
                    new_p = Point(new_p.x, line.start)
            v = new_p.x if direction.horizontal() else new_p.y
            if v in line.walls:
                return p
            p = new_p
        return p

    def follow_instructions(self, instructions: Instructions) -> int:
        pos = self.start()
        facing = Direction.E
        for inst in instructions:
            if isinstance(inst, Turn):
                facing = facing.rotate(inst)
            else:
                pos = self.advance(pos, facing, inst)
        self.tiles[pos] = Tile.END
        return (1000 * pos.y) + (4 * pos.x) + facing

    @staticmethod
    def get_board(lines: list[str]) -> 'Board':
        tiles = {}
        max_x = 0
        rows = {}
        for y, line in enumerate(lines, start=1):
            max_x = max(max_x, len(line.strip('\n')))
            tl = TileLine(2 ** 31 - 1, 0)
            for x, char in enumerate(line.strip('\n'), start=1):
                if char in ['.', '#']:
                    tl.start = min(tl.start, x)
                    tl.end = max(tl.end, x)
                    tiles[Point(x, y)] = Tile(char)
                    if char == '#':
                        tl.walls.append(x)
            rows[y] = tl
        size = Point(max_x, len(lines))
        cols = {}
        for x in range(1, size.x + 1):
            tl = TileLine(2 ** 31 - 1, 0)
            for y in range(1, size.y + 1):
                if tile := tiles.get(Point(x, y)):
                    tl.start = min(tl.start, y)
                    tl.end = max(tl.end, y)
                    if tile == Tile.WALL:
                        tl.walls.append(y)
            cols[x] = tl
        return Board(tiles, size, rows, cols)


Side: TypeAlias = dict[Point, Point]


@dataclass()
class Transfer:
    new_side: int
    new_direction: Direction
    rotate: bool
    reverse_x: bool
    reverse_y: bool


SAMPLE_CUBE_TRANSFERS = {
    1: {
        Direction.E: Transfer(6, Direction.W, False, False, True),
        Direction.S: Transfer(4, Direction.S, False, False, True),
        Direction.W: Transfer(3, Direction.S, True, False, False),
        Direction.N: Transfer(2, Direction.S, False, True, False)
    },
    2: {
        Direction.E: Transfer(3, Direction.E, False, True, False),
        Direction.S: Transfer(5, Direction.N, False, True, False),
        Direction.W: Transfer(6, Direction.N, True, True, True),
        Direction.N: Transfer(1, Direction.S, False, True, False)
    },
    3: {
        Direction.E: Transfer(4, Direction.E, False, True, False),
        Direction.S: Transfer(5, Direction.E, True, True, True),
        Direction.W: Transfer(2, Direction.W, False, True, False),
        Direction.N: Transfer(1, Direction.N, True, False, False)
    },
    4: {
        Direction.E: Transfer(6, Direction.S, True, True, True),
        Direction.S: Transfer(5, Direction.S, False, False, True),
        Direction.W: Transfer(3, Direction.W, False, True, False),
        Direction.N: Transfer(1, Direction.N, False, False, True)
    },
    5: {
        Direction.E: Transfer(6, Direction.E, False, True, False),
        Direction.S: Transfer(2, Direction.N, False, True, False),
        Direction.W: Transfer(3, Direction.N, True, True, True),
        Direction.N: Transfer(4, Direction.N, False, False, True)
    },
    6: {
        Direction.E: Transfer(1, Direction.W, False, False, True),
        Direction.S: Transfer(2, Direction.E, True, True, True),
        Direction.W: Transfer(5, Direction.W, False, True, False),
        Direction.N: Transfer(4, Direction.W, True, True, True)
    }
}

INPUT_CUBE_TRANSFERS = {
    1: {
        Direction.E: Transfer(2, Direction.E, False, True, False),
        Direction.S: Transfer(3, Direction.S, False, False, True),
        Direction.W: Transfer(4, Direction.E, False, False, True),
        Direction.N: Transfer(6, Direction.E, True, False, False)
    },
    2: {
        Direction.E: Transfer(5, Direction.W, False, False, True),
        Direction.S: Transfer(3, Direction.W, True, False, False),
        Direction.W: Transfer(1, Direction.W, False, True, False),
        Direction.N: Transfer(6, Direction.N, False, False, True)
    },
    3: {
        Direction.E: Transfer(2, Direction.N, True, False, False),
        Direction.S: Transfer(5, Direction.S, False, False, True),
        Direction.W: Transfer(4, Direction.S, True, False, False),
        Direction.N: Transfer(1, Direction.N, False, False, True)
    },
    4: {
        Direction.E: Transfer(5, Direction.E, False, True, False),
        Direction.S: Transfer(6, Direction.S, False, False, True),
        Direction.W: Transfer(1, Direction.E, False, False, True),
        Direction.N: Transfer(3, Direction.E, True, False, False)
    },
    5: {
        Direction.E: Transfer(2, Direction.W, False, False, True),
        Direction.S: Transfer(6, Direction.W, True, False, False),
        Direction.W: Transfer(4, Direction.W, False, True, False),
        Direction.N: Transfer(3, Direction.N, False, False, True)
    },
    6: {
        Direction.E: Transfer(5, Direction.N, True, False, False),
        Direction.S: Transfer(2, Direction.S, False, False, True),
        Direction.W: Transfer(1, Direction.S, True, False, False),
        Direction.N: Transfer(4, Direction.N, False, False, True)
    }
}


@dataclass()
class Cube:
    tiles: dict[Point, Tile]
    size: Point
    cube_size: int
    sides: dict[int, Side]
    side_map: dict[Point, tuple[int, Point]]

    def __str__(self):
        s = ''
        for y in range(1, self.size.y + 1):
            tiles = ''
            sides = ''
            for x in range(1, self.size.x + 1):
                tiles += self.tiles.get(Point(x, y), Tile.SPACE)
                sides += str(self.side_map.get(Point(x, y), (Tile.SPACE, Tile.SPACE))[0])
            s += f'{tiles} {sides}\n'
        return s

    def start(self) -> Point:
        return self.sides[1][Point(0, 0)]

    def advance(self, position: Point, direction: Direction, distance: int,
                transfers: dict[int, dict[Direction, Transfer]]) -> tuple[Point, Direction]:
        p = position
        d = direction
        for i in range(0, distance):
            self.tiles[p] = direction_to_tile[d]
            sn, sp = self.side_map[p]
            new_side = sn
            new_d = d
            new_sp = sp + direction_to_move[d]
            if new_sp.x < 0 or new_sp.x >= self.cube_size or new_sp.y < 0 or new_sp.y >= self.cube_size:
                transfer = transfers[sn][d]
                new_sp = sp
                if transfer.rotate:
                    new_sp = Point(new_sp.y, new_sp.x)
                if transfer.reverse_x:
                    new_sp = Point(self.cube_size - 1 - new_sp.x, new_sp.y)
                if transfer.reverse_y:
                    new_sp = Point(new_sp.x, self.cube_size - 1 - new_sp.y)
                new_side = transfer.new_side
                new_d = transfer.new_direction
            new_p = self.sides[new_side][new_sp]
            if self.tiles[new_p] == Tile.WALL:
                return p, d
            p = new_p
            d = new_d
        return p, d

    def follow_instructions(self, instructions: Instructions, transfers: dict[int, dict[Direction, Transfer]]) -> int:
        pos = self.start()
        facing = Direction.E
        for inst in instructions:
            if isinstance(inst, Turn):
                facing = facing.rotate(inst)
            else:
                pos, facing = self.advance(pos, facing, inst, transfers)
        self.tiles[pos] = Tile.END
        return (1000 * pos.y) + (4 * pos.x) + facing

    @staticmethod
    def get_cube(lines: list[str]) -> 'Cube':
        tiles = {}
        max_x = 0
        max_y = len(lines)
        for y, line in enumerate(lines, start=1):
            max_x = max(max_x, len(line.strip('\n')))
            for x, char in enumerate(line.strip('\n'), start=1):
                if char in ['.', '#']:
                    tiles[Point(x, y)] = Tile(char)
        size = Point(max_x, max_y)
        cube_size = math.gcd(max_x, max_y)
        side = 1
        sides = {}
        side_map = {}
        for y in range(1, max_y, cube_size):
            for x in range(1, max_x, cube_size):
                if (p := Point(x, y)) in tiles:
                    s = {}
                    for v in range(cube_size):
                        for u in range(cube_size):
                            n = Point(u, v)
                            s[n] = p + n
                            side_map[p + n] = side, n
                    sides[side] = s
                    side += 1
        return Cube(tiles, size, cube_size, sides, side_map)


def parse_board(filename: str) -> tuple[Board, Instructions]:
    with open(filename) as f:
        file = f.readlines()
        f.close()
    return Board.get_board(file[:-2]), get_instructions(file[-1])


def parse_cube(filename: str) -> tuple[Cube, Instructions]:
    with open(filename) as f:
        file = f.readlines()
        f.close()
    return Cube.get_cube(file[:-2]), get_instructions(file[-1])


if __name__ == '__main__':
    sample_file = "sample.txt"
    input_file = "input.txt"

    p1s_board, p1s_inst = parse_board(sample_file)
    p1s = p1s_board.follow_instructions(p1s_inst)
    assert p1s == 6032

    p1i_board, p1i_inst = parse_board(input_file)
    p1i = p1i_board.follow_instructions(p1i_inst)
    assert p1i == 103224

    print(f'Part 1: {p1i}')

    sample_cube, sample_instructions = parse_cube(sample_file)
    p2s = sample_cube.follow_instructions(sample_instructions, SAMPLE_CUBE_TRANSFERS)
    assert p2s == 5031

    input_cube, input_instructions = parse_cube(input_file)
    p2i = input_cube.follow_instructions(input_instructions, INPUT_CUBE_TRANSFERS)
    assert p2i == 189097

    print(f'Part 2: {p2i}')

