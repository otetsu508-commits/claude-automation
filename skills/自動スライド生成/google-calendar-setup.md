# Google Calendar API 連携手順

**目的**: Googleカレンダーのイベント情報を自動取得して文字起こし・提案資料生成に活用

**作成**: 2026-06-30

---

## ステップ1: Google Cloud Platformでプロジェクト作成

### 1-1. GCPコンソールにアクセス

https://console.cloud.google.com/

### 1-2. 新規プロジェクト作成

1. 左上のプロジェクト選択 → 「新しいプロジェクト」
2. プロジェクト名: `int-partners-calendar`（任意）
3. 「作成」をクリック

---

## ステップ2: Calendar APIを有効化

### 2-1. APIを有効化

1. 左メニュー → 「APIとサービス」→「ライブラリ」
2. 検索: `Google Calendar API`
3. 「Google Calendar API」を選択
4. 「有効にする」をクリック

---

## ステップ3: OAuth認証情報の作成

### 3-1. OAuth同意画面の設定

1. 左メニュー → 「APIとサービス」→「OAuth同意画面」
2. ユーザータイプ: 「外部」を選択
3. 「作成」をクリック

### 3-2. アプリ情報を入力

| 項目 | 入力内容 |
|------|----------|
| アプリ名 | インテリジェンス・パートナーズ |
| ユーザーサポートメール | あなたのメール |
| 開発者連絡先メール | あなたのメール |

### 3-3. スコープの追加

1. 「スコープを追加」をクリック
2. 「...」をクリックしてカレンダーAPIのスコープを追加
3. 必要なスコープ:
   - `https://www.googleapis.com/auth/calendar.readonly`
   - `https://www.googleapis.com/auth/calendar.events`

### 3-4. テストユーザーを追加

1. 「ユーザーを追加」
2. 自分のメールアドレスを追加

### 3-5. 「保存して続行」

---

## ステップ4: クライアントIDの作成

### 4-1. クライアントIDを作成

1. 左メニュー → 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「OAuthクライアントID」
3. アプリケーションの種類: 「デスクトップアプリ」
4. 名前: `Calendar Integration`
5. 「作成」をクリック

### 4-2. 認証情報を確認

作成後に表示される情報をメモ:
- **クライアントID**
- **クライアントシークレット**

---

## ステップ5: ローカル環境設定

### 5-1. 必要なライブラリインストール

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 5-2. 認証ファイルの作成

以下の内容で `credentials.json` を作成:

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "int-partners-calendar",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

### 5-3. 最初の認証実行

```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

# トークンを保存
import pickle
with open('token.pickle', 'wb') as token:
    pickle.dump(creds, token)
```

実行するとブラウザが開き、Google認証が求められます。

---

## ステップ6: カレンダーイベント取得テスト

### 6-1. テストスクリプト

```python
from googleapiclient.discovery import build
import pickle
from datetime import datetime, timedelta

# トークン読み込み
with open('token.pickle', 'rb') as token:
    creds = pickle.load(token)

# サービス作成
service = build('calendar', 'v3', credentials=creds)

# 今日のイベント取得
now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'

events_result = service.events().list(
    calendarId='primary',
    timeMin=now,
    timeMax=tomorrow,
    singleEvents=True,
    orderBy='startTime'
).execute()

events = events_result.get('items', [])

for event in events:
    print(f"{event['summary']}: {event.get('start', {}).get('dateTime', 'N/A')}")
```

---

## ステップ7: 自動スライド生成スキルとの統合

### 7-1. スキル更新

スキルの `workflow.md` を更新して、Google Calendarから取得したイベント情報を文字起こしとして扱います。

### 7-2. ディレクトリ構造

```
.claude/
├── skills/
│   └── 自動スライド生成/
│       ├── google-calendar.py    ← 新規作成
│       ├── workflow.md            ← 更新
│       └── run.sh                 ← 更新
└── credentials/                   ← 新規作成
    ├── credentials.json
    └── token.pickle
```

---

## 注意点

1. **セキュリティ**: `credentials.json` と `token.pickle` は`.gitignore`に追加
2. **トークン有効期限**: トークンの有効期限が切れた場合は再認証必要
3. **カレンダー権限**: 複数カレンダーがある場合は`calendarId`を変更

---

**作成**: 2026-06-30
**作成者**: ライト（CEO）
