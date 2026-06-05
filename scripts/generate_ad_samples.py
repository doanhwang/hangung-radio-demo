#!/usr/bin/env python3
"""
한궁 F&B 라디오 - 광고·후원 포맷 샘플 MP3 생성
실행: python scripts/generate_ad_samples.py
"""
import os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "content"))
from ad_scripts import AD_SAMPLES

from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "AD_samples"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 포맷별 목소리 — F01 밝고 자연스럽게, F02 경쾌하게, F03 따뜻하게, F04 품격있게
VOICE_MAP = {
    "AD_F01": "nova",    # 밝고 친근한 오프닝
    "AD_F02": "alloy",   # 경쾌한 CM
    "AD_F03": "shimmer", # 따뜻한 클로징
    "AD_F04": "nova",    # 품격있는 프로그램 후원
}

print("=" * 55)
print("한궁 F&B 라디오 — 광고·후원 포맷 샘플 MP3 생성")
print("=" * 55)

for ad_id, ad in AD_SAMPLES.items():
    out_path = OUTPUT_DIR / ad["filename"]
    print(f"\n[{ad_id}] {ad['name']}")
    print(f"  포맷: {ad['format']}")
    print(f"  위치: {ad['position']}")
    print(f"  [생성중] {ad['filename']}")

    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=VOICE_MAP[ad_id],
        input=ad["text"],
        speed=0.95,
    )
    audio_bytes = b"".join(response.iter_bytes())
    with open(out_path, "wb") as f:
        f.write(audio_bytes)

    size_kb = out_path.stat().st_size // 1024
    print(f"  [완료] {size_kb}KB")
    time.sleep(1)

print("\n" + "=" * 55)
print(f"저장 위치: {OUTPUT_DIR}")
print("생성 완료: 4개 광고 포맷 샘플")
print("=" * 55)
