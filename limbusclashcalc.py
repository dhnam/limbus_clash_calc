from dataclasses import dataclass
from functools import lru_cache
from math import comb
import numpy as np
import PySimpleGUI as sg

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
    for i, p in enumerate(prob):
        power = skill.base_coin + i * skill.coin_val * skill.head_prob
        if power < 0:
            power = 0
        power_exp = p * power
        res += power_exp * (skill.coin_count - i + 1)
    return res

def skill_column(number:int):
 return [[sg.Text(f"캐릭터 {number}", size=10)],
         [sg.Text("스킬 위력", size=10), sg.Input(key=f"base{number}", size=7)],
         [sg.Text("코인 갯수", size=10), sg.Input(key=f"count{number}", size=7)],
         [sg.Text("코인 위력", size=10), sg.Input(key=f"coin{number}", size=7)],
         [sg.Text("정신력", size=10), sg.Input(key=f"sanity{number}", size=7)],
         [sg.Text("승률:", size=10), sg.Text("", key=f"winrate{number}", size=7)],
         [sg.Text("위력 기댓값:", size=10), sg.Text("", key=f"avgpower{number}", size=7)]]

def detail_column(number: int, res: list[float]):
    res_col = [[sg.Text(f"캐릭터 {number}")]]
    res_col.extend([[sg.Text(f"남은 코인 {i}개로 승리: {next_prob * 100}%")] for i, next_prob in enumerate(res) if i != 0])
    res_col.append([sg.Text(f"총 승률: {sum(res) * 100}%")])
    return res_col

sg.change_look_and_feel('SystemDefaultForReal')
layout = [[sg.Column(skill_column(1)), sg.Column(skill_column(2))],
          [sg.Button("계산", key="calc"), sg.Button("상세 정보", key="detail")]]
window = sg.Window("림버스 합 승률 계산기", layout, finalize=True)
                   
window2 = None
while True:
    win, event, values = sg.read_all_windows()
    if event == sg.WIN_CLOSED or event == 'Exit':
        win.close()
        if win == window2:
            window2 = None
        else:
            break
    if event == "calc" or event == "detail":
        try:
            skill_a = Skill(int(values['base1']), int(values['coin1']), int(values['count1']), int(values['sanity1']))
            skill_b = Skill(int(values['base2']), int(values['coin2']), int(values['count2']), int(values['sanity2']))
        except ValueError as e:
            sg.popup("숫자를 입력해주세요.")
            continue
        a_win, b_win = win_probability(skill_a, skill_b)
        win["winrate1"].update(f"{sum(a_win) * 100:.3f}%")
        win["winrate2"].update(f"{sum(b_win) * 100:.3f}%")
        win["avgpower1"].update(f"{total_avg_power(skill_a, a_win):.3f}")
        win["avgpower2"].update(f"{total_avg_power(skill_b, b_win):.3f}")
        if event == "detail":
            if window2 is not None:
                continue
            window2 = sg.Window("상세정보", 
                                   [
                                       [sg.Column([[sg.Column(detail_column(1, a_win)), sg.Column(detail_column(2, b_win))]], size=(None, 200), scrollable=True, vertical_scroll_only=True)],
                                       [sg.Exit('확인', key="Exit")]
                                   ], finalize=True)

window.close()
