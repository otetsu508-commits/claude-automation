#!/usr/bin/env python3
"""
カレンダーから今日のテーマを取得するスクリプト
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# タイムゾーン考慮（日本時間）
JST = timezone(timedelta(hours=9))

def get_today_theme():
    """今日のテーマをカレンダーから取得"""
    # 今日の日付（日本時間）
    today = datetime.now(JST).strftime("%Y-%m-%d")
    day_of_week = datetime.now(JST).strftime("%A")

    print(f"Checking theme for {today} ({day_of_week})")

    # カレンダーファイルのパス
    calendar_path = Path("inputs/content-calendar.md")

    if not calendar_path.exists():
        print(f"Calendar file not found: {calendar_path}")
        set_output("theme_found", "false")
        set_output("theme_name", "")
        return

    # カレンダーを読み込む
    with open(calendar_path, "r", encoding="utf-8") as f:
        calendar_content = f.read()

    # 今日の日付を探す
    if today in calendar_content:
        lines = calendar_content.split("\n")
        for i, line in enumerate(lines):
            if today in line:
                # 次の行からテーマを取得
                if i + 1 < len(lines):
                    theme_line = lines[i + 1].strip()
                    if theme_line and not theme_line.startswith("#"):
                        theme_name = theme_line.replace("##", "").strip()
                        print(f"Found theme: {theme_name}")

                        # GitHub Actionsの出力を設定
                        set_output("theme_found", "true")
                        set_output("theme_name", theme_name)
                        set_output("date", today)
                        return

    print("No theme found for today")
    set_output("theme_found", "false")
    set_output("theme_name", "")
    set_output("date", today)

def set_output(name, value):
    """GitHub Actionsの出力を設定"""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"{name}={value}\n")
    print(f"Output: {name}={value}")

if __name__ == "__main__":
    from datetime import timezone
    get_today_theme()
