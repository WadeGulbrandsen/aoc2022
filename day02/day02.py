from typing import List, Tuple, Dict


def read_and_play(shape_scores: Dict[str, int], outcome_scores: Dict[str, Dict[str, int]]
                  ) -> List[Tuple[str, str, int, int]]:
    data = []
    with open('day02input.txt') as f:
        for line in f:
            data.append(play_round(shape_scores, outcome_scores, line[0], line[2]))
    return data


def play_round(shape_scores: Dict[str, int], outcome_scores: Dict[str, Dict[str, int]], opponent: str, player: str
               ) -> Tuple[str, str, int, int]:
    return opponent, player, shape_scores[player], outcome_scores[opponent][player]


def score_round(outcome: Tuple[str, str, int, int]) -> int:
    _opponent, _player, shape_score, outcome_score = outcome
    return shape_score + outcome_score


def day02_1() -> int:
    shape_scores = {'X': 1, 'Y': 2, 'Z': 3}
    outcome_scores = {'A': {'X': 3, 'Y': 6, 'Z': 0},
                      'B': {'X': 0, 'Y': 3, 'Z': 6},
                      'C': {'X': 6, 'Y': 0, 'Z': 3}}
    return sum(map(score_round, read_and_play(shape_scores, outcome_scores)))


def day02_2() -> int:
    shape_scores = {'X': 0, 'Y': 3, 'Z': 6}
    outcome_scores = {'A': {'X': 3, 'Y': 1, 'Z': 2},
                      'B': {'X': 1, 'Y': 2, 'Z': 3},
                      'C': {'X': 2, 'Y': 3, 'Z': 1}}
    return sum(map(score_round, read_and_play(shape_scores, outcome_scores)))


if __name__ == '__main__':
    print(day02_2())
