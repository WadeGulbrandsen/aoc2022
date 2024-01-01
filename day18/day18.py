from pprint import pprint
import numpy as np
from numpy.typing import NDArray


def get_cubes(filename) -> NDArray[int]:
    with open(filename) as f:
        indexes = [tuple(map(int, line.strip().split(','))) for line in f]
    x, y, z = map(max, zip(*indexes))
    cubes = np.zeros((x + 1, y + 1, z + 1), int)
    for i, index in enumerate(indexes, 1):
        cubes[index] = i
    return cubes


def day18part1(cubes: NDArray[int]) -> int:
    padded = np.pad(cubes, 1)
    cis = np.argwhere(cubes > 0)
    pis = np.argwhere(padded)
    dirs = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]])
    covered = np.zeros(cubes.shape, int)
    for ci, pi in zip(cis, pis):
        neighbours = pi + dirs
        vals = [v for n in neighbours if (v := padded[*n])]
        covered[*ci] = len(vals)
    total_sides = cis.shape[0] * 6
    covered_sides = np.sum(covered)
    return total_sides - covered_sides


def day18part2(cubes: NDArray[int]) -> int:
    padded = np.pad(np.pad(cubes.astype(bool).astype(int), 1, constant_values=-1), 1, constant_values=-2)
    dirs = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]])
    while (wis := np.argwhere(padded == -1)).cube_size:
        air = {tuple(ai) for ai in np.argwhere(padded == 0)}
        new_water = set()
        for wi in wis:
            neighbours = {tuple(ni) for ni in wi + dirs}
            new_water |= neighbours & air
            padded[*wi] = -2
        for nw in new_water:
            padded[nw] = -1
    cis = np.argwhere(padded == 1)
    wis = {tuple(wi) for wi in np.argwhere(padded < 0)}
    exposed_to_water = np.zeros(padded.shape, int)
    for ci in cis:
        neighbours = {tuple(ni) for ni in ci + dirs}
        water = wis & neighbours
        exposed_to_water[*ci] = len(water)
    air = np.argwhere(padded == 0)
    air_pockets = air - 2
    sides_exposed = np.sum(exposed_to_water)
    return sides_exposed


if __name__ == '__main__':
    pprint(day18part2(get_cubes('day18input.txt')))
