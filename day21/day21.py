import re
from sympy import solve, sympify
from dataclasses import dataclass
from operator import add, sub, mul, floordiv
from typing import Callable, TypeAlias, Self

from more_itertools import partition

know_pattern = re.compile(r'(?P<name>\w{4}): (?P<value>\d+)')
monkey_pattern = re.compile(r'(?P<name>\w{4}): (?P<a>\w{4}) (?P<op>[+-/*]) (?P<b>\w{4})')


@dataclass()
class Monkey:
    name: str
    a: str | int
    b: str | int
    op: Callable[[int, int], int]

    @classmethod
    def monkey_from_str(cls, string: str) -> tuple[str, Self | int] | None:
        ops = {'+': add, '-': sub, '*': mul, '/': floordiv}
        if r := know_pattern.fullmatch(string):
            return r.groupdict()['name'], int(r.groupdict()['value'])
        if r := monkey_pattern.fullmatch(string):
            return r.groupdict()['name'], Monkey(r.groupdict()['name'],
                                                 r.groupdict()['a'],
                                                 r.groupdict()['b'],
                                                 ops[r.groupdict()['op']])
        return None


Monkeys: TypeAlias = dict[str, int | Monkey]


def get_monkeys(filename) -> Monkeys:
    with open(filename) as f:
        return dict([m for line in f if (m := Monkey.monkey_from_str(line.strip()))])


def __get_monkey(name: str, known: dict[str, int], unknown: Monkeys) -> int | None:
    if name in known:
        return known[name]
    elif name in unknown:
        m: Monkey = unknown[name]
        a = known[m.a] if m.a in known else __get_monkey(m.a, known, unknown)
        if a is None:
            return None
        b = known[m.b] if m.b in known else __get_monkey(m.b, known, unknown)
        if b is None:
            return None
        v = m.op(a, b)
        del unknown[name]
        known[name] = v
        return v
    return None


def get_monkey(name: str, monkeys: Monkeys) -> int | None:
    known, unknown = map(dict, partition(lambda x: isinstance(x[1], Monkey), monkeys.items()))
    return __get_monkey(name, known, unknown)


def yell_num(monkeys: Monkeys) -> int | None:
    op_symbols = {add: '+', sub: '-', mul: '*', floordiv: '/'}
    del monkeys['humn']
    root = monkeys.pop('root')
    known, unknown = map(dict, partition(lambda x: isinstance(x[1], Monkey), monkeys.items()))
    left = __get_monkey(root.a, known, unknown)
    right = __get_monkey(root.b, known, unknown)
    if left is None:
        val = right
        h = root.a
    else:
        val = left
        h = root.b

    def __find_humn(head: str) -> str:
        m = unknown[head]
        a = 'x' if m.a == 'humn' else known[m.a] if m.a in known else __find_humn(m.a)
        b = 'x' if m.b == 'humn' else known[m.b] if m.b in known else __find_humn(m.b)
        return f'({a} {op_symbols[m.op]} {b})'

    equation = __find_humn(h)
    eq_str = f'{equation} - {val}'
    expr = sympify(eq_str)
    for sol in solve(expr):
        known['humn'] = sol
        if __get_monkey(h, known, unknown) == val:
            return sol
    return None


if __name__ == '__main__':
    example_data = get_monkeys('day21example.txt')
    input_data = get_monkeys('day21input.txt')
    print(get_monkey('root', input_data))
    print(yell_num(input_data))
