# daily-meeting-proposal スキル

## 実行手順

### ステップ1：今日の日付を取得

```bash
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
```

### ステップ2：議事録フォルダ作成

```bash
mkdir -p "company/06_marketing/sales-doc-creation/meetings/$TODAY/proposals"
```

### ステップ3：文字起こしファイルを取得

```bash
# 昨日の文字起こしファイルを取得
TRANSCRIPT_DIR=".claude/transcriptions/$YESTERDAY"
if [ -d "$TRANSCRIPT_DIR" ]; then
    cp "$TRANSCRIPT_DIR"/*.txt "company/06_marketing/sales-doc-creation/meetings/$TODAY/proposals/"
fi
```

### ステップ4：顧客情報抽出

文字起こしファイルを読み込み、以下を抽出：
- 会社名
- 業界
- 規模
- 課題
- 担当者

### ステップ5：構成案作成

テンプレート `templates/outline-template.md` をベースに作成

### ステップ6：ピッチ資料作成

テンプレート `templates/standard-pitch.md` をベースに作成

### ステップ7：PDF出力

```bash
marp "company/06_marketing/sales-doc-creation/meetings/$TODAY/proposals/pitch.md" --pdf
```

### ステップ8：案件フォルダに保存

```bash
mkdir -p "company/06_marketing/sales-doc-creation/drafts/${TODAY}_${COMPANY_NAME}"
cp -r "company/06_marketing/sales-doc-creation/meetings/$TODAY/proposals/"* \
      "company/06_marketing/sales-doc-creation/drafts/${TODAY}_${COMPANY_NAME}/"
```

## 入力

- 文字起こしファイル（`.txt`）

## 出力

- `meetings/YYYY-MM-DD/proposals/outline.md`
- `meetings/YYYY-MM-DD/proposals/pitch.md`
- `meetings/YYYY-MM-DD/proposals/pitch.pdf`
- `drafts/YYYY-MM-DD_顧客名/` （コピー）
