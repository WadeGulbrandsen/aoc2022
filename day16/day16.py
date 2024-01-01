from collections import deque

import numpy as np
import re
from itertools import combinations, permutations
from operator import itemgetter, attrgetter
from typing import NamedTuple, Self
from dataclasses import dataclass

valve_pattern = re.compile(r'Valve (?P<name>\w+) has flow rate=(?P<rate>-?\d+); '
                           r'tunnels? leads? to valves? (?P<tunnels>.+)')


@dataclass()
class Path:
    time: int
    visited: list[int]
    pressure: int = 0

    def copy(self) -> Self:
        return Path(self.time, self.visited.copy(), self.pressure)


class Valve(NamedTuple):
    name: str
    rate: int
    tunnels: tuple[str]


class ActionPath(NamedTuple):
    path: list[str] = []
    opened: set[str] = set()
    pressure: int = 0
    minutes: int = 30

    def move(self, tunnel: str, rate: int):
        cutoff = self.minutes - 1
        if not rate or tunnel in self.opened or len(self.path) >= cutoff:
            return ActionPath(self.path + [tunnel], self.opened, self.pressure)
        if rate and tunnel not in self.opened:
            return ActionPath(self.path + [tunnel, tunnel],
                              self.opened | {tunnel},
                              self.pressure + rate * (cutoff - len(self.path)))


def get_valves(filename: str) -> list[Valve]:
    with open(filename) as f:
        return {
            gd['name']: Valve(gd['name'], int(gd['rate']), tuple(gd['tunnels'].split(', ')))
            for line in f if len(gd := valve_pattern.match(line.strip()).groupdict()) == 3
        }


def key(a, b):
    return tuple(sorted([a, b]))


def explore(shortest_paths: dict[tuple[str, str], int], start: Valve, targets: set[Valve], path: list[str],
            paths: list[tuple[list[str], int]], turns: int = 0, rate: int = 0, pressure: int = 0,
            max_turns: int = 30) -> int | None:
    if not targets:
        pressure += (max_turns - turns) * rate
        paths.append((path, pressure))
        return pressure
    for t in targets:
        new_turns = shortest_paths.get(key(start.name, t.name), 0) + 1
        if new_turns == 1 or turns + new_turns > max_turns:
            new_pressure = (max_turns - turns) * rate
            paths.append((path, pressure + new_pressure))
            continue
        new_pressure = rate * new_turns
        explore(shortest_paths, t, targets - {t}, path + [t.name], paths, turns + new_turns, rate + t.rate,
                pressure + new_pressure, max_turns)


def get_shortest_paths(valves: dict[str, Valve]) -> dict[tuple[str, str], int]:
    shortest_paths = {}
    for v in valves.values():
        for t in v.tunnels:
            shortest_paths[key(v.name, t)] = 1
            new_paths = {}
            for p, l in shortest_paths.items():
                if t == p[0] and p[1] != v.name:
                    k = key(p[1], v.name)
                elif t == p[1] and p[0] != v.name:
                    k = key(p[0], v.name)
                else:
                    continue
                if k not in shortest_paths or l + 1 < shortest_paths[k]:
                    new_paths[k] = l + 1
            shortest_paths.update(new_paths)
    return shortest_paths


def day16_part1(start: str, valves: dict[str, Valve]) -> tuple[list[str], int]:
    time_limit = 30
    targets = {v for v in valves.values() if v.rate}
    shortest_paths = get_shortest_paths(valves)
    paths: list[tuple[list[str], int]] = []
    explore(shortest_paths, valves[start], targets, [], paths, max_turns=time_limit)
    best = sorted(paths, key=itemgetter(1), reverse=True)[0]
    return best


def adjacency_matrix(valves: dict[str, Valve], index_map: dict[str, int]) -> np.ndarray:
    a = np.zeros((len(valves), len(valves)), dtype=int)
    for v in valves.values():
        for t in v.tunnels:
            a[index_map[v.name], index_map[t]] = 1
    return a


def distance_matrix(A: np.ndarray) -> np.ndarray:
    l = A.shape[0]
    D = np.where(A, A, 10000)
    d = np.diag([1]*l, 0)
    D = np.where(d, 0, D)
    for i, row in enumerate(D):
        neighbours = np.where(row != 10000)[0]
        for n1, n2 in permutations(neighbours, 2):
            d = min(row[n1] + row[n2], D[n1, n2])
            D[n1, n2] = d
            D[n2, n1] = d
    return D.astype(int)


def day16_part2(start: str, valves: dict[str, Valve]) -> tuple[list[str], int]:
    time_limit = 26
    index_map = {v: i for i, v in enumerate(valves)}
    A = adjacency_matrix(valves, index_map)
    D = distance_matrix(A)
    rates = np.array([v.rate for v in valves.values()])
    queue = deque([Path(time_limit, [index_map[start]])])
    paths = []

    while queue:
        path = queue.pop()
        paths.append(path)
        next_valves = [i for i, r in enumerate(rates) if (i not in path.visited) and (r != 0)]
        times_per_valve = [D[path.visited[-1]][c]+1 for c in next_valves]
        for t, v in zip(times_per_valve, next_valves):
            if path.time - t <= 0:
                continue
            new_path = path.copy()
            new_path.time -= t
            new_path.visited.append(v)
            new_path.pressure += (path.time - t) * rates[v]
            queue.append(new_path)

    ranked_paths = sorted(paths, key=attrgetter('pressure'), reverse=True)

    max_p = 0
    j = 0
    for i, a in enumerate(ranked_paths):
        if i > j:
            continue
        x = set(tuple(a.visited[1:]))
        for j, b in enumerate(ranked_paths[i+1:], i):
            if a.pressure + b.pressure <= max_p:
                break
            y = set(tuple(b.visited[1:]))
            if len(set.intersection(x, y)) == 0:
                if a.pressure + b.pressure > max_p:
                    max_p = a.pressure + b.pressure

    return max_p


if __name__ == '__main__':
    from pprint import pprint

    data = get_valves('day16input.txt')
    pprint(day16_part2('AA', data))
