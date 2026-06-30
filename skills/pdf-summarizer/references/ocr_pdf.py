#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF OCR処理スクリプト
PyMuPDFとpytesseractを使ってPDFからテキストを抽出する
"""

import fitz  # PyMuPDF
import pytesseract
import os
import sys
from PIL import Image
import io

# Tesseractのパス（Windows環境）
tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
tessdata_path = r"C:\Users\Tetsu\tessdata"

# Tesseractの設定
pytesseract.pytesseract.tesseract_cmd = tesseract_path
os.environ['TESSDATA_PREFIX'] = tessdata_path

def pdf_to_ocr_text(pdf_path, output_path=None, max_pages=None):
    """
    PDFをOCR処理してテキストを抽出する

    Args:
        pdf_path: PDFファイルのパス
        output_path: テキストファイルの出力先（省略可）
        max_pages: 処理する最大ページ数（省略可）

    Returns:
        抽出されたテキスト
    """
    # PDFを開く
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    print(f"PDFの総ページ数: {total_pages}")

    # 処理するページ数を決定
    if max_pages is None or max_pages > total_pages:
        max_pages = total_pages

    all_text = []

    for page_num in range(max_pages):
        print(f"ページ {page_num + 1}/{max_pages} を処理中...")

        # ページを取得
        page = doc[page_num]

        # ページを画像に変換（高解像度でOCR精度向上）
        mat = fitz.Matrix(3.0, 3.0)  # 3倍の解像度
        pix = page.get_pixmap(matrix=mat)

        # PIL Imageに変換
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))

        # OCR処理（日本語と英語）
        text = pytesseract.image_to_string(
            img,
            lang='jpn+eng',
            config='--psm 6 -c preserve_interword_spaces=1'
        )

        all_text.append(f"--- ページ {page_num + 1} ---\n{text}\n")

    doc.close()

    # 全テキストを結合
    full_text = "\n".join(all_text)

    # ファイルに出力
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"\nテキストを保存しました: {output_path}")

    return full_text


def main():
    """メイン処理"""
    import sys

    # コマンドライン引数からPDFファイルパスを取得
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # デフォルトのPDFファイルパス
        pdf_path = r"C:\Users\Tetsu\OneDrive\大学授業\経営導入基礎Ⅰ\②_経営導入基礎Ⅰ【26・前期・火曜日】【共有用】 (1).pdf"

    # 出力ファイルのパス（PDFと同じフォルダ）
    import os
    pdf_dir = os.path.dirname(pdf_path)
    if pdf_dir:
        output_path = os.path.join(pdf_dir, "ocr_output.txt")
    else:
        output_path = r"C:\Users\Tetsu\OneDrive\大学授業\経営導入基礎Ⅰ\ocr_output.txt"

    # 全ページを処理
    print("OCR処理を開始します...")
    print(f"PDFファイル: {pdf_path}")
    print(f"出力ファイル: {output_path}")

    try:
        text = pdf_to_ocr_text(pdf_path, output_path, max_pages=None)
        print("\n全ページのOCR処理が完了しました！")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
