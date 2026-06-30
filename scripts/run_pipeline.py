#!/usr/bin/env python3
"""
5体パイプラインを実行するスクリプト
"""

import os
import sys
from pathlib import Path
import anthropic
from datetime import datetime, timezone

# 環境変数から情報を取得
THEME_NAME = os.environ.get("THEME_NAME", "")
DATE = os.environ.get("DATE", datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d"))

# エージェントのパス
AGENTS_DIR = Path("agents")
INPUTS_DIR = Path("inputs/themes")
OUTPUTS_DIR = Path("outputs/themes")

def run_agent(agent_name: str, input_content: str) -> str:
    """エージェントを実行して出力を取得"""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # エージェント定義を読み込む
    agent_file = AGENTS_DIR / f"{agent_name}.md"
    if not agent_file.exists():
        raise FileNotFoundError(f"Agent file not found: {agent_file}")

    with open(agent_file, "r", encoding="utf-8") as f:
        agent_definition = f.read()

    # Claude APIを呼び出し
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=agent_definition,
        messages=[
            {"role": "user", "content": input_content}
        ]
    )

    return message.content[0].text

def create_input_file():
    """入力ファイルを作成"""
    theme_folder = INPUTS_DIR / f"{DATE}_{THEME_NAME}"
    theme_folder.mkdir(parents=True, exist_ok=True)

    input_file = theme_folder / "input.md"
    if not input_file.exists():
        content = f"""# テーマ: {THEME_NAME}

## 日付
{DATE}

## ブリーフ
このテーマについての記事を作成してください。

## 読者像
- AIツールに興味があるビジネスパーソン
- 効率化に関心のある層
"""
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(content)

    return str(input_file)

def save_output(stage: str, content: str):
    """出力を保存"""
    output_folder = OUTPUTS_DIR / f"{DATE}_{THEME_NAME}"
    output_folder.mkdir(parents=True, exist_ok=True)

    stage_files = {
        "strategist": "01-angle.md",
        "researcher": "02-research.md",
        "writer": "03-draft.md",
        "editor": "04-edited.md",
        "publisher": "05-final.md"
    }

    output_file = output_folder / stage_files.get(stage, f"{stage}.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {output_file}")

def main():
    """メイン処理"""
    print(f"Starting pipeline for theme: {THEME_NAME}")

    # 入力ファイルを作成
    input_file = create_input_file()
    print(f"Input file: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        input_content = f.read()

    # パイプラインステージ
    stages = [
        ("strategist", "角度決め"),
        ("researcher", "リサーチ"),
        ("writer", "ドラフト作成"),
        ("editor", "編集"),
        ("publisher", "最終出力")
    ]

    current_input = input_content

    for stage, description in stages:
        print(f"\n{'='*50}")
        print(f"Stage: {description} ({stage})")
        print(f"{'='*50}")

        try:
            output = run_agent(stage, current_input)
            save_output(stage, output)
            current_input = output
        except Exception as e:
            print(f"Error in {stage}: {e}")
            sys.exit(1)

    print("\n" + "="*50)
    print("Pipeline completed successfully!")
    print("="*50)

if __name__ == "__main__":
    from datetime import timedelta
    main()
