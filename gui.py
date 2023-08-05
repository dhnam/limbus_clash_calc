from functools import reduce
from enum import Enum
import PySimpleGUI as sg
from limbusclashcalc import *
from translation import *

class detailParaCalc(Enum):
    PARA_NONE = 1
    PARA_SELF = 2
    PARA_ALL = 3

def skill_column(number:int, language:LanguageType):
    return [[sg.Text(skill_trans['character'][language] % (number), size=15)],
            [sg.Text(skill_trans['base'][language], size=15), sg.Input(key=f"base{number}", size=7)],
            [sg.Text(skill_trans['count'][language], size=15), sg.Input(key=f"count{number}", size=7)],
            [sg.Text(skill_trans['coin'][language], size=15), sg.Input(key=f"coin{number}", size=7)],
            [sg.Text(skill_trans['sanity'][language], size=15), sg.Spin(list(range(-45, 46)), 0, key=f"sanity{number}", size=5)],
            [sg.Text(skill_trans['paralyze'][language], size=15), sg.Input("0", key=f"paralyze{number}", size=7)],
            [sg.Text(skill_trans['winrate'][language], size=15), sg.Text("", key=f"winrate{number}", size=7)],
            [sg.Text(skill_trans['avgpower'][language], size=15), sg.Text("", key=f"avgpower{number}", size=7)]]

def detail_column(number: int, res: list[ProbResult], language:LanguageType, detail_type:detailParaCalc=detailParaCalc.PARA_NONE):
    res_col = [[sg.Text(detail_trans['character'][language] % (number))]]
    prob_summary: list[tuple[int, float]] = []
    for next_prob_res in res:
        for i, next_summary in enumerate(prob_summary):
            if next_summary[0] == next_prob_res.coin_count:
                prob_summary[i] = (next_summary[0], next_summary[1] + next_prob_res.probability)
                break
        else:
            prob_summary.append((next_prob_res.coin_count, next_prob_res.probability))
    if detail_type == detailParaCalc.PARA_NONE:
        res_col.extend([[sg.Text(detail_trans['coins'][language] % (coin, prob * 100))]
                        for coin, prob in prob_summary])
    elif detail_type == detailParaCalc.PARA_SELF:
        para_self_prob: list[tuple[int, int, float]] = []
        for next_prob_res in res:
            for i, next_para in enumerate(para_self_prob):
                if next_para[0] == next_prob_res.coin_count and next_para[1] == next_prob_res.paralyze:
                    para_self_prob[i] = (next_para[0], next_para[1], next_para[2] + next_prob_res.probability)
                    break
            else:
                para_self_prob.append((next_prob_res.coin_count, next_prob_res.paralyze, next_prob_res.probability))
        i, j = 0, 0
        while i < len(prob_summary):
            res_col.append([sg.Text(detail_trans['coins'][language] % (prob_summary[i][0], prob_summary[i][1] * 100))])
            while j < len(para_self_prob) and para_self_prob[j][0] == prob_summary[i][0]:
                res_col.append([sg.Text("   " + detail_trans['para_self'][language] % (para_self_prob[j][1], para_self_prob[j][2] * 100))])
                j += 1
            i += 1
    else:
        res = sorted(res, key=lambda x: x.coin_count)
        i, j = 0, 0
        while i < len(prob_summary):
            res_col.append([sg.Text(detail_trans['coins'][language] % (prob_summary[i][0], prob_summary[i][1] * 100))])
            while j < len(res) and res[j].coin_count == prob_summary[i][0]:
                res_col.append([sg.Text("   " + detail_trans['para_all'][language] % (res[j].paralyze, res[j].opp_paralyze, res[j].probability * 100))])
                j += 1
            i += 1

    zero_res = ProbResult(0, 0, 0, 0)
    res_col.append([sg.VPush()])
    res_col.append([sg.Text(detail_trans['winrate'][language] % (reduce(ProbResult.add_prob, res, zero_res).probability * 100))])
    return res_col

def main_layout(language:LanguageType):
    return [[sg.Menu([[main_ui_trans['language'][language], [main_ui_trans['change'][language] + "::language"]]])],
            [sg.Column(skill_column(1, language)), sg.Column(skill_column(2, language))],
            [sg.Button(main_ui_trans['calc'][language], key="calc"), sg.Button(main_ui_trans['detail'][language], key="detail")]]

def detail_layout(a_prob: list[ProbResult], b_prob: list[ProbResult], language:LanguageType, detail_type:detailParaCalc=detailParaCalc.PARA_NONE):
    return [[sg.Column([[sg.Column(detail_column(1, a_prob, language, detail_type), expand_y=True), sg.Column(detail_column(2, b_prob, language, detail_type), expand_y=True)]], size=(None, 200), scrollable=True, vertical_scroll_only=True)],
            [sg.Text(detail_ui_trans['para_info'][language])],
            [sg.Radio(detail_ui_trans['para_none'][language], "para", default=True, enable_events=True, key="para_none"),
             sg.Radio(detail_ui_trans['para_self'][language], "para", enable_events=True, key="para_self"),
             sg.Radio(detail_ui_trans['para_all'][language], "para", enable_events=True, key="para_all")],
            [sg.Exit(detail_ui_trans['exit'][language], key="Exit")]]

sg.change_look_and_feel('SystemDefaultForReal')

curr_language: LanguageType = 'kr'

layout = main_layout(curr_language)
window: sg.Window = sg.Window(title_trans['main'][curr_language], layout, icon='images/logo.ico', titlebar_icon='images/logo.ico', finalize=True)
                   
window2: sg.Window | None = None

while True:
    win, event, values = sg.read_all_windows()
    if event == sg.WIN_CLOSED or event == 'Exit':
        win.close()
        if win == window2:
            window2 = None
        else:
            break
    if event in ('calc', 'detail'):
        try:
            skill_a = Skill(int(values['base1']), int(values['coin1']), int(values['count1']), int(values['sanity1']), int(values['paralyze1']))
            skill_b = Skill(int(values['base2']), int(values['coin2']), int(values['count2']), int(values['sanity2']), int(values['paralyze2']))
        except ValueError as e:
            sg.popup(error_trans[curr_language])
            continue
        a_win, b_win = win_probability(skill_a, skill_b)
        zero_res = ProbResult(0,0,0,0)
        win["winrate1"].update(f"{reduce(ProbResult.add_prob, a_win, zero_res).probability * 100:.3f}%")
        win["winrate2"].update(f"{reduce(ProbResult.add_prob, b_win, zero_res).probability * 100:.3f}%")
        win["avgpower1"].update(f"{total_avg_power(skill_a, a_win):.3f}")
        win["avgpower2"].update(f"{total_avg_power(skill_b, b_win):.3f}")
        if event == "detail":
            if window2 is not None:
                continue
            window2 = sg.Window(title_trans['detail'][curr_language], detail_layout(a_win, b_win, curr_language), icon='images/logo.ico', titlebar_icon='images/logo.ico', finalize=True)
    if event == "para_none":
        win2_before = window2
        win2_loc = win2_before.current_location()
        window2 = sg.Window(
            title_trans['detail'][curr_language],
            detail_layout(a_win, b_win, curr_language, detailParaCalc.PARA_NONE),
            icon='images/logo.ico',
            titlebar_icon='images/logo.ico',
            location=win2_loc,
            finalize=True)
        window2["para_none"].update(value=True)
        win2_before.close()
    if event == "para_self":
        win2_before = window2
        win2_loc = win2_before.current_location()
        window2 = sg.Window(
            title_trans['detail'][curr_language],
            detail_layout(a_win, b_win, curr_language, detailParaCalc.PARA_SELF),
            icon='images/logo.ico',
            titlebar_icon='images/logo.ico',
            location=win2_loc,
            finalize=True)
        window2["para_self"].update(value=True)
        win2_before.close()
    if event == "para_all":
        win2_before = window2
        win2_loc = win2_before.current_location()
        window2 = sg.Window(
            title_trans['detail'][curr_language],
            detail_layout(a_win, b_win, curr_language, detailParaCalc.PARA_ALL),
            icon='images/logo.ico',
            titlebar_icon='images/logo.ico',
            location=win2_loc,
            finalize=True)
        window2["para_all"].update(value=True)
        win2_before.close()
    if event is not None and event.split("::")[-1] == "language":
        if curr_language == 'kr':
            curr_language = 'en'
        else:
            curr_language = 'kr'
        win_before = window
        loc = win_before.current_location()
        foc = win_before.find_element_with_focus().key
        window = sg.Window(title_trans['main'][curr_language], main_layout(curr_language), icon='images/logo.ico', titlebar_icon='images/logo.ico', location=loc, finalize=True)
        del values[0]
        window.fill(values)
        window["winrate1"].update(win_before["winrate1"].get())
        window["winrate2"].update(win_before["winrate2"].get())
        window["avgpower1"].update(win_before["avgpower1"].get())
        window["avgpower2"].update(win_before["avgpower2"].get())
        window[foc].set_focus()
        win_before.close()

window.close()