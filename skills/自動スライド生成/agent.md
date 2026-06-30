# 毎日議事録→提案資料 エージェント

## 役割

議事録から顧客情報を抽出し、提案資料（構成案・ピッチ資料・PDF）を自動生成します。

## 実行手順

### ステップ1：今日の議事録フォルダを確認

```bash
ls meetings/$(date +%Y-%m-%d)/transcripts/
```

### ステップ2：文字起こしファイルを読み込む

`transcripts/` 内のファイルをすべて読み込みます。

### ステップ3：顧客情報を抽出

議事録から以下の情報を抽出：

| 項目 | 抽出方法 |
|------|----------|
| 顧客名 | 会社名として言及されている部分 |
| 業界 | 製造業/サービス業/IT/など |
| 規模 | 従業員数や年商 |
| 課題 | 困っていること、改善したいこと |
| 担当者 | 名前や役職 |

### ステップ4：構成案を作成

`templates/outline-template.md` をベースに、抽出した顧客情報で埋めて `meetings/YYYY-MM-DD/proposals/outline.md` に保存。

### ステップ5：ピッチ資料を作成

`templates/standard-pitch.md` をベースに、抽出した顧客情報で埋めて `meetings/YYYY-MM-DD/proposals/pitch.md` に保存。

### ステップ6：PDFを出力

```bash
marp meetings/$(date +%Y-%m-%d)/proposals/pitch.md --pdf
```

### ステップ7：案件フォルダにコピー

```bash
cp -r meetings/$(date +%Y-%m-%d)/proposals drafts/$(date +%Y-%m-%d)_[顧客名]/
```

## 出力場所

- 議事録: `meetings/YYYY-MM-DD/transcripts/`
- 提案資料: `meetings/YYYY-MM-DD/proposals/`
- 案件フォルダ: `drafts/YYYY-MM-DD_顧客名/`

## 品質基準

- 顧客名が正確に抽出されている
- 課題が具体的に記載されている
- IPブランド（黒×青×白）が守られている
- PDFが正常に出力されている
