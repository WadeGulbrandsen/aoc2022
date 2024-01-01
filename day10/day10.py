from __future__ import annotations

from enum import IntEnum
from itertools import accumulate, takewhile
from operator import attrgetter
from typing import NamedTuple, Optional, List, Tuple

from more_itertools import flatten, chunked


class Instruction(IntEnum):
    NOOP = 1
    ADDX = 2


class Op(NamedTuple):
    instruction: Instruction
    value: Optional[int]

    def __repr__(self):
        return f'Op({self.instruction.name}{" " + str(self.value) if self.value is not None else ""})'


def read_ops() -> List[Op]:
    def __read_op(line: str) -> Op:
        parts = line.strip().split()
        instruction = Instruction[parts[0].upper()]
        value = int(parts[1]) if len(parts) == 2 else None
        return Op(instruction, value)

    with open('day10input.txt') as f:
        ops = [__read_op(line) for line in f]
    return ops


def get_positions(ops: List[Op]) -> List[int]:
    deltas = flatten(map(lambda o: [0] if o.instruction == Instruction.NOOP else [0, o.value], ops))
    positions = list(accumulate(deltas, initial=1))[:-1]
    return positions


def day10_1():
    ops = read_ops()
    positions = get_positions(ops)
    checks = [20, 60, 100, 140, 180, 220]
    signal_strengths = [i * positions[i - 1] for i in checks]
    return sum(signal_strengths)


def day10_2():
    drawn = (
        {'cycle': n + 1, 'col': n % 40, 'sprite': [p - 1, p, p + 1]}
        for n, p in enumerate(get_positions(read_ops()))
    )
    rows = [''.join(['#' if c['col'] in c['sprite'] else ' ' for c in r]) for r in chunked(drawn, 40)]
    return '\n'.join(rows)


if __name__ == '__main__':
    result = day10_2()
    print(result)
