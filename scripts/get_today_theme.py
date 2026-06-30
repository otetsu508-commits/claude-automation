#!/usr/bin/env python3
"""
カレンダーから今日のテーマを取得するスクリプト
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re

def get_today_theme():
    """今日のテーマをカレンダーから取得"""
    # タイムゾーン考慮（日本時間）
    JST = timezone(timedelta(hours=9))
    now = datetime.now(JST)

    # 今日の日付（日本時間、形式: M/DD）
    today_month = now.month
    today_day = now.day
    today_str_short = f"{today_month}/{str(today_day).zfill(2)}"
    today_str_full = f"{now.year}-{str(today_month).zfill(2)}-{str(today_day).zfill(2)}"

    print(f"Checking theme for {today_str_full} ({now.strftime('%A')})")

    # カレンダーファイルのパス
    calendar_path = Path("inputs/content-calendar.md")

    if not calendar_path.exists():
        print(f"Calendar file not found: {calendar_path}")
        set_output("theme_found", "false")
        set_output("theme_name", "")
        set_output("date", today_str_full)
        return

    # カレンダーを読み込む
    with open(calendar_path, "r", encoding="utf-8") as f:
        calendar_content = f.read()

    # テーブルから今日のエントリを探す
    # 形式: | M/DD | 曜日 | テーマ | ... |
    lines = calendar_content.split("\n")

    for i, line in enumerate(lines):
        # テーブル行をチェック（| で区切られている）
        if "|" in line and today_str_short in line:
            parts = [p.strip() for p in line.split("|")]
            # parts[0]は空、parts[1]が日付、parts[2]が曜日、parts[3]がテーマ
            if len(parts) >= 4 and parts[1] == today_str_short:
                theme_name = parts[3]
                # マークダウンの太字を削除
                theme_name = re.sub(r'\*\*([^*]+)\*\*', r'\1', theme_name)
                # 絵文字を残したまま

                print(f"Found theme: {theme_name}")

                # GitHub Actionsの出力を設定
                set_output("theme_found", "true")
                set_output("theme_name", theme_name)
                set_output("date", today_str_full)
                return

    print(f"No theme found for {today_str_short}")
    set_output("theme_found", "false")
    set_output("theme_name", "")
    set_output("date", today_str_full)

def set_output(name, value):
    """GitHub Actionsの出力を設定"""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"{name}={value}\n")
    print(f"Output: {name}={value}")

if __name__ == "__main__":
    get_today_theme()
