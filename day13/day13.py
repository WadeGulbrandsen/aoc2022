import json
import re
from functools import cmp_to_key, reduce
from operator import itemgetter, mul
from typing import Union, List

from more_itertools import partition

pairs_pattern = re.compile(r'(?P<left>[\[\]\d,]+)\n(?P<right>[\[\]\d,]+)')
packet_pattern = re.compile(r'(?P<packet>[\[\]\d,]+)')


def get_packet_pairs():
    with open('day13.txt') as f:
        pairs = [
            {k: json.loads(v) for k, v in p.groupdict().items()}
            for p in pairs_pattern.finditer(f.read())
        ]
    return pairs


def get_packets():
    with open('day13.txt') as f:
        packets = [json.loads(p.group()) for p in packet_pattern.finditer(f.read())]
    return packets


def cmp_ints(a: int, b: int) -> int:
    return (a > b) - (a < b)


def cmp_lists(a: List[Union[List, int]], b: List[Union[List, int]]) -> int:
    if len(a) == 0 and len(b) == 0:
        return 0
    if len(a) == 0:
        return -1
    if len(b) == 0:
        return 1
    c = cmp_pair(a[0], b[0])
    if c == 0:
        return cmp_lists(a[1:], b[1:])
    return c


def cmp_pair(a: Union[List, int], b: Union[List, int]) -> int:
    if isinstance(a, int) and isinstance(b, int):
        return cmp_ints(a, b)
    elif isinstance(a, list) and isinstance(b, list):
        return cmp_lists(a, b)
    else:
        return cmp_lists(*([v] if isinstance(v, int) else v for v in [a, b]))


def day13_1():
    packet_pairs = get_packet_pairs()
    out_of_order, in_order = map(list,
                                 partition(lambda t: t[2] < 0,
                                           [(i, p, cmp_pair(p['left'], p['right'])) for i, p in
                                            enumerate(packet_pairs, 1)]))
    in_order_indexes = list(map(itemgetter(0), in_order))
    return sum(in_order_indexes)


def day13_2():
    dividers = [[[2]], [[6]]]
    packets = get_packets() + dividers
    sorted_packets = dict(filter(lambda x: x[1] in dividers, enumerate(sorted(packets, key=cmp_to_key(cmp_pair)), 1)))
    return reduce(mul, sorted_packets.keys())


if __name__ == '__main__':
    print(day13_2())
