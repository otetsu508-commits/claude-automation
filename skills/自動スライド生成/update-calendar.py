#!/usr/bin/env python3
"""
コンテンツカレンダー自動更新スクリプト

月の最後の記事が書き終わったら、来月の記事テーマを追加してカレンダーを更新します
"""

import re
from datetime import datetime, timedelta
from pathlib import Path

# 設定
CALENDAR_FILE = Path.home() / '.claude' / 'inputs' / 'content-calendar-company.md'


def get_last_article_date(content):
    """カレンダーから最後の記事の日付を取得"""
    # | 2026-07-25 | の形式を探す
    pattern = r'\|\s*(\d{4}-\d{2}-\d{2})\s*\|'
    matches = re.findall(pattern, content)

    if not matches:
        return None

    # 最後の日付を返す
    return matches[-1]


def is_last_article_of_month(date_str):
    """その日が月の最後の記事かどうかを判定"""
    date_obj = datetime.fromisoformat(date_str)

    # その月の最終日を取得
    if date_obj.month == 12:
        last_day = date_obj.replace(day=31)
    else:
        next_month = date_obj.replace(month=date_obj.month + 1, day=1)
        last_day = next_month - timedelta(days=1)

    # 最終日から7日以内なら「月の最後の記事」とみなす
    return (last_day - date_obj).days <= 7


def generate_next_month_themes(current_last_date):
    """来月の記事テーマを生成"""
    current_date = datetime.fromisoformat(current_last_date)

    # 来月の1日と4日（火・金）
    next_month = current_date.replace(day=1) + timedelta(days=32)
    next_month = next_month.replace(day=1)

    # 来月の第1火曜日と金曜日を探す
    first_day = next_month
    if first_day.weekday() >= 4:  # 金曜日以降なら次週
        first_day = first_day + timedelta(days=7 - first_day.weekday())
    else:
        first_day = first_day - timedelta(days=first_day.weekday())  # 月曜日に合わせる

    first_tuesday = first_day + timedelta(days=1)  # 火曜日
    first_friday = first_day + timedelta(days=4)   # 金曜日

    second_tuesday = first_tuesday + timedelta(days=7)
    second_friday = first_friday + timedelta(days=7)

    themes = [
        {
            'date': first_tuesday.strftime('%Y-%m-%d'),
            'dow': '火',
            'theme': '【AI活用】来月のテーマ：中小企業DX成功のポイント',
            'purpose': '来月の導入として'
        },
        {
            'date': first_friday.strftime('%Y-%m-%d'),
            'dow': '金',
            'theme': '【実践編】AIツール比較：〇〇におすすめのツール',
            'purpose': '具体例の提示'
        },
        {
            'date': second_tuesday.strftime('%Y-%m-%d'),
            'dow': '火',
            'theme': '【ケーススタディ】業界別AI導入事例',
            'purpose': '事例紹介'
        },
        {
            'date': second_friday.strftime('%Y-%m-%d'),
            'dow': '金',
            'theme': '【Q&A】AI導入でよくある質問と回答',
            'purpose': '疑問解消'
        }
    ]

    return themes


def update_calendar(content, new_themes):
    """カレンダーを更新"""
    # 「## 記事テーマ計画」のセクションを探す
    pattern = r'(## 記事テーマ計画.*?)(##.*)'
    replacement = r'\1'

    # 新しいテーマを追加
    for theme in new_themes:
        replacement += f"| {theme['date']}（{theme['dow']}） | {theme['theme']} | {theme['purpose']} |\n"

    replacement += r'\2'

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    return new_content


def add_calendar_events_to_google(new_themes):
    """Google Calendarにもイベントを追加"""
    try:
        # add-calendar-events.py をインポートして実行
        import sys
        sys.path.insert(0, str(Path.home() / '.claude' / 'skills' / '自動スライド生成'))
        from add_calendar_events import create_calendar_event, get_credentials

        from googleapiclient.discovery import build
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import pickle

        # 認証
        CREDENTIALS_DIR = Path.home() / '.claude' / 'credentials'
        TOKEN_FILE = CREDENTIALS_DIR / 'token.pickle'
        CREDENTIALS_FILE = CREDENTIALS_DIR / 'credentials.json'

        SCOPES = ['https://www.googleapis.com/auth/calendar.events']

        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)

        # イベントを登録
        for theme in new_themes:
            date_obj = datetime.fromisoformat(theme['date'])
            start_time = date_obj.replace(hour=7, minute=0)
            end_time = date_obj.replace(hour=8, minute=0)

            event_data = {
                'date': theme['date'],
                'theme': theme['theme'],
                'start': start_time,
                'end': end_time
            }

            create_calendar_event(service, event_data)

    except Exception as e:
        print(f"Google Calendarへの登録でエラーが発生しました: {e}")


def main():
    """メイン処理"""
    print("=== コンテンツカレンダー自動更新 ===")
    print()

    if not CALENDAR_FILE.exists():
        print(f"エラー: {CALENDAR_FILE} が見つかりません")
        return

    # カレンダーを読み込む
    with open(CALENDAR_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 最後の記事の日付を取得
    last_date = get_last_article_date(content)

    if not last_date:
        print("記事が見つかりませんでした")
        return

    print(f"最後の記事: {last_date}")

    # 月の最後の記事かどうか判定
    if is_last_article_of_month(last_date):
        print("月の最後の記事です。来月のテーマを追加します...")
        print()

        # 来月のテーマを生成
        new_themes = generate_next_month_themes(last_date)

        print("来月のテーマ:")
        for theme in new_themes:
            print(f"  {theme['date']}（{theme['dow']}）: {theme['theme']}")
        print()

        # カレンダーを更新
        new_content = update_calendar(content, new_themes)

        with open(CALENDAR_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"{CALENDAR_FILE} を更新しました")
        print()

        # Google Calendarにも追加
        print("Google Calendarにもイベントを追加します...")
        add_calendar_events_to_google(new_themes)

        print()
        print("完了!")
    else:
        print("まだ月の途中です。更新は不要です。")


if __name__ == '__main__':
    main()
