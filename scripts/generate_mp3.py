#!/usr/bin/env python3
"""
한궁 F&B 라디오 MP3 생성 스크립트 (에피소드 1파일 버전)
에피소드당 MP3 1개 생성 (5구간 텍스트를 합쳐서 한 번에 TTS)

사용법:
  python scripts/generate_mp3.py --mode demo
  python scripts/generate_mp3.py --mode single --program P01 --episode EP001
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "content"))
from broadcast_scripts import PROGRAMS, get_all_segments

OUTPUT_DIR = Path(__file__).parent.parent / "output"
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

PROGRAM_DIRS = {
    "P01": OUTPUT_DIR / "P01_praise",
    "P02": OUTPUT_DIR / "P02_memory",
    "P03": OUTPUT_DIR / "P03_parents",
    "P04": OUTPUT_DIR / "P04_routine",
    "P05": OUTPUT_DIR / "P05_7day",
    "P06": OUTPUT_DIR / "P06_instructor_edu",
    "P07": OUTPUT_DIR / "P07_instructor_crm",
    "P08": OUTPUT_DIR / "P08_instructor_rev",
    "P09": OUTPUT_DIR / "P09_president",
    "P10": OUTPUT_DIR / "P10_executive",
}


def get_episode_text(prog_id, ep_id):
    """에피소드의 5구간 텍스트를 하나로 합치기 (S4 노래재생 구간 제외)"""
    all_segs = get_all_segments()
    ep_segs = [
        s for s in all_segs
        if s["program_id"] == prog_id and s["episode_id"] == ep_id
    ]
    ep_segs = sorted(ep_segs, key=lambda x: x["segment_num"])

    parts = []
    for seg in ep_segs:
        # S4(노래재생)는 실제 노래 자리이므로 짧은 안내 멘트로 대체
        if seg["segment_num"] == "S4":
            parts.append("(잠시 후 노래가 흐릅니다.)")
        else:
            parts.append(seg["text"])

    full_text = "\n\n".join(parts)
    ep_title = ep_segs[0]["episode_title"] if ep_segs else ep_id
    return full_text, ep_title


def generate_episode_mp3(prog_id, ep_id, client):
    """에피소드 전체를 MP3 1개로 생성"""
    output_dir = PROGRAM_DIRS[prog_id]
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"HANGUNG_{prog_id}_{ep_id}_20260606_v1.mp3"
    output_path = output_dir / filename

    if output_path.exists():
        print(f"  [스킵] {filename} (이미 존재)")
        return True

    full_text, ep_title = get_episode_text(prog_id, ep_id)

    print(f"  [생성중] {filename}")
    print(f"          '{ep_title}' ({len(full_text)}자)")

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=full_text,
        )
        # 스트리밍 없이 바이트로 직접 저장
        audio_bytes = b"".join(response.iter_bytes())
        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        size_kb = output_path.stat().st_size // 1024
        print(f"  [완료] {filename} ({size_kb}KB)")
        return True

    except Exception as e:
        print(f"  [오류] {filename}: {e}")
        return False


def generate_demo_set(client):
    """전체 데모 세트 생성"""
    print("=" * 60)
    print("한궁 F&B 라디오 - 투자유치 데모 MP3 생성")
    print(f"총 10개 프로그램 × 2에피소드 = 20개 MP3")
    print("=" * 60)

    success = 0
    fail = 0

    for prog_id, prog in PROGRAMS.items():
        print(f"\n[{prog_id}] {prog['name']} (대상: {prog['target']})")
        for ep in prog["episodes"]:
            ok = generate_episode_mp3(prog_id, ep["ep"], client)
            if ok:
                success += 1
            else:
                fail += 1
            time.sleep(1)  # API 과부하 방지

    print("\n" + "=" * 60)
    print(f"완료: {success}개  오류: {fail}개")
    print(f"저장 위치: {OUTPUT_DIR}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="한궁 라디오 MP3 생성기")
    parser.add_argument("--mode", choices=["demo", "single"], default="demo")
    parser.add_argument("--tts", default="openai")
    parser.add_argument("--program", help="예: P01")
    parser.add_argument("--episode", help="예: EP001")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("오류: OPENAI_API_KEY 환경변수가 없습니다.")
        print("터미널에서 먼저 실행하세요:")
        print('  $env:OPENAI_API_KEY="sk-..."')
        sys.exit(1)

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    if args.mode == "demo":
        generate_demo_set(client)
    elif args.mode == "single":
        if not args.program or not args.episode:
            print("단일 모드: --program P01 --episode EP001 필요")
            sys.exit(1)
        generate_episode_mp3(args.program, args.episode, client)


if __name__ == "__main__":
    main()
