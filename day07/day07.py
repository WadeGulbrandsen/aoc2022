from __future__ import annotations
from functools import reduce
from operator import getitem, itemgetter, attrgetter
import re
from pathlib import PurePosixPath
from pprint import pprint
from typing import Dict, Union, Tuple, List, NamedTuple
from dataclasses import dataclass

from more_itertools import partition

cd_pattern = re.compile(r'\$ cd (?P<dir>\S+)')
dir_pattern = re.compile(r'dir (?P<dir>\S+)')
file_pattern = re.compile(r'(?P<size>\d+) (?P<name>\S+)')


@dataclass
class File:
    path: PurePosixPath
    name: str
    size: int


@dataclass
class Directory:
    path: PurePosixPath
    name: str
    children: Dict[str, Union[Directory, File]]
    size: int = 0


def get_by_path(root: Directory, path: List[str]) -> Union[Directory, File, None]:
    def __get_child(directory: Directory, item: str) -> Union[Directory, File]:
        if directory.name == item:
            return directory
        return directory.children.get(item)
    return reduce(__get_child, path, root)


def build_fs():
    root = Directory(PurePosixPath('/'), '/', {})
    path = []
    current: Directory
    with open('day07input.txt') as f:
        for line in f:
            line = line.strip()
            if line == '$ ls':
                current = get_by_path(root, path)
            elif line.startswith('$ cd'):
                if match := cd_pattern.fullmatch(line):
                    directory = match.groupdict()['dir']
                    if directory == '/':
                        path = ['/']
                    elif directory == '..':
                        path = path[:-1]
                    else:
                        path.append(directory)
            else:
                if match := dir_pattern.fullmatch(line):
                    name = match.groupdict()['dir']
                    current.children[name] = Directory(current.path / name, name, {})
                elif match := file_pattern.fullmatch(line):
                    name = match.groupdict()['name']
                    size = int(match.groupdict()['size'])
                    current.children[name] = File(current.path / name, name, size)
    return root


def compute_sizes(directory: Directory) -> Directory:
    for child in directory.children.values():
        if type(child) == Directory:
            compute_sizes(child)
    total = sum(map(attrgetter('size'), directory.children.values()))
    directory.size = total
    return directory


def get_all_dirs(root: Directory) -> List[Directory]:
    all_dirs: List[Directory] = []

    def __get_dirs(item: Union[Directory, File]):
        if isinstance(item, Directory):
            all_dirs.append(item)
            for child in item.children.values():
                __get_dirs(child)

    __get_dirs(root)

    return all_dirs


def day07_1() -> int:
    all_dirs = get_all_dirs(compute_sizes(build_fs()))
    at_most_100000 = [size for directory in all_dirs if (size := directory.size) <= 100000]
    return sum(at_most_100000)


def day07_2():
    capacity = 70000000
    needed_free = 30000000
    root = compute_sizes(build_fs())
    used = root.size
    current_free = capacity - used
    need_to_free = needed_free - current_free
    pad = len(f'{capacity:,d}')
    at_least_needed = sorted([d for d in get_all_dirs(root) if d.size >= need_to_free], key=attrgetter('size'))
    to_be_deleted = at_least_needed[0]
    text_pad = max(len(str(to_be_deleted.path)), len('Size of disk'))
    return f'{"Size of disk":{text_pad}s}: {capacity:{pad},d}\n' \
           f'{"Current Free":{text_pad}s}: {current_free:{pad},d}\n' \
           f'{"Need to Free":{text_pad}s}: {need_to_free:{pad},d}\n' \
           f'{str(to_be_deleted.path):{text_pad}s}: {to_be_deleted.size:{pad},d}\n\n' \
           f'{to_be_deleted.size}'


if __name__ == '__main__':
    print(day07_2())
