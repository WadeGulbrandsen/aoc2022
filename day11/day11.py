from __future__ import annotations
import re
from dataclasses import dataclass
from functools import reduce
from itertools import product
from operator import attrgetter, pow
from typing import List, Callable, Dict
from gmpy2 import mpz, mul, add, f_mod, f_div

from more_itertools import partition

monkey_pattern = re.compile(r'Monkey (?P<monkey>\d+):\n'
                            r'  Starting items: (?P<items>.+)\n'
                            r'  Operation: new = old (?P<op>[*+]) (?P<val>.+)\n'
                            r'  Test: divisible by (?P<test>\d+)\n'
                            r'    If true: throw to monkey (?P<true>\d+)\n'
                            r'    If false: throw to monkey (?P<false>\d+)')


@dataclass
class Monkey:
    monkey_id: int
    items: List[int]
    op: Callable[[int, int], int]
    val: int
    test: int
    if_true: int
    if_false: int
    inspected: int = 0

    def take_turn(self, others: List[Monkey]):
        self.inspected += len(self.items)
        to_true, to_false = partition(lambda i: f_mod(i, self.test), [f_div(self.op(item, self.val), 3) for item in self.items])
        others[self.if_true].items.extend(to_true)
        others[self.if_false].items.extend(to_false)
        self.items.clear()

    def catch(self, item: int):
        self.items.append(item)

    def take_turn_mod(self, others: List[Monkey], moduli: mpz):
        self.inspected += len(self.items)
        to_true, to_false = partition(lambda i: i % self.test, [f_mod(self.op(item, self.val), moduli) for item in self.items])
        others[self.if_true].items.extend(to_true)
        others[self.if_false].items.extend(to_false)
        self.items.clear()


def get_monkeys():
    def __parse_monkey_dict(monkey_dict: Dict[str, str]) -> Monkey:
        monkey_id = int(monkey_dict['monkey'])
        items = list(map(int, monkey_dict['items'].split(', ')))
        if monkey_dict['val'] == 'old':
            op = pow
            val = 2
        else:
            op = {'+': add, '*': mul}[monkey_dict['op']]
            val = int(monkey_dict['val'])
        test = int(monkey_dict['test'])
        if_true = int(monkey_dict['true'])
        if_false = int(monkey_dict['false'])
        return Monkey(monkey_id, items, op, val, test, if_true, if_false)
        
    with open('day11input.txt') as f:
        return [__parse_monkey_dict(m.groupdict()) for m in monkey_pattern.finditer(f.read())]


def print_round(i: int, monkeys: List[Monkey]):
    print(f'== After round {i} ==')
    for monkey in monkeys:
        print(f'Monkey {monkey.monkey_id} inspected items {monkey.inspected} times.')
    print('')


def day11_1():
    monkeys = get_monkeys()
    print_at = [1, 10, 20]
    for i in range(1, 21):
        [monkey.take_turn(monkeys) for monkey in monkeys]
        if i in print_at:
            print_round(i, monkeys)
    return mul(*sorted(map(attrgetter('inspected'), monkeys), reverse=True)[:2])


def day11_2():
    monkeys = get_monkeys()
    moduli = reduce(mul, map(attrgetter('test'), monkeys))
    print_at = [1, 20] + list(range(100, 10001, 100))
    for i in range(1, 10001):
        [monkey.take_turn_mod(monkeys, moduli) for monkey in monkeys]
        if i in print_at:
            print_round(i, monkeys)
    return mul(*sorted(map(attrgetter('inspected'), monkeys), reverse=True)[:2])


if __name__ == '__main__':
    result = day11_2()
    print(result)
