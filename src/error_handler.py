"""
錯誤處理模組
定義自訂錯誤類別和錯誤處理策略
"""

import time
import logging
from typing import Callable, Any, Optional, Dict
from functools import wraps

logger = logging.getLogger(__name__)


# ==================== 自訂錯誤類別 ====================

class DeepSeekOCRError(Exception):
    """DeepSeek-OCR 基礎錯誤類別"""
    def __init__(self, message: str, suggestion: Optional[str] = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(self.message)
    
    def __str__(self):
        if self.suggestion:
            return f"{self.message}\n建議: {self.suggestion}"
        return self.message


class CUDANotAvailableError(DeepSeekOCRError):
    """CUDA 不可用錯誤"""
    def __init__(self):
        super().__init__(
            "CUDA 不可用，無法使用 GPU 加速",
            "請檢查: 1) NVIDIA 驅動是否安裝 2) PyTorch CUDA 版本是否正確 3) 執行 nvidia-smi 確認 GPU 狀態"
        )


class ModelLoadError(DeepSeekOCRError):
    """模型載入錯誤"""
    def __init__(self, model_path: str, original_error: str):
        super().__init__(
            f"模型載入失敗: {model_path}\n原因: {original_error}",
            "請檢查: 1) 模型路徑是否正確 2) 模型檔案是否完整 3) 是否有足夠的記憶體"
        )


class ImageProcessingError(DeepSeekOCRError):
    """圖片處理錯誤"""
    def __init__(self, image_path: str, original_error: str):
        super().__init__(
            f"圖片處理失敗: {image_path}\n原因: {original_error}",
            "請檢查: 1) 圖片檔案是否存在 2) 圖片格式是否支援 3) 圖片是否損壞"
        )


class OutOfMemoryError(DeepSeekOCRError):
    """記憶體不足錯誤"""
    def __init__(self, memory_type: str = "VRAM"):
        super().__init__(
            f"{memory_type} 記憶體不足",
            "請嘗試: 1) 減少批次大小 2) 降低圖片解析度 3) 使用 CPU 模式 4) 關閉其他程式釋放記憶體"
        )


class PDFConversionError(DeepSeekOCRError):
    """PDF 轉換錯誤"""
    def __init__(self, pdf_path: str, original_error: str):
        super().__init__(
            f"PDF 轉換失敗: {pdf_path}\n原因: {original_error}",
            "請檢查: 1) PDF 檔案是否存在 2) PDF 是否損壞 3) 是否安裝 poppler"
        )


class ConfigurationError(DeepSeekOCRError):
    """配置錯誤"""
    def __init__(self, config_item: str, issue: str):
        super().__init__(
            f"配置錯誤: {config_item}\n問題: {issue}",
            "請檢查配置檔案是否正確"
        )


# ==================== 錯誤處理策略 ====================

def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    重試裝飾器
    
    Args:
        max_retries: 最大重試次數
        delay: 初始延遲時間（秒）
        backoff: 延遲時間倍增係數
        exceptions: 需要重試的例外類型
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"{func.__name__} 失敗 (嘗試 {attempt + 1}/{max_retries + 1}): {str(e)}"
                        )
                        logger.info(f"等待 {current_delay:.1f} 秒後重試...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"{func.__name__} 達到最大重試次數，放棄")
            
            raise last_exception
        
        return wrapper
    return decorator


def fallback_on_error(fallback_func: Callable, exceptions: tuple = (Exception,)):
    """
    Fallback 裝飾器：當主函數失敗時，執行備用函數
    
    Args:
        fallback_func: 備用函數
        exceptions: 需要 fallback 的例外類型
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                logger.warning(f"{func.__name__} 失敗: {str(e)}")
                logger.info(f"嘗試使用 fallback: {fallback_func.__name__}")
                return fallback_func(*args, **kwargs)
        
        return wrapper
    return decorator


def log_errors(logger_name: Optional[str] = None):
    """
    錯誤日誌裝飾器：自動記錄錯誤
    
    Args:
        logger_name: 日誌記錄器名稱
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            error_logger = logging.getLogger(logger_name or __name__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_logger.error(
                    f"函數 {func.__name__} 發生錯誤: {type(e).__name__}: {str(e)}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    default_return: Any = None,
    error_message: Optional[str] = None,
    log_error: bool = True
) -> Any:
    """
    安全執行函數，捕捉所有錯誤
    
    Args:
        func: 要執行的函數
        default_return: 發生錯誤時的預設返回值
        error_message: 自訂錯誤訊息
        log_error: 是否記錄錯誤
        
    Returns:
        函數執行結果或預設返回值
    """
    try:
        return func()
    except Exception as e:
        if log_error:
            msg = error_message or f"執行 {func.__name__} 時發生錯誤"
            logger.error(f"{msg}: {str(e)}")
        return default_return


# ==================== 錯誤處理輔助函數 ====================

def handle_cuda_error() -> Dict[str, Any]:
    """
    處理 CUDA 相關錯誤
    
    Returns:
        錯誤處理結果字典
    """
    import torch
    
    if not torch.cuda.is_available():
        logger.error("CUDA 不可用")
        return {
            'cuda_available': False,
            'suggestion': 'CPU 模式運行或檢查 CUDA 安裝',
            'fallback': 'cpu'
        }
    
    try:
        # 嘗試清理 CUDA 快取
        torch.cuda.empty_cache()
        logger.info("CUDA 快取已清理")
        return {
            'cuda_available': True,
            'action': 'cache_cleared'
        }
    except Exception as e:
        logger.error(f"CUDA 錯誤處理失敗: {e}")
        return {
            'cuda_available': False,
            'error': str(e),
            'fallback': 'cpu'
        }


def handle_memory_error(error: Exception) -> Dict[str, Any]:
    """
    處理記憶體錯誤
    
    Args:
        error: 記憶體錯誤例外
        
    Returns:
        錯誤處理結果字典
    """
    import torch
    import gc
    
    logger.warning("偵測到記憶體錯誤，嘗試清理...")
    
    # 清理 Python 垃圾回收
    gc.collect()
    
    # 清理 CUDA 快取
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    return {
        'action': 'memory_cleared',
        'suggestion': '減少批次大小或降低圖片解析度',
        'error': str(error)
    }


def get_error_solution(error: Exception) -> str:
    """
    根據錯誤類型提供解決方案
    
    Args:
        error: 例外物件
        
    Returns:
        解決方案字串
    """
    error_type = type(error).__name__
    
    solutions = {
        'FileNotFoundError': '檔案不存在，請檢查路徑是否正確',
        'PermissionError': '權限不足，請以管理員身份執行或檢查檔案權限',
        'MemoryError': '記憶體不足，請關閉其他程式或減少批次大小',
        'RuntimeError': '執行時錯誤，請檢查 CUDA 和模型配置',
        'ValueError': '參數值錯誤，請檢查輸入參數',
        'TypeError': '類型錯誤，請檢查參數類型',
        'ImportError': '模組匯入失敗，請檢查套件是否安裝',
        'KeyError': '鍵值不存在，請檢查配置檔案',
    }
    
    if isinstance(error, DeepSeekOCRError):
        return error.suggestion or "請查看錯誤訊息"
    
    return solutions.get(error_type, "未知錯誤，請查看詳細錯誤訊息")
