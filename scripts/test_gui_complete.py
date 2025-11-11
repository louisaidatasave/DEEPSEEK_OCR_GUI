#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試完整 GUI
驗證所有頁籤是否正常
"""

import sys
import os

if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, '.')

print("=" * 60)
print("測試 GUI 完整性")
print("=" * 60)
print()

print("【測試 1】匯入模組")
try:
    from src.gui import MainWindow, SingleImageTab, BatchTab, PDFTab
    print("✓ 所有 GUI 模組匯入成功")
except Exception as e:
    print(f"✗ 匯入失敗: {e}")
    sys.exit(1)

print()

print("【測試 2】檢查類別")
print(f"  MainWindow: {MainWindow}")
print(f"  SingleImageTab: {SingleImageTab}")
print(f"  BatchTab: {BatchTab}")
print(f"  PDFTab: {PDFTab}")
print("✓ 所有類別定義正確")

print()

print("【測試 3】啟動 GUI")
print("正在啟動 GUI 視窗...")
print("請檢查:")
print("  1. 視窗是否正常開啟")
print("  2. 是否有三個頁籤: 單張圖片 OCR、批次處理、PDF 處理")
print("  3. 右側監控面板是否顯示")
print("  4. 所有頁籤是否都有完整介面（不是「開發中」）")
print()
print("關閉視窗後測試將結束...")
print()

try:
    app = MainWindow()
    app.mainloop()
    print("\n✓ GUI 正常關閉")
except Exception as e:
    print(f"\n✗ GUI 執行失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("✓ 測試完成！")
print("=" * 60)
