#!/usr/bin/env python3
"""
한궁 라디오 MP3 파일 카탈로그 관리 시스템
==========================================
수천 개 MP3 파일의 체계적 관리와 검색을 위한 카탈로그

사용법:
  python catalog.py --list              # 전체 파일 목록
  python catalog.py --report            # 생성 현황 리포트
  python catalog.py --program P01       # 특정 프로그램 파일 목록
  python catalog.py --export csv        # CSV 내보내기 (스프레드시트용)
"""

import os
import json
import csv
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "content"))
from broadcast_scripts import PROGRAMS, get_all_segments


OUTPUT_DIR = Path(__file__).parent.parent / "output"

# ═══════════════════════════════════════════════════════════════
# 파일 명명 체계 (Naming Convention)
# ═══════════════════════════════════════════════════════════════
"""
파일명 구조:
  HANGUNG_{프로그램}_{에피소드}_{구간}_{날짜}_{버전}.mp3

구성 요소:
  HANGUNG      : 서비스 식별자 (고정)
  P01~P10      : 프로그램 코드
  EP001~EP999  : 에피소드 번호
  S1~S5 / FULL : 구간 코드 (FULL = 합본)
  YYYYMMDD     : 생성 날짜
  v1, v2 ...   : 버전 (재제작 시 v2로 업데이트)

예시:
  HANGUNG_P01_EP001_S1_20260606_v1.mp3   (칭찬라디오 1화 오프닝)
  HANGUNG_P01_EP001_FULL_20260606_v1.mp3 (칭찬라디오 1화 합본)
  HANGUNG_P09_EP001_S2_20260606_v1.mp3   (총재메시지 1화 사연소개)

프로그램 코드 매핑:
  P01: 한궁 칭찬 라디오          (회원용)
  P02: 기억활력 라디오            (회원용)
  P03: 부모님 안부 라디오         (회원+가족)
  P04: 오늘의 한궁 루틴 라디오    (회원용, 자동화)
  P05: 7일 체험 라디오            (신규 회원)
  P06: 지도사 교육 라디오         (지도사)
  P07: 지도사 CRM 라디오          (지도사)
  P08: 지도사 수익화 라디오       (지도사)
  P09: 총재 메시지 라디오         (전 조직)
  P10: 경영자 리포트 라디오       (경영진)

구간 코드:
  S1: 오프닝
  S2: 사연소개
  S3: 노래소개
  S4: 노래재생 (사연기반 AI노래 or BGM)
  S5: 클로징
  FULL: 5구간 합본
"""


def get_expected_catalog():
    """예상 파일 카탈로그 (전체 생성 계획)"""
    catalog = []
    segments = get_all_segments()
    
    for seg in segments:
        catalog.append({
            "filename": seg["filename"],
            "program_id": seg["program_id"],
            "program_name": seg["program_name"],
            "episode_id": seg["episode_id"],
            "episode_title": seg["episode_title"],
            "segment": seg["segment_key"],
            "segment_display": {
                "S1": "오프닝",
                "S2": "사연소개",
                "S3": "노래소개",
                "S4": "노래재생",
                "S5": "클로징",
            }.get(seg["segment_num"], seg["segment_num"]),
            "target": PROGRAMS[seg["program_id"]]["target"],
            "purpose": PROGRAMS[seg["program_id"]]["purpose"],
            "type": "segment",
            "dir": f"output/{seg['program_id']}_{'_'.join(PROGRAMS[seg['program_id']]['name'].split()[:2])}",
        })
        
        # 합본 파일 추가 (에피소드당 하나)
        full_filename = seg["filename"].replace(seg["segment_num"], "FULL")
        # 중복 방지
        if not any(c["filename"] == full_filename for c in catalog):
            catalog.append({
                "filename": full_filename,
                "program_id": seg["program_id"],
                "program_name": seg["program_name"],
                "episode_id": seg["episode_id"],
                "episode_title": seg["episode_title"],
                "segment": "FULL",
                "segment_display": "합본 (5구간 전체)",
                "target": PROGRAMS[seg["program_id"]]["target"],
                "purpose": PROGRAMS[seg["program_id"]]["purpose"],
                "type": "full_episode",
                "dir": f"output/{seg['program_id']}",
            })
    
    return catalog


def get_existing_files():
    """실제 생성된 파일 목록"""
    existing = {}
    for prog_dir in OUTPUT_DIR.iterdir():
        if prog_dir.is_dir():
            for f in prog_dir.glob("*.mp3"):
                meta_file = f.with_suffix(".json")
                meta = {}
                if meta_file.exists():
                    with open(meta_file, encoding="utf-8") as mf:
                        meta = json.load(mf)
                
                size_kb = f.stat().st_size // 1024
                duration_est = size_kb // 16  # 대략적인 초 추정 (128kbps 기준)
                
                existing[f.name] = {
                    "path": str(f),
                    "size_kb": size_kb,
                    "duration_est_sec": duration_est,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                    "metadata": meta,
                }
    return existing


def print_catalog_report():
    """카탈로그 현황 리포트 출력"""
    catalog = get_expected_catalog()
    existing = get_existing_files()
    
    total_planned = len(catalog)
    total_existing = len(existing)
    
    print("=" * 70)
    print("한궁 F&B 라디오 MP3 파일 카탈로그 리포트")
    print(f"생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print(f"계획 파일 수: {total_planned:,}개")
    print(f"생성 완료:   {total_existing:,}개")
    print(f"미생성:      {total_planned - total_existing:,}개")
    print(f"완료율:      {total_existing/total_planned*100:.1f}%")
    print()
    
    # 프로그램별 현황
    print("프로그램별 현황:")
    print("-" * 70)
    print(f"{'코드':<6} {'프로그램명':<22} {'대상':<12} {'계획':<6} {'완료':<6} {'상태'}")
    print("-" * 70)
    
    for prog_id, prog in PROGRAMS.items():
        planned = len([c for c in catalog if c["program_id"] == prog_id])
        done = len([e for e in existing if e.startswith(f"HANGUNG_{prog_id}_")])
        status = "✓ 완료" if done >= planned else f"진행중 ({done}/{planned})" if done > 0 else "미시작"
        print(f"{prog_id:<6} {prog['name']:<22} {prog['target']:<12} {planned:<6} {done:<6} {status}")
    
    print("=" * 70)


def export_csv(output_path: str = None):
    """카탈로그를 CSV로 내보내기"""
    catalog = get_expected_catalog()
    existing = get_existing_files()
    
    output_path = output_path or str(Path(__file__).parent.parent / "hangung_radio_catalog.csv")
    
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "파일명", "프로그램코드", "프로그램명", "에피소드", "에피소드제목",
            "구간", "구간설명", "대상", "목적", "생성여부", "파일크기KB", "예상길이초"
        ])
        writer.writeheader()
        
        for item in catalog:
            ex = existing.get(item["filename"], {})
            writer.writerow({
                "파일명": item["filename"],
                "프로그램코드": item["program_id"],
                "프로그램명": item["program_name"],
                "에피소드": item["episode_id"],
                "에피소드제목": item["episode_title"],
                "구간": item["segment"],
                "구간설명": item["segment_display"],
                "대상": item["target"],
                "목적": item["purpose"],
                "생성여부": "완료" if item["filename"] in existing else "미생성",
                "파일크기KB": ex.get("size_kb", ""),
                "예상길이초": ex.get("duration_est_sec", ""),
            })
    
    print(f"CSV 내보내기 완료: {output_path}")
    return output_path


def scale_projection():
    """운영 규모 확장 시뮬레이션"""
    print("\n운영 규모별 MP3 파일 수 전망")
    print("=" * 70)
    
    segments_per_episode = 6  # 5구간 + 합본
    
    scenarios = [
        ("투자유치 데모", 10, 2, "10개 프로그램 × 2에피소드"),
        ("베타 운영", 10, 20, "10개 프로그램 × 20에피소드"),
        ("1차 정식 운영", 10, 52, "10개 프로그램 × 주간 1편 × 1년"),
        ("지도사 50명 운영", 10, 52, "지도사별 회원 사연 포함", 50),
        ("전국 운영 1,000명 지도사", 10, 52, "사연 기반 개인화 포함", 1000),
    ]
    
    print(f"{'시나리오':<28} {'기본MP3':<12} {'개인화MP3':<12} {'총MP3'}")
    print("-" * 70)
    
    for scenario in scenarios:
        name = scenario[0]
        progs = scenario[1]
        episodes = scenario[2]
        desc = scenario[3]
        instructors = scenario[4] if len(scenario) > 4 else 1
        
        base_files = progs * episodes * segments_per_episode
        personal_files = instructors * 10 * segments_per_episode  # 지도사별 평균 월 10건 사연
        total = base_files + personal_files
        
        print(f"{name:<28} {base_files:<12,} {personal_files:<12,} {total:,}")
    
    print()
    print("주: 사연 기반 개인화 MP3 = 지도사 × 월 사연 10건 × 구간 6개")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="한궁 라디오 카탈로그 관리")
    parser.add_argument("--report", action="store_true", help="현황 리포트")
    parser.add_argument("--list", action="store_true", help="전체 파일 목록")
    parser.add_argument("--export", choices=["csv"], help="내보내기")
    parser.add_argument("--program", help="특정 프로그램 조회")
    parser.add_argument("--scale", action="store_true", help="규모 확장 시뮬레이션")
    
    args = parser.parse_args()
    
    if args.report or not any(vars(args).values()):
        print_catalog_report()
    
    if args.export == "csv":
        export_csv()
    
    if args.scale:
        scale_projection()
    
    if args.list:
        catalog = get_expected_catalog()
        for item in catalog:
            print(item["filename"])
