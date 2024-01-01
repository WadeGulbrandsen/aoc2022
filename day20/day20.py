from collections import deque


def get_ints(filename) -> list[int]:
    with open(filename) as f:
        return list(map(int, f.read().split()))


def decrypt(numbers: list[int], mixes: int = 1, key: int = 0) -> int:
    keyed = numbers
    if key:
        keyed = list(map(lambda num: num * key, numbers))
    dq = deque(range(len(keyed)), maxlen=len(keyed))
    for _ in range(mixes):
        for i, n in enumerate(keyed):
            position = dq.index(i)
            dq.rotate(-position)
            x = keyed[dq.popleft()]
            assert x == n
            dq.rotate(-x)
            dq.appendleft(i)
    zero = dq.index(keyed.index(0))
    dq.rotate(-zero)
    coordinates = [keyed[dq[x % len(dq)]] for x in [1000, 2000, 3000]]
    return sum(coordinates)


if __name__ == '__main__':
    ints = get_ints('day20input.txt')
    print(f'Part 1: {decrypt(ints, 1)}')
    print(f'Part 2: {decrypt(ints, 10, 811589153)}')
