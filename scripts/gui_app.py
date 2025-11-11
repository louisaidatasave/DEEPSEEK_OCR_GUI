#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek-OCR GUI 應用程式
使用 CustomTkinter 建立的本地視窗介面
"""

import sys
import os
from pathlib import Path

# 設定 Windows 終端機編碼
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 添加專案根目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gui import MainWindow
from src.logger import setup_logger

# 設定日誌
logger = setup_logger("gui_app", console_output=True, file_output=True)


def setup_local_poppler():
    """設定本地 Poppler 路徑"""
    import os
    poppler_path = Path(__file__).parent.parent / "tools" / "poppler" / "Library" / "bin"
    
    if poppler_path.exists():
        poppler_path_str = str(poppler_path.absolute())
        if poppler_path_str not in os.environ.get('PATH', ''):
            os.environ['PATH'] = poppler_path_str + os.pathsep + os.environ.get('PATH', '')
            logger.info(f"已設定本地 Poppler 路徑: {poppler_path_str}")


def main():
    """主函數"""
    try:
        # 設定本地 Poppler（如果存在）
        setup_local_poppler()
        
        logger.info("啟動 DeepSeek-OCR GUI 應用程式")
        
        # 建立並執行主視窗
        app = MainWindow()
        app.mainloop()
        
        logger.info("應用程式正常關閉")
    
    except Exception as e:
        logger.error(f"應用程式發生錯誤: {e}", exc_info=True)
        import tkinter.messagebox as messagebox
        messagebox.showerror("錯誤", f"應用程式發生錯誤:\n{e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
