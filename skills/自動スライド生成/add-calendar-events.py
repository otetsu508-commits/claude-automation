#!/usr/bin/env python3
"""
Google Calendar イベント登録スクリプト

コンテンツカレンダーの記事公開日をGoogle Calendarに登録します
"""

import os
import sys
import pickle
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Google APIライブラリ
try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
except ImportError:
    print("Google APIライブラリがインストールされていません")
    print("pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# 設定（書き込み権限付き）
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_DIR = Path.home() / '.claude' / 'credentials'
TOKEN_FILE = CREDENTIALS_DIR / 'token.pickle'
CREDENTIALS_FILE = CREDENTIALS_DIR / 'credentials.json'
CALENDAR_FILE = Path.home() / '.claude' / 'inputs' / 'content-calendar-company.md'


def get_credentials():
    """認証情報を取得または作成"""
    creds = None

    # トークンが存在する場合、読み込む
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # トークンがない、または有効期限切れの場合、再認証
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print(f"エラー: {CREDENTIALS_FILE} が見つかりません")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        # トークンを保存
        CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return creds


def parse_calendar_file():
    """コンテンツカレンダーファイルをパース"""
    if not CALENDAR_FILE.exists():
        print(f"エラー: {CALENDAR_FILE} が見つかりません")
        return []

    with open(CALENDAR_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    events = []
    lines = content.split('\n')

    for i, line in enumerate(lines):
        # 記事テーマの行を探す（| 2026-07-01 | テーマ | の形式）
        if '| 2026-' in line and '（火）' in line or '（金）' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                date_str = parts[1].strip().split('（')[0].strip()
                theme = parts[2].strip()

                # 時間を設定（7:00-8:00）
                date_obj = datetime.fromisoformat(date_str)
                start_time = date_obj.replace(hour=7, minute=0)
                end_time = date_obj.replace(hour=8, minute=0)

                events.append({
                    'date': date_str,
                    'theme': theme,
                    'start': start_time,
                    'end': end_time
                })

    return events


def create_calendar_event(service, event_data):
    """Google Calendarにイベントを作成"""
    event = {
        'summary': f'【note記事】{event_data["theme"]}',
        'description': f'note記事公開日: {event_data["theme"]}\n\nインテリジェンス・パートナーズ',
        'start': {
            'dateTime': event_data['start'].isoformat(),
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': event_data['end'].isoformat(),
            'timeZone': 'Asia/Tokyo',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 60},
            ],
        },
    }

    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"  [OK] 登録成功: {event_data['date']} - {event_data['theme']}")
        return True
    except Exception as e:
        print(f"  [NG] 登録失敗: {event_data['date']} - {event_data['theme']}")
        print(f"     エラー: {e}")
        return False


def main():
    """メイン処理"""
    print("=== Google Calendar イベント登録 ===")
    print()

    # 認証（書き込み権限が必要）
    print("認証チェック中...")
    try:
        # 既存のトークンを削除（スコープ変更のため）
        if TOKEN_FILE.exists():
            print("スコープ変更のため、既存トークンを削除します")
            TOKEN_FILE.unlink()

        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)
        print("認証完了")
    except Exception as e:
        print(f"認証エラー: {e}")
        sys.exit(1)

    print()

    # カレンダーファイルをパース
    print("コンテンツカレンダーを読み込み中...")
    events = parse_calendar_file()

    if not events:
        print("イベントが見つかりませんでした")
        return

    print(f"{len(events)}件のイベントが見つかりました")
    print()

    # イベントを登録
    print("Google Calendarにイベントを登録中...")
    print()

    success_count = 0
    for event in events:
        if create_calendar_event(service, event):
            success_count += 1

    print()
    print(f"完了! {success_count}/{len(events)}件のイベントを登録しました")


if __name__ == '__main__':
    main()
