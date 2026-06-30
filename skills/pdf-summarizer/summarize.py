#!/usr/bin/env python3
"""
PDF要約スキルのスクリプト
PDFファイルを読み込み、要約して適切なフォルダに保存する
"""

import re
import os
from datetime import datetime
from pathlib import Path


def get_summary_filename(original_path):
    """元のファイル名から要約ファイル名を生成する"""
    filename = Path(original_path).stem

    # 不要な文字を除去し、わかりやすいファイル名にする
    # 空白や特殊文字をアンダースコアに置換
    cleaned = re.sub(r'[\\/*?:"<>|]', '_', filename)
    cleaned = re.sub(r'\s+', '_', cleaned)

    # 全角スペースをアンダースコアに置換
    cleaned = cleaned.replace('　', '_')

    # 括弧内の内容を保持しつつ、わかりやすく
    cleaned = re.sub(r'\(([^)]+)\)', r'_\1', cleaned)

    # 要約サフィックスを付加
    return f"{cleaned}_要約.md"


def extract_subject_from_path(file_path, base_dir="大学授業"):
    """ファイルパスから教科名を抽出する"""
    path = Path(file_path)

    # ベースディレクトリから教科フォルダを探す
    for part in path.parts:
        if part != base_dir and "授業" not in part and part not in ["OneDrive", "Tetsu", "Users", "c:", ""]:
            # 大学授業以下の最初のサブディレクトリを教科とみなす
            if "大学授業" in str(path):
                idx = list(path.parts).index("大学授業")
                if idx + 1 < len(path.parts):
                    return path.parts[idx + 1]

    # 見つからない場合は現在のディレクトリ名
    return path.parent.name


def get_subject_folder(file_path, base_dir="c:/Users/Tetsu/OneDrive/大学授業"):
    """教科フォルダのパスを取得する"""
    path = Path(file_path)
    subject = extract_subject_from_path(file_path)

    # 教科フォルダのパスを作成
    subject_folder = Path(base_dir) / subject

    # 教科フォルダが存在するか確認
    if not subject_folder.exists():
        # 見つからない場合はファイルのあるディレクトリを使用
        return path.parent

    return subject_folder


def create_summary_markdown(content, original_file_path):
    """要約のMarkdown形式を作成する"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    original_filename = Path(original_file_path).name
    subject = extract_subject_from_path(original_file_path)

    return f"""# {subject} - 要約

## 概要
{content.get('overview', '内容の要約')}

## 主要ポイント
{chr(10).join(f'- {p}' for p in content.get('points', []))}

## 詳細内容
{chr(10).join(f"### {section}{chr(10)}{details}{chr(10)}" for section, details in content.get('details', {}).items())}

## 重要キーワード
{chr(10).join(f'- {kw}' for kw in content.get('keywords', []))}

---
元のファイル: {original_filename}
作成日: {now}
"""


def summarize_pdf(pdf_path, summary_content, target_folder=None):
    """PDFを要約して保存する

    Args:
        pdf_path: PDFファイルのパス
        summary_content: 要約内容の辞書
        target_folder: 保存先フォルダのパス（省略時は自動判定）
    """
    # 保存先フォルダを決定
    if target_folder:
        # ユーザーが指定したフォルダを使用
        subject_folder = Path(target_folder)
    else:
        # 自動判定
        subject_folder = get_subject_folder(pdf_path)

    # 要約ファイル名を生成
    summary_filename = get_summary_filename(pdf_path)
    summary_path = subject_folder / summary_filename

    # Markdownを作成
    markdown_content = create_summary_markdown(summary_content, pdf_path)

    return {
        'summary_path': str(summary_path),
        'markdown_content': markdown_content,
        'subject_folder': str(subject_folder)
    }


if __name__ == '__main__':
    # テスト用
    test_path = "経営学概論/経営学概論　(4.社会の中の企業).pdf"
    test_folder = "c:/Users/Tetsu/OneDrive/大学授業/経営学概論"
    test_content = {
        'overview': '企業と社会の関係性についての講義資料',
        'points': ['企業の社会的責任', 'ステークホルダー理論', '企業統治'],
        'details': {
            '企業の社会的責任': '企業は利益追求だけでなく、社会に対する責任も果たす必要がある',
            'ステークホルダー理論': '株主だけでなく、従業員、顧客、地域社会など全てのステークホルダーを考慮する'
        },
        'keywords': ['CSR', 'ステークホルダー', '企業統治', 'サステナビリティ']
    }

    # ターゲットフォルダを指定した場合
    result = summarize_pdf(test_path, test_content, target_folder=test_folder)
    print(f"要約ファイルパス: {result['summary_path']}")
    print(f"教科フォルダ: {result['subject_folder']}")

    # ターゲットフォルダを指定しない場合（自動判定）
    result2 = summarize_pdf(test_path, test_content)
    print(f"\n（自動判定）要約ファイルパス: {result2['summary_path']}")
    print(f"（自動判定）教科フォルダ: {result2['subject_folder']}")