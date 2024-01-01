from __future__ import annotations
import re
from collections import deque
from dataclasses import dataclass
from enum import IntEnum
from pprint import pprint
from typing import NamedTuple, TypeAlias, Literal, Iterator
from functools import reduce
from operator import mul
from heapq import heappop, heappush
from itertools import count

bp_pattern = re.compile(r'\d+')


Amount: TypeAlias = int
Robots: TypeAlias = tuple[Amount, Amount, Amount, Amount]
Resources: TypeAlias = tuple[Amount, Amount, Amount, Amount]
Recipe: TypeAlias = tuple[Amount, Amount, Amount]


class Resource(IntEnum):
    ore = 0
    clay = 1
    obsidian = 2
    geode = 3


class Factory(NamedTuple):
    remaining: int
    robots: Robots = (1, 0, 0, 0)
    resources: Resources = (0, 0, 0, 0)

    def traverse(self, bp: BluePrint) -> Iterator[Factory]:
        rem = self.remaining
        per_robot = zip(Resource, bp.recipes, self.robots, bp.max_robots, self.resources)
        for rtype, recipe, have, rmax, res in per_robot:
            if rmax and have * rem + res >= rmax * rem:
                continue
            if not all(bool(prod) for prod, req in zip(self.robots, recipe) if req):
                continue

            needed = 1 + (
                max(
                    0 if avail >= req else (req - avail + prod - 1) // prod
                    for req, avail, prod in zip(recipe, self.resources, self.robots)
                    if req
                )
            )
            if needed >= rem:
                continue

            new_resources = [avail - req + prod * needed
                             for avail, req, prod in zip(self.resources, (*recipe, 0), self.robots)]
            new_robots = list(self.robots)
            new_robots[rtype] += 1
            yield Factory(rem - needed, tuple(new_robots), tuple(new_resources))

    @property
    def max_geodes(self) -> Amount:
        return self.resources[Resource.geode] + self.remaining * self.robots[Resource.geode]

    @property
    def max_geode_potential(self) -> Amount:
        return self.max_geodes + self.remaining * (self.remaining - 1) // 2

    @property
    def priority(self) -> tuple[Amount, Amount, Amount, int]:
        return *(-1 * r for r in self.resources[:0:-1]), self.remaining


@dataclass(frozen=True)
class BluePrint:
    bp_id: int
    recipes: tuple[Recipe, Recipe, Recipe, Recipe]
    max_robots: tuple[Amount, Amount, Amount, Literal[0]]

    @classmethod
    def from_tuple(cls, bp_id, oo, co, bo, bc, go, gb) -> BluePrint:
        recipes = ((oo, 0, 0), (co, 0, 0), (bo, bc, 0), (go, 0, gb))
        max_robots = [max(resource) for resource in zip(*recipes)]
        return cls(bp_id, recipes, (*max_robots, 0))

    def max_geodes(self, time: int) -> int:
        start = Factory(time)
        dq = deque([start])
        seen = {start}
        geodes = 0
        while dq:
            for state in dq.popleft().traverse(self):
                if state in seen or state.max_geode_potential < geodes:
                    continue
                geodes = max(geodes, state.max_geodes)
                seen.add(state)
                dq.append(state)
        return geodes


def get_blueprints(filename) -> list[BluePrint]:
    with open(filename) as f:
        return [BluePrint.from_tuple(*map(int, bp_pattern.findall(line.strip()))) for line in f]


def day19part1(blueprints: list[BluePrint], turns: int) -> int:
    geodes = [prioritised_maximum_opened_geodes(bp, turns) for bp in blueprints]
    quality_levels = [i * g for i, g in enumerate(geodes, 1)]
    return sum(quality_levels)


def day19part2(blueprints: list[BluePrint], turns: int) -> int:
    geodes = [prioritised_maximum_opened_geodes(bp, turns) for bp in blueprints[:3]]
    return reduce(mul, geodes)


def prioritised_maximum_opened_geodes(bp: BluePrint, time: int) -> int:
    tiebreaker = count()
    queue: list[tuple[Amount, Amount, Amount, int, int, Factory]] = []

    def add(factory: Factory):
        heappush(queue, (*factory.priority, next(tiebreaker), factory))

    start = Factory(time)
    add(start)
    seen = {start}
    max_geodes = 0
    while queue:
        *_, state = heappop(queue)
        for nstate in state.traverse(bp):
            if nstate in seen or nstate.max_geode_potential < max_geodes:
                continue
            max_geodes = max(max_geodes, nstate.max_geodes)
            seen.add(nstate)
            add(nstate)
    return max_geodes


if __name__ == '__main__':
    data = get_blueprints('day19input.txt')
    # result = day19part1(data, 24)
    result = day19part2(data, 32)
    pprint(result)
