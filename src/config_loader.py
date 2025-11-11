"""
配置載入模組
載入和管理系統配置
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置載入器類別"""
    
    def __init__(self, config_path: str = "config/system_config.json"):
        """
        初始化配置載入器
        
        Args:
            config_path: 配置檔案路徑
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        載入配置檔案
        
        Returns:
            配置字典
        """
        if not self.config_path.exists():
            logger.warning(f"配置檔案不存在: {self.config_path}，使用預設配置")
            self.config = self._get_default_config()
            return self.config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info(f"配置檔案載入成功: {self.config_path}")
            return self.config
        except Exception as e:
            logger.error(f"配置檔案載入失敗: {e}")
            self.config = self._get_default_config()
            return self.config
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        取得配置值（支援巢狀鍵值）
        
        Args:
            key_path: 鍵值路徑，例如 "device.type"
            default: 預設值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        設定配置值（支援巢狀鍵值）
        
        Args:
            key_path: 鍵值路徑，例如 "device.type"
            value: 配置值
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save_config(self, output_path: Optional[str] = None):
        """
        儲存配置到檔案
        
        Args:
            output_path: 輸出路徑，None 則使用原路徑
        """
        save_path = Path(output_path) if output_path else self.config_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置已儲存至: {save_path}")
        except Exception as e:
            logger.error(f"配置儲存失敗: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """取得預設配置"""
        return {
            "project": {
                "name": "DeepSeek-OCR",
                "version": "1.0.0"
            },
            "paths": {
                "model_dir": "./models/deepseek-ocr",
                "output_dir": "./outputs",
                "log_dir": "./outputs/logs"
            },
            "device": {
                "type": "cuda",
                "fallback_to_cpu": True
            },
            "model": {
                "torch_dtype": "bfloat16",
                "base_size": 1024,
                "image_size": 1024
            },
            "logging": {
                "level": "INFO",
                "console_output": True,
                "file_output": True
            }
        }
    
    def get_model_config(self) -> Dict[str, Any]:
        """取得模型配置"""
        return self.get("model", {})
    
    def get_device_config(self) -> Dict[str, Any]:
        """取得裝置配置"""
        return self.get("device", {})
    
    def get_paths_config(self) -> Dict[str, Any]:
        """取得路徑配置"""
        return self.get("paths", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """取得日誌配置"""
        return self.get("logging", {})
    
    def print_config(self):
        """列印配置"""
        print(json.dumps(self.config, ensure_ascii=False, indent=2))


# 全域配置載入器實例
_global_config = None


def get_config(config_path: str = "config/system_config.json") -> ConfigLoader:
    """
    取得全域配置載入器實例
    
    Args:
        config_path: 配置檔案路徑
        
    Returns:
        ConfigLoader 實例
    """
    global _global_config
    if _global_config is None:
        _global_config = ConfigLoader(config_path)
    return _global_config


def reload_config(config_path: str = "config/system_config.json") -> ConfigLoader:
    """
    重新載入配置
    
    Args:
        config_path: 配置檔案路徑
        
    Returns:
        ConfigLoader 實例
    """
    global _global_config
    _global_config = ConfigLoader(config_path)
    return _global_config
