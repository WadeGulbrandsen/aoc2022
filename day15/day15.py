from collections import Counter
from dataclasses import dataclass, field
from operator import attrgetter
from typing import NamedTuple
from more_itertools import flatten
import re

sensor_pattern = re.compile(r'Sensor at x=(?P<sx>-?\d+), y=(?P<sy>-?\d+): '
                            r'closest beacon is at x=(?P<bx>-?\d+), y=(?P<by>-?\d+)')


class Point(NamedTuple):
    x: int
    y: int


@dataclass()
class SensorAndBeacon:
    sensor: Point
    beacon: Point
    distance: int = field(init=False)

    def __y_distance(self, y: int):
        return abs(self.distance - abs(self.sensor.y - y))

    def __x_range(self, y: int) -> range | None:
        match self.get_x_bounds(y):
            case (min_x, max_x):
                return range(min_x, max_x + 1)
            case _:
                return None

    def get_x_bounds(self, y: int) -> tuple[int, int] | None:
        if (y_distance := self.__y_distance(y)) <= self.distance:
            min_x = self.sensor.x - y_distance
            max_x = self.sensor.x + y_distance
            return min_x, max_x
        return None

    def __post_init__(self):
        self.distance = taxi_distance(self.sensor, self.beacon)

    def in_range(self, p: Point) -> bool:
        return taxi_distance(self.sensor, p) <= self.distance

    def get_points_in_range(self) -> list[Point]:
        y_range = range(self.sensor.y - self.distance, self.sensor.y + self.distance + 1)
        points = [Point(x, y) for y in y_range for x in x_range if (x_range := self.__x_range(y))]
        return points

    def get_edge_points(self, xy_range: range = None) -> list[Point]:
        def __x_edges(y: int) -> list[int]:
            y_distance = self.distance - abs(self.sensor.y - y) + 1
            return [self.sensor.x - y_distance, self.sensor.x + y_distance]
        y_range = range(self.sensor.y - self.distance - 1, self.sensor.y + self.distance + 2)
        if xy_range:
            points = [Point(x, y) for y in y_range for x in __x_edges(y) if x in xy_range and y in xy_range]
        else:
            points = [Point(x, y) for y in y_range for x in __x_edges(y)]
        return points

    def get_points_in_row(self, y: int) -> list[Point]:
        if abs(self.sensor.y - y) <= self.distance:
            points = [Point(x, y) for x in self.__x_range(y)]
            return points
        return []


def taxi_distance(a: Point, b: Point) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def get_sensors_with_beacons() -> list[SensorAndBeacon]:
    def __make_sensor(sb: dict[str, int]) -> SensorAndBeacon:
        return SensorAndBeacon(Point(sb['sx'], sb['sy']), Point(sb['bx'], sb['by']))

    with open('day15.txt') as f:
        return [
            __make_sensor({k: int(v) for k, v in m.groupdict().items()})
            for m in sensor_pattern.finditer(f.read())
        ]


def draw_board(title: str, sensors: set[Point], beacons: set[Point], scanned: set[Point], edges: Counter[Point],
               x_range: range = None, y_range: range = None) -> str:
    def __get_char(p: Point) -> str:
        if p in edges:
            return str(edges[p])
        if p in sensors:
            return 'S'
        if p in beacons:
            return 'B'
        if p in scanned:
            return '#'
        return '.'

    all_points = sensors | beacons | scanned | set(edges)
    xs, ys = zip(*all_points)
    if x_range is None:
        x_range = range(min(xs), max(xs) + 1)
    if y_range is None:
        y_range = range(min(ys), max(ys) + 1)
    lines = [''.join([__get_char(Point(x, y)) for x in x_range]) for y in y_range]
    return '\n'.join([title] + lines)


def day15_1a(swbs: list[SensorAndBeacon], y: int) -> int:
    # 26 or 5403290
    beacons = set(map(attrgetter('beacon'), swbs))
    scanned = set(flatten(s.get_points_in_row(y) for s in swbs)) - beacons
    return len(scanned)


def day15_1b(swbs: list[SensorAndBeacon], y: int) -> int:
    beacons = set(map(attrgetter('beacon'), swbs))
    x_bounds = [xb for swb in swbs if (xb := swb.get_x_bounds(y))]
    ranges = {x_bounds[0]}
    for x_min, x_max in x_bounds[1:]:
        to_remove = set()
        for r in ranges:
            r_min, r_max = r
            match (x_min <= r_min <= x_max, x_min <= r_max <= x_max):
                case True, True:
                    to_remove.add(r)
                case True, False:
                    to_remove.add(r)
                    x_max = r_max
                case False, True:
                    to_remove.add(r)
                    x_min = r_min
                case False, False if (r_min < x_min < r_max and r_min < x_max < r_max):
                    x_min, x_max = r_min, r_max
                    break
        ranges -= to_remove
        ranges |= {(x_min, x_max)}
    scanned = {Point(x, y) for r_min, r_max in ranges for x in range(r_min, r_max + 1)}
    return len(scanned - beacons)


def day15_2a(swbs: list[SensorAndBeacon]):
    # 56000011 or 10291582906626
    xy_range = range(21)
    edges = Counter()
    checked = set()
    for s in swbs:
        edges.update(set(s.get_edge_points(xy_range)) - checked)
        to_check = [e for e in edges if edges[e] >= 4]
        for p in to_check:
            if any(swb.in_range(p) for swb in swbs):
                checked.add(p)
                del edges[p]
            else:
                return f'{p.x * 4000000 + p.y} {p}'

    # edges = set(flatten(s.get_edge_points() for s in swbs))
    # edges = set(swbs[0].get_edge_points())
    # points = [p for y in xy_range for x in xy_range if not any(s.in_range((p := Point(x, y))) for s in swbs)]
    return "Couldn't find the beacon"


if __name__ == '__main__':
    # 26 or 5403290
    # 56000011 or 10291582906626
    from timeit import timeit
    import gc
    n = 1000000
    data = get_sensors_with_beacons()
    cmds = ['day15_1a(data, 10)', 'day15_1b(data, 10)']
    for cmd in cmds:
        print(f'{cmd} = {eval(cmd)}')
        print(f'{n} runs in: {timeit(cmd, "gc.enable()", globals=globals(), number=n)}s\n')
