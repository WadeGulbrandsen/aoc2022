import re
from typing import Dict, List

pattern = re.compile(r'move (?P<num>\d+) from (?P<source>\d+) to (?P<target>\d+)')


def day05_1():
    stacks = []
    state: Dict[str, List[str]]
    with open('day05input.txt') as f:
        while True:
            line = f.readline().rstrip()
            if line.startswith(' 1 '):
                key_line = line
                stacks.reverse()
                state = {
                    stack: [c for l in stacks if len(l) > pos and (c := l[pos]) != ' ']
                    for pos, stack in enumerate(key_line) if stack != ' '
                }
                break
            stacks.append(line)
        for line in f:
            if match := pattern.fullmatch(line.strip()):
                for _ in range(int(match.groupdict()['num'])):
                    crate = state[match.groupdict()['source']].pop()
                    state[match.groupdict()['target']].append(crate)
    return ''.join([c[-1] for c in state.values()])


def day05_2():
    stacks = []
    state: Dict[str, List[str]]
    with open('day05input.txt') as f:
        while True:
            line = f.readline().rstrip()
            if line.startswith(' 1 '):
                key_line = line
                stacks.reverse()
                state = {
                    stack: [c for l in stacks if len(l) > pos and (c := l[pos]) != ' ']
                    for pos, stack in enumerate(key_line) if stack != ' '
                }
                break
            stacks.append(line)
        for line in f:
            if match := pattern.fullmatch(line.strip()):
                num = int(match.groupdict()['num'])
                crates = state[match.groupdict()['source']][-num:]
                state[match.groupdict()['source']] = state[match.groupdict()['source']][:-num]
                state[match.groupdict()['target']].extend(crates)

    return ''.join([c[-1] for c in state.values()])


if __name__ == '__main__':
    print(day05_2())