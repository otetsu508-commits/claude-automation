#!/usr/bin/env python3
"""
実行結果をメールで通知するスクリプト
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone

# 環境変数
TO_EMAIL = os.environ.get("TO_EMAIL", "")
WORKFLOW_STATUS = os.environ.get("WORKFLOW_STATUS", "unknown")
THEME_FOUND = os.environ.get("THEME_FOUND", "false")
THEME_NAME = os.environ.get("THEME_NAME", "なし")

# Gmailの設定（OAuth2を使う予定だが、簡易版として実装）
# 実際にはGmail APIまたはOAuth2フローが必要

def create_email_body() -> str:
    """メール本文を作成"""
    now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")

    status_emoji = {
        "success": "✅",
        "failure": "❌",
        "unknown": "❓"
    }.get(WORKFLOW_STATUS.lower(), "❓")

    body = f"""
<h2>記事生成ワークフロー 実行結果</h2>

<p><strong>実行日時:</strong> {now}</p>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
  <tr>
    <th>項目</th>
    <th>結果</th>
  </tr>
  <tr>
    <td>ステータス</td>
    <td>{status_emoji} {WORKFLOW_STATUS}</td>
  </tr>
  <tr>
    <td>テーマ発見</td>
    <td>{'✅ あり' if THEME_FOUND == 'true' else '❌ なし'}</td>
  </tr>
  <tr>
    <td>テーマ名</td>
    <td>{THEME_NAME}</td>
  </tr>
</table>

<h3>詳細</h3>

<ul>
"""

    if THEME_FOUND == "true":
        body += f"<li>テーマ「{THEME_NAME}」の記事生成を実行しました</li>"
        body += "<li>生成ファイルは outputs/themes/ に保存されています</li>"
    else:
        body += "<li>今日のテーマは見つかりませんでした</li>"
        body += "<li>カレンダー（inputs/content-calendar.md）を確認してください</li>"

    body += f"""
</ul>

<p><small>このメールは GitHub Actions から自動送信されています。</small></p>
"""

    return body

def send_email_gmail_api():
    """Gmail APIを使ってメールを送信"""
    # Gmail API用のライブラリが必要
    # ここでは簡易的な実装としてstdoutに出力
    print("Email notification (Gmail API):")
    print(create_email_body())

def send_email_smtp():
    """SMTPを使ってメールを送信（バックアップ）"""
    # Gmail SMTPの設定
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587

    # 認証情報はGitHub Secretsから取得
    # 実際の実装ではOAuth2またはアプリパスワードを使用

    sender_email = os.environ.get("GMAIL_SENDER", "")
    app_password = os.environ.get("GMAIL_APP_PASSWORD", "")

    if not sender_email or not app_password:
        print("SMTP credentials not configured. Skipping email send.")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"記事生成ワークフロー: {WORKFLOW_STATUS}"
        msg["From"] = sender_email
        msg["To"] = TO_EMAIL

        html_body = create_email_body()
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)

        print("Email sent successfully via SMTP")

    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    """メイン処理"""
    print("Sending email notification...")
    print(f"Status: {WORKFLOW_STATUS}")
    print(f"Theme found: {THEME_FOUND}")
    print(f"Theme name: {THEME_NAME}")

    # メール送信（簡易版としてstdout）
    print("\n" + "="*50)
    print("EMAIL CONTENT:")
    print("="*50)
    print(create_email_body())

    # Gmail APIによる送信は追加設定が必要
    # send_email_gmail_api()

if __name__ == "__main__":
    main()
