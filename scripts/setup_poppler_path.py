#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定本地 Poppler 路徑
將專案本地的 Poppler 加入 PATH（僅當前 Python 程序）
"""

import os
import sys
from pathlib import Path

# 本地 Poppler 路徑
POPPLER_LOCAL_PATH = Path(__file__).parent.parent / "tools" / "poppler" / "Library" / "bin"

def setup_poppler_path():
    """設定 Poppler 路徑"""
    if POPPLER_LOCAL_PATH.exists():
        poppler_path_str = str(POPPLER_LOCAL_PATH.absolute())
        
        # 加入到當前程序的 PATH
        if poppler_path_str not in os.environ.get('PATH', ''):
            os.environ['PATH'] = poppler_path_str + os.pathsep + os.environ.get('PATH', '')
            print(f"✓ 已設定本地 Poppler 路徑: {poppler_path_str}")
            return True
        else:
            print(f"✓ Poppler 路徑已存在")
            return True
    else:
        print(f"✗ 本地 Poppler 不存在: {POPPLER_LOCAL_PATH}")
        print(f"  請執行: .\\scripts\\install_poppler_local.ps1")
        return False

def verify_poppler():
    """驗證 Poppler 是否可用"""
    import subprocess
    
    try:
        result = subprocess.run(['pdftoppm', '-v'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        if result.returncode == 0 or 'pdftoppm version' in (result.stdout + result.stderr):
            print("✓ Poppler 可用")
            return True
        else:
            print("✗ Poppler 無法執行")
            return False
    
    except FileNotFoundError:
        print("✗ pdftoppm 未找到")
        return False
    except Exception as e:
        print(f"✗ 驗證失敗: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("設定本地 Poppler 路徑")
    print("=" * 60)
    print()
    
    if setup_poppler_path():
        print()
        print("驗證 Poppler...")
        if verify_poppler():
            print()
            print("✓ Poppler 設定成功！PDF 功能可用")
        else:
            print()
            print("✗ Poppler 驗證失敗")
    else:
        print()
        print("✗ 設定失敗")
        print()
        print("請先安裝本地 Poppler:")
        print("  .\\scripts\\install_poppler_local.ps1")
    
    print()
    print("=" * 60)
