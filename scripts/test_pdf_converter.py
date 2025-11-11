#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試 PDF 轉換模組"""

import sys
import os

if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, '.')

from src.pdf_converter import PDFConverter, get_pdf_info
from pathlib import Path

print("=" * 60)
print("PDF 轉換模組測試")
print("=" * 60)
print()

# 建立測試 PDF（如果沒有真實 PDF，會跳過測試）
test_pdf_paths = [
    "test.pdf",
    "sample.pdf",
    "document.pdf"
]

# 尋找可用的測試 PDF
test_pdf = None
for pdf_path in test_pdf_paths:
    if Path(pdf_path).exists():
        test_pdf = pdf_path
        break

if not test_pdf:
    print("⚠ 找不到測試 PDF 檔案")
    print("建立模擬測試...")
    
    # 測試 PDF 資訊功能（使用不存在的檔案）
    print("\n【測試 1】PDF 資訊檢查（不存在的檔案）")
    info = get_pdf_info("nonexistent.pdf")
    print(f"檔案存在: {info.get('exists', False)}")
    if 'error' in info:
        print(f"錯誤: {info['error']}")
    
    print("\n【測試 2】PDF 轉換器初始化")
    converter = PDFConverter(dpi=150, output_format='PNG', max_pages=10)
    print(f"✓ 轉換器建立成功")
    print(f"  DPI: {converter.dpi}")
    print(f"  格式: {converter.output_format}")
    print(f"  最大頁數: {converter.max_pages}")
    
    print("\n【測試 3】轉換不存在的 PDF")
    result = converter.convert_pdf(
        "nonexistent.pdf",
        "outputs/pdf_test"
    )
    print(f"轉換成功: {result.success}")
    print(f"錯誤訊息: {result.error_message}")
    
else:
    print(f"找到測試 PDF: {test_pdf}")
    
    # 測試 PDF 資訊
    print("\n【測試 1】PDF 資訊")
    info = get_pdf_info(test_pdf)
    if info.get('exists'):
        print(f"檔案: {info['file_name']}")
        print(f"大小: {info['file_size_mb']:.2f} MB")
        print(f"總頁數: {info['total_pages']}")
        print(f"第一頁尺寸: {info['first_page_size']}")
        print(f"預估轉換時間: {info['estimated_conversion_time']} 秒")
    else:
        print(f"錯誤: {info.get('error')}")
    
    # 測試轉換
    print("\n【測試 2】PDF 轉換（前 3 頁）")
    converter = PDFConverter(dpi=150, max_pages=3)
    result = converter.convert_pdf(
        test_pdf,
        "outputs/pdf_test",
        prefix="test_page"
    )
    
    print(f"轉換成功: {result.success}")
    if result.success:
        print(f"總頁數: {result.total_pages}")
        print(f"已轉換: {result.converted_pages}")
        print(f"輸出目錄: {result.output_dir}")
        print("生成的圖片:")
        for img_path in result.image_paths:
            print(f"  - {Path(img_path).name}")
    else:
        print(f"錯誤: {result.error_message}")
    
    # 測試單頁轉換
    print("\n【測試 3】單頁轉換（第 1 頁）")
    single_result = converter.convert_single_page(
        test_pdf,
        "outputs/pdf_single",
        1,
        prefix="single_page"
    )
    
    print(f"轉換成功: {single_result.success}")
    if single_result.success:
        print(f"轉換頁數: {single_result.converted_pages}")
        print(f"圖片檔案: {single_result.image_paths}")

print("\n=" * 60)
print("✓ 測試完成！")
print("=" * 60)
print()
print("注意: 如需完整測試，請將 PDF 檔案放在專案根目錄")
print("支援的檔名: test.pdf, sample.pdf, document.pdf")
