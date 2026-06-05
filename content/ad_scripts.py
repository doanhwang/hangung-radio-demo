"""
한궁 F&B 라디오 - 광고·후원 포맷 샘플 스크립트
4가지 포맷 각 1개씩
"""

AD_SAMPLES = {

    "AD_F01": {
        "name": "스폰서 오프닝 멘트",
        "format": "Format 01 · 방송 내 음성",
        "duration": "5~10초",
        "position": "방송 시작 전",
        "text": """
오늘 한궁 칭찬 라디오는 종근당 건강과 함께합니다.
어르신들의 건강한 하루를, 종근당 건강이 응원합니다.
        """.strip(),
        "filename": "HANGUNG_AD_F01_SPONSOR_OPENING_20260606_v1.mp3"
    },

    "AD_F02": {
        "name": "중간 CM송",
        "format": "Format 02 · 방송 내 음성",
        "duration": "15~30초",
        "position": "S3(노래소개)와 S4(노래재생) 사이",
        "text": """
한화생명 요양보험.
부모님이 오래도록 건강하게, 가족이 안심할 수 있도록.
한화생명 요양보험은 어르신의 내일을 함께 준비합니다.
지금 지도사 선생님께 물어보세요.
한화생명 요양보험, 가족이 안심하는 선택입니다.
        """.strip(),
        "filename": "HANGUNG_AD_F02_CM_SONG_20260606_v1.mp3"
    },

    "AD_F03": {
        "name": "클로징 협찬 안내",
        "format": "Format 03 · 방송 내 음성",
        "duration": "10~15초",
        "position": "S5(클로징) 마지막",
        "text": """
오늘 방송을 후원해 주신 벨톤 보청기에 감사드립니다.
더 잘 들리는 하루, 더 선명하게 연결되는 가족의 목소리.
벨톤 보청기와 함께하세요.
        """.strip(),
        "filename": "HANGUNG_AD_F03_CLOSING_SPONSOR_20260606_v1.mp3"
    },

    "AD_F04": {
        "name": "프로그램 단독 후원 오프닝",
        "format": "Format 04 · 프로그램 단위",
        "duration": "15~20초",
        "position": "프로그램 전체 단독 후원 — 매 에피소드 오프닝",
        "text": """
삼성생명이 함께하는 부모님 안부 라디오.
멀리 있어도 마음은 가깝게, 가족의 사랑을 소리로 전합니다.
오늘도 삼성생명 부모님 안부 라디오와 함께해 주셔서 감사합니다.
부모님의 건강한 내일, 삼성생명이 함께 지킵니다.
        """.strip(),
        "filename": "HANGUNG_AD_F04_PROGRAM_SPONSOR_20260606_v1.mp3"
    },
}
