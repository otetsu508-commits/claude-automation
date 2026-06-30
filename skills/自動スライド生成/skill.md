# 毎日議事録→提案資料 自動生成スキル

## 概要

毎日朝9:00に自動実行され、前日のアポイント文字起こしから提案資料を自動生成します。

## 完全自動化される工程

| ステップ | 内容 | 自動/手動 |
|---------|------|----------|
| 1. 議事録フォルダ作成 | `meetings/YYYY-MM-DD/` | ✅ 自動 |
| 2. 文字起こし取得 | `transcriptions/YYYY-MM-DD/` から | ✅ 自動 |
| 3. 顧客情報抽出 | 会社名、業界、規模、課題 | ✅ 自動 |
| 4. 構成案作成 | テンプレートベース | ✅ 自動 |
| 5. ピッチ資料作成 | Marp形式 | ✅ 自動 |
| 6. PDF出力 | Marpで変換 | ✅ 自動 |
| 7. 案件フォルダ保存 | `drafts/YYYY-MM-DD_顧客名/` | ✅ 自動 |

## ワークフロー

```
毎日9:00
  └─> meetings/YYYY-MM-DD/ フォルダ作成
      └─> transcriptions/YYYY-MM-DD/ から文字起こし取得
          └─> 顧客情報抽出（会社名、業界、課題など）
              └─> 構成案作成 (outline.md)
                  └─> ピッチ資料作成 (pitch.md)
                      └─> PDF出力 (pitch.pdf)
                          └─> 案件フォルダに保存 (drafts/YYYY-MM-DD_顧客名/)
```

## 入力

- 文字起こしファイル（`.txt`）- `transcriptions/YYYY-MM-DD/` に配置

## 出力

- `meetings/YYYY-MM-DD/proposals/outline.md` - 構成案
- `meetings/YYYY-MM-DD/proposals/pitch.md` - ピッチ資料
- `meetings/YYYY-MM-DD/proposals/pitch.pdf` - PDF
- `drafts/YYYY-MM-DD_顧客名/` - 案件フォルダ（コピー）

## 定期実行設定

- **スケジュール**: 毎日9:00
- **ジョブID**: c99d2819
- **永続化**: `.claude/scheduled_tasks.json` に保存（7日有効）

## 使い方

### 自動実行（毎日9:00）

何もしなくてOK。自動で実行されます。

### 手動実行

```
/skill daily-meeting-proposal
```

### 文字起こしファイルの配置場所

```
.claude/transcriptions/YYYY-MM-DD/
├── meeting-1.txt
└── meeting-2.txt
```

## 顧客情報抽出ロジック

文字起こしから以下を抽出：

| 項目 | 抽出方法 |
|------|----------|
| 会社名 | 「株式会社」「有限会社」などの後ろ |
| 業界 | 「製造業」「サービス業」「IT」などのキーワード |
| 規模 | 「従業員〇〇名」「年商〇〇円」 |
| 課題 | 「困っている」「問題」「課題」の前後 |
| 担当者 | 名前や役職の言及 |

## 注意点

- 文字起こしファイルは `transcriptions/YYYY-MM-DD/` に配置してください
- PDF出力には `marp` コマンドが必要です
- ファイル名は `YYYY-MM-DD` 形式です
