from typing import List


def day01_read_data() -> List[int]:
    totals = [0]
    index = 0
    with open('day 01-1 input.txt') as f:
        for line in f:
            data = line.strip()
            try:
                totals[index] += int(data)
            except ValueError:
                index += 1
                totals.append(0)
    return totals


def day01_1() -> int:
    totals = day01_read_data()
    return max(totals)


def day01_2() -> int:
    totals = sum(sorted(day01_read_data(), reverse=True)[:3])
    return totals


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(day01_1())
    print(day01_2())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
