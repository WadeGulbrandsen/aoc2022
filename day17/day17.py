from enum import Enum
from itertools import cycle
from operator import itemgetter
from pprint import pprint
from more_itertools import split_at
from dataclasses import dataclass
from typing import NamedTuple, TypeVar
import numpy as np
import matplotlib.pyplot as plt
from numpy.typing import NDArray
from deepdiff import DeepDiff


SHAPE_CHAR_MAP = {True: '#', False: '.'}
SHOW_DEPTH = 30


T = TypeVar('T')

plt.style.use('dark_background')


class XYPair(NamedTuple):
    x: int
    y: int


class Dir(XYPair):
    pass


class Shape(NamedTuple):
    matrix: NDArray[bool]


class Move(Enum):
    UP = Dir(0, -1)
    DOWN = Dir(0, 1)
    LEFT = Dir(-1, 0)
    RIGHT = Dir(1, 0)


@dataclass()
class Rock:
    matrix: NDArray[int]

    def __init__(self, shape: Shape) -> None:
        self.matrix = np.pad(shape.matrix.astype(int), ((0, 3), (2, 5 - shape.matrix.shape[1])))


def to_str_matrix(matrix: NDArray[T], char_map: dict[T, str], default: str = ' ') -> NDArray[str]:
    str_array = np.frompyfunc(lambda item: char_map.get(item, default), 1, 1)
    str_matrix = str_array(matrix).astype(str)
    if str_matrix.ndim > 2:
        return np.squeeze(str_matrix, axis=0)
    return str_matrix


def shape_from_strings(lines: list[str]) -> Shape | None:
    if not lines:
        return None
    points = [[c == '#' for c in line] for line in lines]
    shape = Shape(np.array(points, dtype=bool))
    return shape


def load_shapes() -> list[Shape]:
    with open('day17shapes.txt') as f:
        s = list(filter(None, map(shape_from_strings, split_at(f.read().splitlines(), lambda l: l == ''))))
    return s


def get_jets(filename: str) -> list[Move]:
    dir_map = {'<': Move.LEFT, '>': Move.RIGHT}
    with open(filename) as f:
        return [d for c in f.read().strip() if (d := dir_map.get(c))]


def draw_cave(stack: NDArray[int], num: int, drops: int, h_pads: tuple[int, int] = (-1, -1)) -> None:
    depth = stack.shape[0]
    pad_y = SHOW_DEPTH - depth if depth < SHOW_DEPTH else 0
    plt.ion()
    plt.title(f'Rock {num} of {drops}')
    plt.imshow(np.pad(stack[:SHOW_DEPTH], ((0, 1 + pad_y), (1, 1)), constant_values=((0, -1 * bool(pad_y)), h_pads)),
               vmin=-3, vmax=9)
    plt.show()
    plt.pause(0.00001)


def move_rock(stack: NDArray[int], jet: Move) -> bool:
    rock_indexes = np.argwhere(stack == 1)
    targets = rock_indexes + list(reversed(jet.value))
    y_size, x_size = stack.shape
    for target in targets:
        if not (0 <= target[0] < y_size and 0 <= target[1] < x_size):
            return False
        val = stack[*target]
        if val > 1:
            return False
    rs = {tuple(ri) for ri in rock_indexes}
    ts = {tuple(ti) for ti in targets}
    for yx in rs - ts:
        stack[yx] = 0
    for yx in ts - rs:
        stack[yx] = 1
    return True


def drop_rock(shape: Shape, moves: cycle, stack: NDArray[int] | None, num: int, drops: int) -> NDArray[int]:
    wall_pads = {Move.LEFT: (3, -1), Move.RIGHT: (-1, 3)}
    rock = Rock(shape)
    if stack is None:
        stack = rock.matrix
    else:
        stack = np.vstack([rock.matrix, stack])
    # draw_cave(stack, num, drops)
    can_move = True
    while can_move:
        jet: Move = next(moves)
        move_rock(stack, jet)
        can_move = move_rock(stack, Move.DOWN)
        # draw_cave(stack, num, drops)
    stack = stack[~np.all(stack == 0, axis=1)]
    for ri in np.argwhere(stack == 1):
        stack[*ri] = 9
    # draw_cave(stack, num, drops)
    return stack


def day17part1(shapes: list[Shape], jets: list[Move], drops: int):
    shape_cycler = cycle(shapes)
    jets_cycler = cycle(jets)
    stack: NDArray[int] | None = None

    for i in range(drops):
        stack = drop_rock(next(shape_cycler), jets_cycler, stack, i + 1, drops)
        if i % 1000 == 0:
            print(f'Rock {i} of {drops}')
    return stack.shape[0]


def day17part2(shapes: list[Shape], jets: list[Move], drops: int):
    num_shapes = len(shapes)
    num_jets = len(jets)
    stack: NDArray[int] | None = None
    j = 0
    prev_h = 0
    results = []
    for i in range(drops):
        rock = Rock(shapes[i % num_shapes])
        if stack is None:
            stack = rock.matrix
        else:
            stack = np.vstack([rock.matrix, stack])
        can_move = True
        while can_move:
            jet = jets[j % num_jets]
            j += 1
            move_rock(stack, jet)
            can_move = move_rock(stack, Move.DOWN)
        stack = stack[~np.all(stack == 0, axis=1)]
        for ri in np.argwhere(stack == 1):
            stack[*ri] = 9
        new_h = stack.shape[0]
        results.append((new_h - prev_h, i % num_shapes, j % num_jets, tuple(map(tuple, np.argwhere(stack[:30] == 9)))))
        prev_h = new_h
        if i > 60:
            m = i // 2
            for l in range(30, m):
                s1 = results[-l:]
                s2 = results[l * -2:-l]
                if s1 == s2:
                    p_len = len(s1)
                    print(f'Pattern found on turn {i} with length of {p_len}')
                    print(f'Current height is {new_h}')
                    h_deltas = tuple(map(itemgetter(0), s1))
                    p_height = sum(h_deltas)
                    to_go = drops - i - 1
                    cycles, remainder = divmod(to_go, p_len)
                    print(f'Each cycle of the pattern adds {p_height}')
                    print(f'With {to_go} rocks to go that will take {cycles} cycles with {remainder} left over')
                    total = new_h + p_height * cycles + sum(h_deltas[:remainder])
                    print(f'The total is {total}')
                    return total

    return stack.shape[0]


if __name__ == '__main__':
    # pprint(day17part1(load_shapes(), get_jets('day17example.txt'), 2022))
    pprint(day17part2(load_shapes(), get_jets('day17input.txt'), 2022))
    pprint(day17part2(load_shapes(), get_jets('day17input.txt'), 1000000000000))

