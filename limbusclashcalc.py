from dataclasses import dataclass
from functools import lru_cache
import itertools
from itertools import product
from math import comb
import numpy as np

@dataclass(unsafe_hash=True)
class Skill:
    base_coin: int
    coin_val: int
    coin_count: int
    sanity: int
    paralyze: int = 0

    @property
    @lru_cache(1)
    def head_prob(self) -> float:
        return (50 + self.sanity) / 100
    
    @property
    @lru_cache(1)
    def prob_list(self) -> list[tuple[int, float]]:
        coin_flipped = max(0, self.coin_count - self.paralyze)
        return sorted(
            [
                (max(0, self.base_coin + self.coin_val * i),
                 self.head_prob ** i\
                 * (1 - self.head_prob) ** (coin_flipped - i)\
                 * comb(coin_flipped, i))
                 for i in range(coin_flipped + 1)
            ]
            , key=lambda x: x[0])
    
    @property
    @lru_cache(1)
    def possible_paralyzes(self) -> list[int]:
        res = set([0])
        curr = set([self.paralyze])
        curr_before = set([])
        possible_coins = [self.coin_count]
        while curr != set([0]) and curr != curr_before:
            curr_before = curr
            res |= curr
            curr = set(max(i - j, 0) for i, j in product(curr_before, possible_coins))
            if possible_coins[-1] > 1:
                possible_coins.append(possible_coins[-1] - 1)
        return list(res)
    
@dataclass(unsafe_hash=True)
class ProbResult:
    probability: float
    coin_count: int
    paralyze: int
    opp_paralyze: int

    def __str__(self) -> str:
        return f"<Coin {self.coin_count}: {self.probability}{' (paralyze ' + str(self.paralyze) + ')' if self.paralyze != 0 else ''}{' (opponenet paralyze ' + str(self.opp_paralyze) + ')' if self.opp_paralyze != 0 else ''}>"
    
    def __repr__(self) -> str:
        return str(self)
    
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
    base_left_paralyzes = left.possible_paralyzes
    left_paralyzes_count = len(base_left_paralyzes)
    base_right_paralyzes = right.possible_paralyzes
    right_paralyzes_count = len(base_right_paralyzes)
    base_matrix = np.zeros((left.coin_count + 1, left_paralyzes_count,
                            right.coin_count + 1, right_paralyzes_count,
                            left.coin_count + 1, left_paralyzes_count,
                            right.coin_count + 1, right_paralyzes_count))
    # (before_left, before_left_paralyze, before_right, before_right_paralyze, after_left, after_left_paralyze, after_right, after_right_paralyze)
    for left_coins in range(left.coin_count + 1):
        for right_coins in range(right.coin_count + 1):
            for left_paralyze, right_paralyze in product(base_left_paralyzes, base_right_paralyzes):
                if max(right_paralyze - right_coins, 0) not in base_right_paralyzes\
                    or max(left_paralyze - left_coins, 0) not in base_left_paralyzes:
                    continue
                if left_coins == 0 or right_coins == 0:
                    base_matrix[left_coins, base_left_paralyzes.index(left_paralyze),
                                right_coins, base_right_paralyzes.index(right_paralyze),
                                left_coins, base_left_paralyzes.index(left_paralyze),
                                right_coins, base_right_paralyzes.index(right_paralyze)] = 1
                    continue
                new_left = Skill(left.base_coin, left.coin_val, left_coins, left.sanity, left_paralyze)
                new_right = Skill(right.base_coin, right.coin_val, right_coins, right.sanity, right_paralyze)
                l, d, r = single_clash_prob(new_left, new_right)
                base_matrix[
                    left_coins, base_left_paralyzes.index(left_paralyze),
                    right_coins, base_right_paralyzes.index(right_paralyze),
                    left_coins, base_left_paralyzes.index(max(left_paralyze - left_coins, 0)),
                    right_coins - 1, base_right_paralyzes.index(max(right_paralyze - right_coins, 0))] = l
                base_matrix[left_coins, base_left_paralyzes.index(left_paralyze),
                            right_coins, base_right_paralyzes.index(right_paralyze),
                            left_coins, base_left_paralyzes.index(max(left_paralyze - left_coins, 0)),
                            right_coins, base_right_paralyzes.index(max(right_paralyze - right_coins, 0))] = d
                base_matrix[left_coins, base_left_paralyzes.index(left_paralyze),
                            right_coins, base_right_paralyzes.index(right_paralyze),
                            left_coins - 1, base_left_paralyzes.index(max(left_paralyze - left_coins, 0)),
                            right_coins, base_right_paralyzes.index(max(right_paralyze - right_coins, 0))] = r
    paralyze_product = left_paralyzes_count * right_paralyzes_count
    return base_matrix.reshape((left.coin_count + 1) * (right.coin_count + 1) * paralyze_product,
                               (left.coin_count + 1) * (right.coin_count + 1) * paralyze_product)

def power_until_steady(matrix: np.ndarray) -> np.ndarray:
    mat_before = np.zeros_like(matrix)
    while not np.array_equal(mat_before, matrix):
        mat_before = matrix
        matrix = matrix @ matrix
    return matrix

def get_result_matrix(left: Skill, right: Skill) -> np.ndarray:
    base_left_paralyzes = left.possible_paralyzes
    left_paralyzes_count = len(base_left_paralyzes)
    base_right_paralyzes = right.possible_paralyzes
    right_paralyzes_count = len(base_right_paralyzes)
    # print(power_until_steady(clash_matrix(left, right))[-1])
    return power_until_steady(clash_matrix(left, right))[-1].reshape(((left.coin_count + 1) * left_paralyzes_count, (right.coin_count + 1) * right_paralyzes_count))

def repeat_elements(lst, n):
    return list(itertools.chain.from_iterable(itertools.repeat(x, n) for x in lst))

def win_probability(left: Skill, right: Skill) -> tuple[list[ProbResult], list[ProbResult]]:
    res = get_result_matrix(left, right)
    base_left_paralyzes = left.possible_paralyzes
    base_right_paralyzes = right.possible_paralyzes
    left_prob_list: list[ProbResult] = []
    right_prob_list: list[ProbResult] = []
    for i, next_left_win in enumerate(res.T[:len(base_right_paralyzes)]):
        left_prob_list.extend([ProbResult(prob, coin, paralyze, base_right_paralyzes[i]) for prob, coin, paralyze in
                              zip(next_left_win[len(base_left_paralyzes):],
                              repeat_elements(range(1, left.coin_count + 1), len(base_left_paralyzes)),
                              base_left_paralyzes * (left.coin_count + 1)) if prob != 0])
        
    for i, next_right_win in enumerate(res[:len(base_left_paralyzes)]):
        right_prob_list.extend([ProbResult(prob, coin, paralyze, base_left_paralyzes[i]) for prob, coin, paralyze in
                               zip(next_right_win[len(base_right_paralyzes):],
                               repeat_elements(range(1, right.coin_count + 1), len(base_right_paralyzes)),
                               base_right_paralyzes * (right.coin_count + 1)) if prob != 0])

    return left_prob_list, right_prob_list

def total_avg_power(skill: Skill, prob: list[ProbResult]) -> float:
    res: float = 0
    coin_power: list[float] = []
    for next_prob in prob:
        count = next_prob.coin_count
        p = next_prob.probability
        paralyze = next_prob.paralyze
        power = skill.base_coin + max(count - paralyze, 0) * skill.coin_val * skill.head_prob
        power = max(0, power)
        coin_power.append(power)
        res += p * sum(coin_power)
    return res

if __name__ == "__main__":
    skill_a = Skill(30, -12, 4, 0, 13)
    skill_b = Skill(33, -4, 3, 0)
    # skill_a = Skill(5, 3, 2, 0, 4)
    # skill_b = Skill(2, 4, 2, 0, 0)
    # np.set_printoptions(threshold=40000, linewidth=1000, formatter={'float_kind':lambda x: '{0:0.1f}'.format(x)})
    # print(clash_matrix(skill_a, skill_b))
    # test = np.zeros((2,2,1,2,2,2,1,2))
    # for i, (a, b, c, d, e, f, g, h) in enumerate(product(range(2), range(2), range(1), range(2), range(2), range(2), range(1), range(2))):
        # test[a,b,c,d,e,f,g,h] = 10000000*a + 1000000*b + 100000*c + 10000 *d + 1000 * e + 100 *f + 10 * g + h
    # print(test.reshape(8,8)[-1].reshape(4,2))
    print(get_result_matrix(skill_a, skill_b))
    print(win_probability(skill_a, skill_b))
    print(total_avg_power(skill_a, win_probability(skill_a, skill_b)[0]))