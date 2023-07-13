from dataclasses import dataclass
from functools import lru_cache
from math import comb
import numpy as np

@dataclass(unsafe_hash=True)
class Skill:
    base_coin: int
    coin_val: int
    coin_count: int
    sanity: int

    @property
    @lru_cache(1)
    def head_prob(self) -> float:
        return (50 + self.sanity) / 100
    
    @property
    @lru_cache(1)
    def prob_list(self) -> list[tuple[int, float]]:
        return sorted(
            [
                (self.base_coin + self.coin_val * i,
                 self.head_prob ** i * (1 - self.head_prob) ** (self.coin_count - i) * comb(self.coin_count, i))
                 for i in range(self.coin_count + 1)
            ]
            , key=lambda x: x[0])

def single_clash_prob(left: Skill, right: Skill) -> tuple[float, float, float]:
    left_winrate: float = 0
    draw_rate: float = 0
    right_winrate: float = 0
    right_accm: float = 0
    for left_val, left_prob in left.prob_list:
        right_accm = 0
        for right_val, right_prob in right.prob_list:
            if left_val < right_val:
                right_winrate += left_prob * (1 - right_accm)
                break
            if left_val == right_val:
                draw_rate += left_prob * right_prob
            right_accm += right_prob
            if left_val > right_val:
                left_winrate += left_prob * right_prob
    return left_winrate, draw_rate, right_winrate


def clash_matrix(left: Skill, right: Skill) -> np.ndarray:
    base_matrix = np.zeros((left.coin_count + 1, right.coin_count + 1, left.coin_count + 1, right.coin_count + 1))
    for left_coins in range(left.coin_count + 1):
        for right_coins in range(right.coin_count + 1):
            if left_coins == 0 or right_coins == 0:
                base_matrix[left_coins, right_coins, left_coins, right_coins] = 1
                continue
            new_left = Skill(left.base_coin, left.coin_val, left_coins, left.sanity)
            new_right = Skill(right.base_coin, right.coin_val, right_coins, right.sanity)
            l, d, r = single_clash_prob(new_left, new_right)
            base_matrix[left_coins, right_coins, left_coins, right_coins - 1] = l
            base_matrix[left_coins, right_coins, left_coins, right_coins] = d
            base_matrix[left_coins, right_coins, left_coins - 1, right_coins] = r
    return base_matrix.reshape((left.coin_count + 1) * (right.coin_count + 1), (left.coin_count + 1) * (right.coin_count + 1))

def power_until_steady(matrix: np.ndarray) -> np.ndarray:
    mat_before = np.zeros_like(matrix)
    while not np.array_equal(mat_before, matrix):
        mat_before = matrix
        matrix = matrix @ matrix
    return matrix

def get_result_matrix(left: Skill, right: Skill) -> np.ndarray:
    return power_until_steady(clash_matrix(left, right))[-1].reshape((left.coin_count + 1, right.coin_count + 1))

def win_probability(left: Skill, right: Skill) -> tuple[list[float], list[float]]:
    res = get_result_matrix(left, right)
    return list(res.T[0]), list(res[0])

def total_avg_power(skill: Skill, prob: list[float]) -> float:
    res: float = 0
    coin_power: list[float] = []
    for i, p in enumerate(prob):
        if i == 0:
            continue
        power = skill.base_coin + i * skill.coin_val * skill.head_prob
        if power < 0:
            power = 0
        coin_power.append(power)
        res += p * sum(coin_power)
    return res