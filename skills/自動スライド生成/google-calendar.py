#!/usr/bin/env python3
"""
Google Calendar API 連携スクリプト（マージ機能付き）

カレンダーイベントと議事録フォルダから文字起こしデータを生成します
"""

import os
import sys
import pickle
import json
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

# 設定
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_DIR = Path.home() / '.claude' / 'credentials'
TOKEN_FILE = CREDENTIALS_DIR / 'token.pickle'
CREDENTIALS_FILE = CREDENTIALS_DIR / 'credentials.json'
OUTPUT_DIR = Path.home() / '.claude' / 'transcriptions'
MEETINGS_DIR = Path.home() / '.claude' / 'meetings'


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
                print("google-calendar-setup.md を参照して認証情報を作成してください")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        # トークンを保存
        CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return creds


def get_calendar_events(service, date_str=None):
    """指定日付のカレンダーイベントを取得

    Args:
        service: Calendar APIサービス
        date_str: 日付文字列（YYYY-MM-DD形式）。Noneの場合は今日

    Returns:
        イベントリスト
    """
    if date_str:
        # 指定日付の00:00〜23:59を取得
        start_time = datetime.fromisoformat(f"{date_str}T00:00:00+09:00")
        end_time = datetime.fromisoformat(f"{date_str}T23:59:59+09:00")
    else:
        # 今日のイベントを取得
        now = datetime.now(timezone.utc)
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)

    # RFC3339形式に変換
    start_time_str = start_time.isoformat()
    end_time_str = end_time.isoformat()

    print(f"取得範囲: {start_time_str} 〜 {end_time_str}")

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time_str,
        timeMax=end_time_str,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return events


def get_meeting_files(date_str):
    """議事録フォルダから文字起こしファイルを取得

    Args:
        date_str: 日付文字列

    Returns:
        ファイルリストと結合されたテキスト
    """
    meeting_dir = MEETINGS_DIR / date_str

    if not meeting_dir.exists():
        return [], ""

    txt_files = list(meeting_dir.glob("*.txt"))

    if not txt_files:
        return [], ""

    # 全ファイルの内容を結合
    combined_text = []
    for txt_file in sorted(txt_files):
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            combined_text.append(f"## {txt_file.name}\n\n{content}")

    return txt_files, "\n\n".join(combined_text)


def events_to_transcription(events, meeting_text, date_str):
    """イベント情報と議事録を文字起こし形式に変換

    Args:
        events: イベントリスト
        meeting_text: 議事録テキスト
        date_str: 日付文字列

    Returns:
        文字起こしテキスト
    """
    lines = [
        "# 文字起こし",
        f"日付: {date_str}",
        "",
        "## データソース",
        "- Google Calendar",
        "- 議事録フォルダ",
        "",
    ]

    # Google Calendarイベント
    if events:
        lines.extend([
            "## Google Calendar イベント",
            ""
        ])

        for event in events:
            # タイトル
            summary = event.get('summary', '（タイトルなし）')

            # 時間
            start = event.get('start', {})
            end = event.get('end', {})

            if 'dateTime' in start:
                start_time = start.get('dateTime', '').replace('+09:00', '')
                end_time = end.get('dateTime', '').replace('+09:00', '')
                time_str = f"{start_time} 〜 {end_time}"
            else:
                date = start.get('date', '')
                time_str = f"終日: {date}"

            # 説明
            description = event.get('description', '')
            if description:
                description = f"\n{description}\n"

            # 場所
            location = event.get('location', '')
            if location:
                location = f"場所: {location}"

            lines.append(f"### {summary}")
            lines.append(f"時間: {time_str}")

            if location:
                lines.append(location)

            if description:
                lines.append(description)

            lines.append("")
    else:
        lines.extend([
            "## Google Calendar イベント",
            "",
            "この日のイベントはありませんでした。",
            ""
        ])

    # 議事録フォルダの内容
    if meeting_text:
        lines.extend([
            "## 議事録フォルダ",
            "",
            meeting_text,
            ""
        ])
    else:
        lines.extend([
            "## 議事録フォルダ",
            "",
            "議事録ファイルはありませんでした。",
            ""
        ])

    return "\n".join(lines)


def save_transcription(text, date_str):
    """文字起こしをファイルに保存

    Args:
        text: 文字起こしテキスト
        date_str: 日付文字列
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / f"{date_str}.txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"保存: {output_file}")


def main():
    """メイン処理"""
    import argparse

    parser = argparse.ArgumentParser(description='Google Calendarと議事録フォルダから文字起こしを生成')
    parser.add_argument('--date', type=str, help='日付（YYYY-MM-DD形式）。デフォルトは今日')
    args = parser.parse_args()

    # 日付決定
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')

    print(f"=== 自動スライド生成：データ取得 ===")
    print(f"対象日: {date_str}")
    print()

    # 認証
    print("認証チェック中...")
    try:
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)
        print("認証完了")
    except Exception as e:
        print(f"認証エラー: {e}")
        print("Google Calendarはスキップします")
        service = None
    print()

    # Google Calendarからイベント取得
    events = []
    if service:
        print("Google Calendar イベント取得中...")
        try:
            events = get_calendar_events(service, date_str)
            print(f"{len(events)}件のイベントが見つかりました")
        except Exception as e:
            print(f"イベント取得エラー: {e}")
        print()

    # 議事録フォルダからファイル取得
    print("議事録フォルダ確認中...")
    meeting_files, meeting_text = get_meeting_files(date_str)
    print(f"{len(meeting_files)}件の議事録ファイルが見つかりました")
    print()

    # 文字起こし形式に変換
    print("マージ処理中...")
    transcription = events_to_transcription(events, meeting_text, date_str)

    # 保存
    save_transcription(transcription, date_str)

    print()
    print("完了!")


if __name__ == '__main__':
    main()
