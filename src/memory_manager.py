"""
記憶體管理模組
監控 VRAM 使用、自動清理快取、動態調整批次大小
"""

import torch
import gc
from typing import Dict, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MemoryInfo:
    """記憶體資訊資料類別"""
    vram_used_gb: float
    vram_total_gb: float
    vram_free_gb: float
    vram_usage_percent: float
    cuda_available: bool
    device_name: str = ""


class MemoryManager:
    """記憶體管理器類別"""
    
    def __init__(self, vram_threshold: float = 0.9):
        """
        初始化記憶體管理器
        
        Args:
            vram_threshold: VRAM 使用率警戒值（0-1）
        """
        self.vram_threshold = vram_threshold
        self.cuda_available = torch.cuda.is_available()
        
        if self.cuda_available:
            self.device_count = torch.cuda.device_count()
            self.device_name = torch.cuda.get_device_name(0)
            logger.info(f"MemoryManager 初始化，GPU: {self.device_name}")
        else:
            self.device_count = 0
            self.device_name = "CPU"
            logger.warning("CUDA 不可用，使用 CPU 模式")
        
        logger.info(f"VRAM 警戒值: {vram_threshold * 100:.1f}%")
    
    def get_vram_usage(self, device: int = 0) -> MemoryInfo:
        """
        取得 VRAM 使用資訊
        
        Args:
            device: GPU 裝置編號
            
        Returns:
            MemoryInfo 物件
        """
        if not self.cuda_available:
            return MemoryInfo(
                vram_used_gb=0.0,
                vram_total_gb=0.0,
                vram_free_gb=0.0,
                vram_usage_percent=0.0,
                cuda_available=False,
                device_name="CPU"
            )
        
        try:
            # 取得記憶體資訊
            vram_used = torch.cuda.memory_allocated(device) / 1024**3
            vram_total = torch.cuda.get_device_properties(device).total_memory / 1024**3
            vram_free = vram_total - vram_used
            vram_usage_percent = (vram_used / vram_total) * 100
            
            return MemoryInfo(
                vram_used_gb=vram_used,
                vram_total_gb=vram_total,
                vram_free_gb=vram_free,
                vram_usage_percent=vram_usage_percent,
                cuda_available=True,
                device_name=self.device_name
            )
        
        except Exception as e:
            logger.error(f"取得 VRAM 資訊失敗: {e}")
            return MemoryInfo(
                vram_used_gb=0.0,
                vram_total_gb=0.0,
                vram_free_gb=0.0,
                vram_usage_percent=0.0,
                cuda_available=False
            )
    
    def clear_cache(self, device: int = 0):
        """
        清理 GPU 快取
        
        Args:
            device: GPU 裝置編號
        """
        if not self.cuda_available:
            logger.debug("CUDA 不可用，跳過快取清理")
            return
        
        try:
            # 記錄清理前的使用量
            before = self.get_vram_usage(device)
            
            # 清理快取
            torch.cuda.empty_cache()
            gc.collect()
            
            # 記錄清理後的使用量
            after = self.get_vram_usage(device)
            
            freed = before.vram_used_gb - after.vram_used_gb
            logger.info(f"快取清理完成，釋放 {freed:.2f} GB VRAM")
            
        except Exception as e:
            logger.error(f"快取清理失敗: {e}")
    
    def check_vram_available(self, required_gb: float, device: int = 0) -> bool:
        """
        檢查是否有足夠的 VRAM
        
        Args:
            required_gb: 需要的 VRAM 量（GB）
            device: GPU 裝置編號
            
        Returns:
            True 如果有足夠 VRAM
        """
        if not self.cuda_available:
            return False
        
        memory_info = self.get_vram_usage(device)
        available = memory_info.vram_free_gb
        
        logger.debug(f"檢查 VRAM: 需要 {required_gb:.2f} GB，可用 {available:.2f} GB")
        return available >= required_gb
    
    def is_vram_critical(self, device: int = 0) -> bool:
        """
        檢查 VRAM 使用是否達到警戒值
        
        Args:
            device: GPU 裝置編號
            
        Returns:
            True 如果達到警戒值
        """
        if not self.cuda_available:
            return False
        
        memory_info = self.get_vram_usage(device)
        usage_ratio = memory_info.vram_usage_percent / 100
        
        is_critical = usage_ratio >= self.vram_threshold
        
        if is_critical:
            logger.warning(
                f"VRAM 使用率達到警戒值: {memory_info.vram_usage_percent:.1f}% "
                f"(警戒值: {self.vram_threshold * 100:.1f}%)"
            )
        
        return is_critical
    
    def calculate_optimal_batch_size(
        self,
        base_batch_size: int,
        image_size: Tuple[int, int],
        device: int = 0
    ) -> int:
        """
        根據 VRAM 使用情況計算最佳批次大小
        
        Args:
            base_batch_size: 基礎批次大小
            image_size: 圖片尺寸 (width, height)
            device: GPU 裝置編號
            
        Returns:
            建議的批次大小
        """
        if not self.cuda_available:
            return 1
        
        memory_info = self.get_vram_usage(device)
        
        # 如果 VRAM 使用率過高，減少批次大小
        if memory_info.vram_usage_percent > 80:
            optimal_size = max(1, base_batch_size // 2)
            logger.info(f"VRAM 使用率高 ({memory_info.vram_usage_percent:.1f}%)，批次大小: {base_batch_size} -> {optimal_size}")
            return optimal_size
        
        # 根據圖片大小調整
        width, height = image_size
        pixels = width * height
        
        # 大圖片使用較小批次
        if pixels > 1024 * 1024:  # > 1MP
            optimal_size = max(1, base_batch_size // 2)
        elif pixels > 2048 * 2048:  # > 4MP
            optimal_size = 1
        else:
            optimal_size = base_batch_size
        
        logger.debug(f"圖片尺寸 {image_size}，建議批次大小: {optimal_size}")
        return optimal_size
    
    def auto_manage_memory(self, device: int = 0) -> Dict:
        """
        自動記憶體管理
        
        Args:
            device: GPU 裝置編號
            
        Returns:
            管理結果字典
        """
        if not self.cuda_available:
            return {'action': 'skip', 'reason': 'CUDA not available'}
        
        memory_info = self.get_vram_usage(device)
        
        # 如果使用率過高，自動清理
        if self.is_vram_critical(device):
            logger.info("VRAM 使用率過高，執行自動清理")
            self.clear_cache(device)
            
            # 重新檢查
            new_memory_info = self.get_vram_usage(device)
            
            return {
                'action': 'cleared',
                'before_usage_percent': memory_info.vram_usage_percent,
                'after_usage_percent': new_memory_info.vram_usage_percent,
                'freed_gb': memory_info.vram_used_gb - new_memory_info.vram_used_gb
            }
        
        return {
            'action': 'none',
            'usage_percent': memory_info.vram_usage_percent,
            'reason': 'VRAM usage within normal range'
        }
    
    def get_memory_report(self, device: int = 0) -> Dict:
        """
        取得詳細記憶體報告
        
        Args:
            device: GPU 裝置編號
            
        Returns:
            記憶體報告字典
        """
        memory_info = self.get_vram_usage(device)
        
        report = {
            'cuda_available': self.cuda_available,
            'device_name': memory_info.device_name,
            'vram': {
                'used_gb': memory_info.vram_used_gb,
                'total_gb': memory_info.vram_total_gb,
                'free_gb': memory_info.vram_free_gb,
                'usage_percent': memory_info.vram_usage_percent
            },
            'threshold': {
                'warning_percent': self.vram_threshold * 100,
                'is_critical': self.is_vram_critical(device)
            }
        }
        
        if self.cuda_available:
            try:
                # 取得更詳細的 CUDA 資訊
                report['cuda_info'] = {
                    'device_count': self.device_count,
                    'current_device': torch.cuda.current_device(),
                    'memory_reserved': torch.cuda.memory_reserved(device) / 1024**3
                }
            except:
                pass
        
        return report


# 全域記憶體管理器實例
_global_memory_manager = None


def get_memory_manager(vram_threshold: float = 0.9) -> MemoryManager:
    """
    取得全域記憶體管理器實例
    
    Args:
        vram_threshold: VRAM 警戒值
        
    Returns:
        MemoryManager 實例
    """
    global _global_memory_manager
    if _global_memory_manager is None:
        _global_memory_manager = MemoryManager(vram_threshold)
    return _global_memory_manager
