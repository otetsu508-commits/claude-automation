#!/bin/bash
# 毎日議事録→提案資料 自動生成スクリプト

# 設定
BASE_DIR="/c/Users/Tetsu/.claude"
SALES_DIR="$BASE_DIR/company/06_marketing/sales-doc-creation"
TRANSCRIPTS_DIR="$BASE_DIR/transcriptions"
TEMPLATES_DIR="$SALES_DIR/templates"

# 日付取得
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)

echo "=== 議事録→提案資料 自動生成 ($TODAY) ==="

# ステップ1：議事録フォルダ作成
echo "1. 議事録フォルダ作成..."
MEETING_DIR="$SALES_DIR/meetings/$TODAY"
PROPOSAL_DIR="$MEETING_DIR/proposals"
mkdir -p "$PROPOSAL_DIR"

# ステップ2：文字起こしファイル取得
echo "2. 文字起こしファイル取得..."
TRANSCRIPT_DIR="$TRANSCRIPTS_DIR/$YESTERDAY"
if [ -d "$TRANSCRIPT_DIR" ]; then
    # 文字起こしファイルを結合
    cat "$TRANSCRIPT_DIR"/*.txt > "$PROPOSAL_DIR/transcript.txt" 2>/dev/null
    TRANSCRIPT="$PROPOSAL_DIR/transcript.txt"
    echo "   文字起こしファイルを取得しました"
else
    echo "   文字起こしファイルが見つかりません: $TRANSCRIPT_DIR"
    exit 0
fi

# ステップ3：顧客情報抽出（簡易版）
echo "3. 顧客情報抽出..."

# ファイル全体を読み込んで変数にセット
CONTENT=$(cat "$TRANSCRIPT")

# 会社名抽出（複数パターン対応）
COMPANY_NAME=$(echo "$CONTENT" | grep "株式会社" | head -1 | sed 's/.*株式会社/株式会社/')
if [ -z "$COMPANY_NAME" ]; then
    COMPANY_NAME=$(echo "$CONTENT" | grep "顧客" | head -1 | sed 's/.*顧客[：:]*//')
fi
[ -z "$COMPANY_NAME" ] && COMPANY_NAME="顧客名"

# 業界抽出
INDUSTRY=$(echo "$CONTENT" | grep "業界" | head -1 | sed 's/.*業界[：:]*//')
[ -z "$INDUSTRY" ] && INDUSTRY="[業界]"

# 規模抽出
SCALE=$(echo "$CONTENT" | grep "規模" | head -1 | sed 's/.*規模[：:]*//')
[ -z "$SCALE" ] && SCALE="[規模]"

# 課題抽出
ISSUE=$(echo "$CONTENT" | grep "課題" | head -1 | sed 's/.*課題[：:]*//')
[ -z "$ISSUE" ] && ISSUE="[課題]"

# 担当者抽出
CONTACT=$(echo "$CONTENT" | grep "担当者" | head -1 | sed 's/.*担当者[：:]*//')
[ -z "$CONTACT" ] && CONTACT="[担当者]"

echo "   会社名: $COMPANY_NAME"
echo "   業界: $INDUSTRY"
echo "   規模: $SCALE"
echo "   課題: $ISSUE"
echo "   担当者: $CONTACT"

# ステップ4：構成案作成
echo "4. 構成案作成..."
sed "s/\[顧客会社名\]/$COMPANY_NAME/g; s/\[業界\]/$INDUSTRY/g; s/\[規模\]/$SCALE/g; s/\[課題\]/$ISSUE/g" "$TEMPLATES_DIR/outline-template.md" > "$PROPOSAL_DIR/outline.md"

# ステップ5：ピッチ資料作成
echo "5. ピッチ資料作成..."
sed "s/\[顧客会社名\]/$COMPANY_NAME/g; s/\[業界\]/$INDUSTRY/g; s/\[規模\]/$SCALE/g; s/\[課題\]/$ISSUE/g" "$TEMPLATES_DIR/standard-pitch.md" > "$PROPOSAL_DIR/pitch.md"

# ステップ6：PDF出力
echo "6. PDF出力..."
marp "$PROPOSAL_DIR/pitch.md" --pdf --allow-local-files

# ステップ7：案件フォルダに保存
echo "7. 案件フォルダに保存..."
DRAFT_DIR="$SALES_DIR/drafts/${TODAY}_$COMPANY_NAME"
mkdir -p "$DRAFT_DIR"
cp "$PROPOSAL_DIR"/* "$DRAFT_DIR/"

echo "=== 完了 ==="
echo "提案資料: $PROPOSAL_DIR"
echo "案件フォルダ: $DRAFT_DIR"
