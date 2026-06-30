# 1. Strategist を呼ぶ
$ claude /agents content-strategist
# 入力: テーマ + 読者像 + プラットフォーム
# 出力: angle.md (角度 + フック + ブリーフ + 書かないこと)
# 2. Researcher に渡す
$ claude /agents content-researcher
# 入力: angle.md + ハンドオフ情報
# 出力: research.md (一次情報 + 主要事実 + 反証データ)
# 3. Writer に渡す
$ claude /agents content-writer
# 入力: angle.md + research.md + ハンドオフ情報
# 出力: draft.md (フルドラフト)
# 4. Editor に渡す
$ claude /agents content-editor
# 入力: draft.md + ハンドオフ情報
# 出力: edited.md (30% 削った版 + 変更ログ)
# 5. Publisher に渡す
$ claude /agents content-publisher
# 入力: edited.md + プラットフォーム指定 + ハンドオフ情報
# 出力: final.md (公開可能形式)