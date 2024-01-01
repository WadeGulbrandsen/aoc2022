from dataclasses import dataclass
from functools import cached_property

SNAFU_DIGIT = {'=': -2, '-': -1} | {str(x): x for x in range(3)}
SNAFU_CHAR = list(SNAFU_DIGIT.keys())
SNAFU_BASE = len(SNAFU_CHAR)
SNAFU_ZERO_OFFSET = SNAFU_CHAR.index('0')


@dataclass(order=True, frozen=True)
class SNAFU:
    snafu: str

    def __str__(self):
        return f'{self.snafu}: {self.value}'

    def __repr__(self):
        return f'SNAFU {self.snafu}: {self.value}'

    @cached_property
    def value(self) -> int:
        value = 0
        for i, x in enumerate(reversed(self.snafu)):
            place = SNAFU_BASE ** i
            value += place * SNAFU_DIGIT[x]
        return value

    @staticmethod
    def from_int(v: int) -> 'SNAFU':
        snafu = ''
        while v:
            shift = (v + SNAFU_ZERO_OFFSET) % SNAFU_BASE
            snafu += SNAFU_CHAR[shift]
            if shift < SNAFU_ZERO_OFFSET:
                v += SNAFU_BASE
            v //= SNAFU_BASE
        return SNAFU(snafu[::-1])


def read_numbers(filename: str) -> list[SNAFU]:
    with open(filename) as f:
        file = f.read().splitlines()
        f.close()
    return [SNAFU(line) for line in file]


if __name__ == '__main__':
    sample_snafus = read_numbers('sample.txt')
    sample_answer = SNAFU.from_int(sum(n.value for n in sample_snafus))
    print(f'Sample: {sample_answer}')
    assert sample_answer.snafu == '2=-1=0'

    input_snafus = read_numbers('input.txt')
    input_answer = SNAFU.from_int(sum(n.value for n in input_snafus))
    print(f'Input: {input_answer}')
    assert input_answer.snafu == '20=212=1-12=200=00-1'
