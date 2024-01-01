from __future__ import annotations
from enum import Enum
import re
from typing import NamedTuple, List, Set

from more_itertools import flatten

move_pattern = re.compile(r'(?P<direction>[UDLR]) (?P<spaces>\d+)')


class Direction(Enum):
    U = (0, -1)
    D = (0, 1)
    L = (-1, 0)
    R = (1, 0)


class Vector(NamedTuple):
    x: int
    y: int

    def length(self) -> int:
        return max(abs(self.x), abs(self.y))


class Position(NamedTuple):
    x: int
    y: int

    def move(self, move: Move) -> List[Position]:
        dx, dy = move.direction.value
        return [Position(self.x + dx * i, self.y + dy * i) for i in range(1, move.distance + 1)]

    def to_other(self, other: Position) -> Vector:
        return Vector(other.x - self.x, other.y - self.y)

    def touching(self, other: Position) -> bool:
        if self == other:
            return True
        vec = self.to_other(other)
        if vec.length() <= 1:
            return True
        return False


class Move(NamedTuple):
    direction: Direction
    distance: int


def get_moves() -> List[Move]:
    with open('day09input.txt') as f:
        moves = [
            Move(Direction[m.groupdict()['direction']], int(m.groupdict()['spaces']))
            for line in f if (m := move_pattern.fullmatch(line.strip()))
        ]
    return moves


def render_state(min_x: int, max_x: int, min_y: int, max_y: int, start: Position, hp: Position, tp: Position) -> str:
    def __char(p: Position) -> str:
        if p == hp:
            return 'H'
        if p == tp:
            return 'T'
        if p == start:
            return 's'
        return '.'

    rows = [''.join([__char(Position(x, y)) for x in range(min_x, max_x + 1)]) for y in range(min_y, max_y + 1)]
    return '\n'.join(rows)


def move_tail(tail_position: Position, head_position: Position) -> Position:
    def __scale(v: int) -> int:
        if v == 0:
            return v
        if v < 0:
            return -1
        if v > 0:
            return 1

    vec = tail_position.to_other(head_position)
    if vec.length() <= 1:
        return tail_position
    return Position(tail_position.x + __scale(vec.x), tail_position.y + __scale(vec.y))


def render_visited(min_x: int, max_x: int, min_y: int, max_y: int, start: Position, tails: Set[Position]) -> str:
    def __char(p: Position) -> str:
        if p == start:
            return 'S'
        if p in tails:
            return '#'
        return '.'

    rows = [''.join([__char(Position(x, y)) for x in range(min_x, max_x + 1)]) for y in range(min_y, max_y + 1)]
    return '\n'.join(rows)


def render_long_tail(min_x: int, max_x: int, min_y: int, max_y: int, start: Position, positions: List[Position]) -> str:
    def __char(p: Position) -> str:
        try:
            index = positions.index(p)
            if index == 0:
                return 'H'
            else:
                return str(index)
        except ValueError:
            pass
        if p == start:
            return 'S'
        return '.'

    rows = [''.join([__char(Position(x, y)) for x in range(min_x, max_x + 1)]) for y in range(min_y, max_y + 1)]
    return '\n'.join(rows)


def day09_1():
    moves = get_moves()
    start = Position(0, 0)
    head_position = start
    tail_position = start
    head_positions = [start]
    tail_positions = []
    for move in moves:
        head_positions.extend(head_position.move(move))
        head_position = head_positions[-1]
    for hp in head_positions:
        tail_position = move_tail(tail_position, hp)
        tail_positions.append(tail_position)
    x_vals = {p.x for p in head_positions}
    y_vals = {p.y for p in head_positions}
    min_x = min(x_vals)
    max_x = max(x_vals)
    min_y = min(y_vals)
    max_y = max(y_vals)
    tail_visits = set(tail_positions)
    print('\nTail Visited')
    print(render_visited(min_x, max_x, min_y, max_y, start, tail_visits))
    return len(tail_visits)


def day09_2():
    moves = get_moves()
    start = Position(0, 0)
    positions = [[start for _i in range(10)]]
    for move in moves:
        heads = positions[-1][0].move(move)
        for head in heads:
            current = positions[-1]
            new_positions = [head]
            for p in current[1:]:
                new_positions.append(move_tail(p, new_positions[-1]))
            positions.append(new_positions)

    x_vals = {p.x for p in flatten(positions)}
    y_vals = {p.y for p in flatten(positions)}
    min_x = min(x_vals)
    max_x = max(x_vals)
    min_y = min(y_vals)
    max_y = max(y_vals)
    if len(positions) < 1000:
        for num, state in enumerate(positions):
            if not num:
                print('== Initiial State ==')
            else:
                print(f'\n== Step #{num:03d} ==')
            print(render_long_tail(min_x, max_x, min_y, max_y, start, state))
    tail_visits = set([p[-1] for p in positions])
    print('\nTail Visited')
    print(render_visited(min_x, max_x, min_y, max_y, start, tail_visits))
    return len(tail_visits)


if __name__ == '__main__':
    print(day09_2())
