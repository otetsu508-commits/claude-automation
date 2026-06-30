# 自動スライド生成ワークフロー

## 概要

毎日朝9:00に実行され、議事録フォルダとGoogle Calendarのイベントから提案資料を自動生成します。

## ワークフロー（更新版）

```
1. データソースから情報取得
   ├─> Google Calendarからイベント取得（google-calendar.py）
   │   └─> transcriptions/YYYY-MM-DD.txt
   └─> 議事録フォルダから文字起こしファイル取得
       └─> meetings/YYYY-MM-DD/*.txt

2. 内容マージ
   ├─> 重複している場合 → Google Calendarの内容を優先
   └─> 内容が異なる場合 → 両方の内容を統合

3. 顧客情報抽出
   └─> 会社名、業界、規模、課題

4. 構成案作成
   └─> meetings/YYYY-MM-DD/proposals/outline.md

5. ピッチ資料作成
   └─> meetings/YYYY-MM-DD/proposals/pitch.md

6. PDF出力
   └─> meetings/YYYY-MM-DD/proposals/pitch.pdf

7. 案件フォルダに保存
   └─> drafts/YYYY-MM-DD_顧客名/
```

## ディレクトリ構造

```
.claude/
├── credentials/
│   ├── credentials.json      ← Google認証情報（手動配置）
│   └── token.pickle          ← トークン（自動生成）
├── transcriptions/
│   └── YYYY-MM-DD.txt       ← Google Calendarから自動生成
├── meetings/                 ← 議事録フォルダ（既存）
│   └── YYYY-MM-DD/
│       ├── meeting-1.txt    ← 手動配置
│       └── meeting-2.txt
├── company/06_marketing/
│   ├── meetings/
│   │   └── YYYY-MM-DD/
│   │       └── proposals/
│   └── drafts/
│       └── YYYY-MM-DD_顧客名/
└── skills/
    └── 自動スライド生成/
        ├── google-calendar.py
        ├── google-calendar-setup.md
        └── run-calendar.bat
```

## データソースの優先順位

| ソース | 優先度 | 説明 |
|--------|--------|------|
| Google Calendar | 高 | 最新の予定情報 |
| 議事録フォルダ | 低 | 過去の会議記録 |

- 同じイベントの場合：Google Calendarの内容を優先
- 異なる内容の場合：両方を統合

## 実行方法

### 自動実行（毎日9:00）
ルーティンで自動実行されます。

### 手動実行
```bash
# Google Calendarから今日のイベントを取得
run-calendar.bat

# 日付指定
run-calendar.bat --date 2026-07-01
```

### Python直接実行
```bash
python google-calendar.py
python google-calendar.py --date 2026-07-01
```

## 設定手順

1. **Google Cloud Platformでプロジェクト作成**
   → `google-calendar-setup.md` を参照

2. **認証情報の配置**
   - `credentials.json` を `.claude/credentials/` に配置

3. **初回認証実行**
   - `run-calendar.bat` を実行
   - ブラウザでGoogle認証
   - `token.pickle` が自動生成

## 処理内容

### 1. 文字起こしファイルの取得
- Google Calendar APIからイベント取得
- `meetings/YYYY-MM-DD/` フォルダからテキストファイル取得

### 2. 顧客情報の抽出
- 会社名
- 業界
- 規模
- 課題
- 担当者

### 3. マージ処理
- 重複イベントの除外
- 時系列順の整理
- Google Calendar優先（最新情報）

## 注意点

- 初回実行時はブラウザ認証が必要
- トークンの有効期限（約1週間）が切れると再認証が必要
- 複数カレンダーがある場合はスクリプトの`calendarId`を変更
- 議事録フォルダとGoogle Calendarの両方を使うことで、過去の会議記録と今後の予定を統合

---

**最終更新**: 2026-06-30
