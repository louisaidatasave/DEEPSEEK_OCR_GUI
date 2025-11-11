#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查 Poppler 是否已安裝
"""

import sys
import os
import subprocess

if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 60)
print("Poppler 安裝檢查")
print("=" * 60)
print()

# 檢查 pdftoppm 是否在 PATH 中
print("【檢查 1】pdftoppm 命令")
try:
    result = subprocess.run(['pdftoppm', '-v'], 
                          capture_output=True, 
                          text=True, 
                          timeout=5)
    
    if result.returncode == 0 or 'pdftoppm version' in result.stdout or 'pdftoppm version' in result.stderr:
        version_output = result.stdout + result.stderr
        print("✓ pdftoppm 可用")
        print(f"  版本資訊: {version_output.split(chr(10))[0]}")
        poppler_installed = True
    else:
        print("✗ pdftoppm 無法執行")
        poppler_installed = False

except FileNotFoundError:
    print("✗ pdftoppm 未找到")
    print("  Poppler 未安裝或不在 PATH 中")
    poppler_installed = False

except Exception as e:
    print(f"✗ 檢查失敗: {e}")
    poppler_installed = False

print()

# 檢查 pdf2image 是否可用
print("【檢查 2】pdf2image Python 套件")
try:
    import pdf2image
    print("✓ pdf2image 已安裝")
    print(f"  版本: {pdf2image.__version__ if hasattr(pdf2image, '__version__') else '未知'}")
    pdf2image_installed = True
except ImportError:
    print("✗ pdf2image 未安裝")
    print("  執行: pip install pdf2image")
    pdf2image_installed = False

print()

# 測試 PDF 轉換功能
print("【檢查 3】PDF 轉換功能測試")
if poppler_installed and pdf2image_installed:
    print("✓ 所有依賴已安裝")
    print("  PDF 處理功能應該可以正常使用")
    test_passed = True
else:
    print("✗ 缺少必要依賴")
    if not poppler_installed:
        print("  - 需要安裝 Poppler")
    if not pdf2image_installed:
        print("  - 需要安裝 pdf2image")
    test_passed = False

print()
print("=" * 60)

if test_passed:
    print("✓ 檢查通過！PDF 功能可用")
    print("=" * 60)
    sys.exit(0)
else:
    print("✗ 檢查失敗！需要安裝依賴")
    print("=" * 60)
    print()
    print("請參考安裝指南:")
    print("  docs/POPPLER_INSTALL.md")
    print()
    print("或執行快速安裝（需要管理員權限）:")
    print("  choco install poppler")
    sys.exit(1)
