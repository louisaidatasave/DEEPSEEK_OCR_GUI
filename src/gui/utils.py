"""
GUI 工具函數
"""

from pathlib import Path
from typing import List
import os


def format_file_size(size_bytes: int) -> str:
    """
    格式化檔案大小
    
    Args:
        size_bytes: 檔案大小（位元組）
        
    Returns:
        格式化的字串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_time(seconds: float) -> str:
    """
    格式化時間
    
    Args:
        seconds: 秒數
        
    Returns:
        格式化的字串
    """
    if seconds < 60:
        return f"{seconds:.1f} 秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} 分鐘"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} 小時"


def get_supported_image_extensions() -> List[str]:
    """
    取得支援的圖片副檔名
    
    Returns:
        副檔名列表
    """
    return ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']


def is_image_file(file_path: Path) -> bool:
    """
    檢查是否為圖片檔案
    
    Args:
        file_path: 檔案路徑
        
    Returns:
        True 如果是圖片檔案
    """
    return file_path.suffix.lower() in get_supported_image_extensions()


def is_pdf_file(file_path: Path) -> bool:
    """
    檢查是否為 PDF 檔案
    
    Args:
        file_path: 檔案路徑
        
    Returns:
        True 如果是 PDF 檔案
    """
    return file_path.suffix.lower() == '.pdf'


def open_file_location(file_path: Path):
    """
    在檔案總管中開啟檔案位置
    
    Args:
        file_path: 檔案路徑
    """
    import subprocess
    
    if not file_path.exists():
        return
    
    if os.name == 'nt':  # Windows
        subprocess.Popen(['explorer', '/select,', str(file_path)])
    elif os.name == 'posix':  # Linux/Mac
        subprocess.Popen(['xdg-open', str(file_path.parent)])


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    截斷文字
    
    Args:
        text: 原始文字
        max_length: 最大長度
        
    Returns:
        截斷後的文字
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def validate_positive_int(value: str, default: int = 1) -> int:
    """
    驗證正整數
    
    Args:
        value: 輸入值
        default: 預設值
        
    Returns:
        驗證後的整數
    """
    try:
        num = int(value)
        return max(1, num)
    except:
        return default


def validate_range(value: int, min_val: int, max_val: int, default: int) -> int:
    """
    驗證範圍
    
    Args:
        value: 輸入值
        min_val: 最小值
        max_val: 最大值
        default: 預設值
        
    Returns:
        驗證後的值
    """
    if min_val <= value <= max_val:
        return value
    return default
