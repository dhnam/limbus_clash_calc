
from typing import Literal

LanguageType = Literal['kr'] | Literal['en']
SentencePair = dict[LanguageType, str]
Translation = dict[str, SentencePair]

skill_trans: Translation = {
    'character': {'kr': '캐릭터 %d', 'en': 'Character %d'},
    'base': {'kr': '스킬 위력', 'en': 'Skill power'},
    'count': {'kr': '코인 갯수', 'en': 'Coin count'},
    'coin': {'kr': '코인 위력', 'en': 'Coin power'},
    'sanity': {'kr': '정신력', 'en': 'Sanity'},
    'winrate': {'kr': '승률:', 'en': 'Win rate:'},
    'avgpower': {'kr': '위력 기댓값:', 'en': 'Expected Power:'},
}

detail_trans: Translation = {
    'character': {'kr': '캐릭터 %d', 'en': 'Character %d'},
    'coins': {'kr': '남은 코인 %d개로 승리: %f%%', 'en': 'Win with %d coin(s) left: %f%%'},
    'winrate': {'kr': '총 승률: %f%%', 'en': 'Net. Winrate: %f%%'},
}

title_trans: Translation = {
    'main': {'kr': '림버스 합 승률 계산기', 'en': 'Limbus Clash Winrate Calculator'},
    'detail': {'kr': '상세정보', 'en': 'Detailed Information'},
}

main_ui_trans: Translation = {
    'calc': {'kr': '계산', 'en': 'Calculate'},
    'detail': {'kr': '상세 정보', 'en': 'Detail'},
    'language': {'kr': 'English', 'en': '한국어'},
    'change': {'kr': 'Change language', 'en': '언어 변경'}
}

detail_ui_trans: Translation = {
    'exit': {'kr': '확인', 'en': 'OK'}
}

error_trans: SentencePair = {
    'kr': '숫자를 입력해주세요',
    'en': 'Please input the number',
}
