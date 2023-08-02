import PySimpleGUI as sg
from limbusclashcalc import *
from translation import *

# TODO Add Paralyze
def skill_column(number:int, language:LanguageType):
    return [[sg.Text(skill_trans['character'][language] % (number), size=15)],
            [sg.Text(skill_trans['base'][language], size=15), sg.Input(key=f"base{number}", size=7)],
            [sg.Text(skill_trans['count'][language], size=15), sg.Input(key=f"count{number}", size=7)],
            [sg.Text(skill_trans['coin'][language], size=15), sg.Input(key=f"coin{number}", size=7)],
            [sg.Text(skill_trans['sanity'][language], size=15), sg.Input(key=f"sanity{number}", size=7)],
            [sg.Text(skill_trans['winrate'][language], size=15), sg.Text("", key=f"winrate{number}", size=7)],
            [sg.Text(skill_trans['avgpower'][language], size=15), sg.Text("", key=f"avgpower{number}", size=7)]]

# TODO fix this function to meet new signature of win_probability
def detail_column(number: int, res: list[float], language:LanguageType):
    res_col = [[sg.Text(detail_trans['character'][language] % (number))]]
    res_col.extend([[sg.Text(detail_trans['coins'][language] % (i, next_prob * 100))] for i, next_prob in enumerate(res) if i != 0])
    res_col.append([sg.Text(detail_trans['winrate'][language] % (sum(res) * 100))])
    return res_col

def main_layout(language:LanguageType):
    return [[sg.Menu([[main_ui_trans['language'][language], [main_ui_trans['change'][language] + "::language"]]])],
            [sg.Column(skill_column(1, language)), sg.Column(skill_column(2, language))],
            [sg.Button(main_ui_trans['calc'][language], key="calc"), sg.Button(main_ui_trans['detail'][language], key="detail")]]

def detail_layout(language:LanguageType):
    return [[sg.Column([[sg.Column(detail_column(1, a_win, language)), sg.Column(detail_column(2, b_win, language))]], size=(None, 200), scrollable=True, vertical_scroll_only=True)],
            [sg.Exit(detail_ui_trans['exit'][language], key="Exit")]]

sg.change_look_and_feel('SystemDefaultForReal')

curr_language: LanguageType = 'kr'

layout = main_layout(curr_language)
window = sg.Window(title_trans['main'][curr_language], layout, icon='images/logo.ico', titlebar_icon='images/logo.ico', finalize=True)
                   
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
            sg.popup(error_trans[curr_language])
            continue
        # TODO fix this to meet new signature of win_probability
        a_win, b_win = win_probability(skill_a, skill_b)
        win["winrate1"].update(f"{sum(a_win) * 100:.3f}%")
        win["winrate2"].update(f"{sum(b_win) * 100:.3f}%")
        win["avgpower1"].update(f"{total_avg_power(skill_a, a_win):.3f}")
        win["avgpower2"].update(f"{total_avg_power(skill_b, b_win):.3f}")
        if event == "detail":
            if window2 is not None:
                continue
            window2 = sg.Window(title_trans['detail'][curr_language], detail_layout(curr_language), icon='images/logo.ico', titlebar_icon='images/logo.ico', finalize=True)
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