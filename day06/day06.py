def day06_1():
    with open('day06input.txt') as f:
        seq = f.read().strip()
    #seq = 'zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw'
    for i in range(4, len(seq)):
        last4 = seq[i - 4:i]
        unique = set(last4)
        if len(unique) == 4:
            return i
    return 0


def day06_2():
    with open('day06input.txt') as f:
        seq = f.read().strip()
    for i in range(14, len(seq)):
        last14 = seq[i - 14:i]
        unique = set(last14)
        if len(unique) == 14:
            return i
    return 0


if __name__ == '__main__':
    print(day06_2())
