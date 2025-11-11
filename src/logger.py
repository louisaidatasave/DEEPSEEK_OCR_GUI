"""
日誌模組
提供統一的日誌記錄功能
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """彩色日誌格式化器（Windows 終端機支援）"""
    
    # ANSI 顏色代碼
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 綠色
        'WARNING': '\033[33m',    # 黃色
        'ERROR': '\033[31m',      # 紅色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def format(self, record):
        # 添加顏色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(
    name: str = "deepseek_ocr",
    log_dir: str = "outputs/logs",
    log_level: int = logging.INFO,
    console_output: bool = True,
    file_output: bool = True,
    colored: bool = True
) -> logging.Logger:
    """
    設定日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        log_dir: 日誌檔案目錄
        log_level: 日誌等級
        console_output: 是否輸出到終端機
        file_output: 是否輸出到檔案
        colored: 終端機輸出是否使用彩色
        
    Returns:
        配置好的 Logger 物件
    """
    # 建立 logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 避免重複添加 handler
    if logger.handlers:
        return logger
    
    # 日誌格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 終端機輸出
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        if colored:
            console_formatter = ColoredFormatter(log_format, datefmt=date_format)
        else:
            console_formatter = logging.Formatter(log_format, datefmt=date_format)
        
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # 檔案輸出
    if file_output:
        # 建立日誌目錄
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # 日誌檔案名稱（包含日期）
        log_filename = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        log_file = log_path / log_filename
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"日誌檔案: {log_file}")
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    取得日誌記錄器
    
    Args:
        name: 日誌記錄器名稱，None 則使用預設
        
    Returns:
        Logger 物件
    """
    if name is None:
        name = "deepseek_ocr"
    
    logger = logging.getLogger(name)
    
    # 如果 logger 還沒設定，使用預設設定
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


# 便利函數
def log_info(message: str, logger_name: Optional[str] = None):
    """記錄 INFO 等級日誌"""
    logger = get_logger(logger_name)
    logger.info(message)


def log_warning(message: str, logger_name: Optional[str] = None):
    """記錄 WARNING 等級日誌"""
    logger = get_logger(logger_name)
    logger.warning(message)


def log_error(message: str, logger_name: Optional[str] = None):
    """記錄 ERROR 等級日誌"""
    logger = get_logger(logger_name)
    logger.error(message)


def log_debug(message: str, logger_name: Optional[str] = None):
    """記錄 DEBUG 等級日誌"""
    logger = get_logger(logger_name)
    logger.debug(message)


def log_critical(message: str, logger_name: Optional[str] = None):
    """記錄 CRITICAL 等級日誌"""
    logger = get_logger(logger_name)
    logger.critical(message)


# 初始化預設 logger
_default_logger = setup_logger()
