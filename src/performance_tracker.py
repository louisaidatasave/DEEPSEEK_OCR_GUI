"""
效能追蹤模組
記錄推理時間、VRAM 使用、GPU 使用率等效能指標
"""

import torch
import time
import psutil
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List, Dict
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """效能指標資料類別"""
    timestamp: str
    processing_time: float          # 處理時間（秒）
    image_size: tuple                # 圖片尺寸
    vram_used_gb: float              # VRAM 使用量（GB）
    vram_total_gb: float             # VRAM 總量（GB）
    vram_usage_percent: float        # VRAM 使用率（%）
    gpu_available: bool              # GPU 是否可用
    cpu_percent: float               # CPU 使用率（%）
    ram_used_gb: float               # RAM 使用量（GB）
    ram_total_gb: float              # RAM 總量（GB）
    file_path: str                   # 檔案路徑
    success: bool                    # 是否成功
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        return asdict(self)
    
    def to_json(self) -> str:
        """轉換為 JSON 字串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class PerformanceTracker:
    """效能追蹤器類別"""
    
    def __init__(self):
        """初始化效能追蹤器"""
        self.metrics_history: List[PerformanceMetrics] = []
        self.start_time: Optional[float] = None
        logger.info("PerformanceTracker 初始化")
    
    def start_tracking(self):
        """開始追蹤"""
        self.start_time = time.time()
        logger.debug("開始效能追蹤")
    
    def stop_tracking(
        self,
        image_size: tuple,
        file_path: str,
        success: bool = True
    ) -> PerformanceMetrics:
        """
        停止追蹤並記錄指標
        
        Args:
            image_size: 圖片尺寸
            file_path: 檔案路徑
            success: 是否成功
            
        Returns:
            PerformanceMetrics 物件
        """
        if self.start_time is None:
            raise RuntimeError("必須先呼叫 start_tracking()")
        
        processing_time = time.time() - self.start_time
        
        # 取得 GPU 資訊
        gpu_available = torch.cuda.is_available()
        vram_used_gb = 0.0
        vram_total_gb = 0.0
        vram_usage_percent = 0.0
        
        if gpu_available:
            vram_used_gb = torch.cuda.memory_allocated(0) / 1024**3
            vram_total_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
            vram_usage_percent = (vram_used_gb / vram_total_gb) * 100
        
        # 取得 CPU 和 RAM 資訊
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram_info = psutil.virtual_memory()
        ram_used_gb = ram_info.used / 1024**3
        ram_total_gb = ram_info.total / 1024**3
        
        # 建立指標物件
        metrics = PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time,
            image_size=image_size,
            vram_used_gb=vram_used_gb,
            vram_total_gb=vram_total_gb,
            vram_usage_percent=vram_usage_percent,
            gpu_available=gpu_available,
            cpu_percent=cpu_percent,
            ram_used_gb=ram_used_gb,
            ram_total_gb=ram_total_gb,
            file_path=file_path,
            success=success
        )
        
        # 加入歷史記錄
        self.metrics_history.append(metrics)
        
        # 重置開始時間
        self.start_time = None
        
        logger.info(f"效能追蹤完成: {processing_time:.2f}秒, VRAM: {vram_used_gb:.2f}GB")
        return metrics
    
    def get_summary(self) -> Dict:
        """
        取得效能摘要統計
        
        Returns:
            摘要統計字典
        """
        if not self.metrics_history:
            return {
                'total_processed': 0,
                'message': '尚無處理記錄'
            }
        
        successful = [m for m in self.metrics_history if m.success]
        
        if not successful:
            return {
                'total_processed': len(self.metrics_history),
                'successful': 0,
                'failed': len(self.metrics_history)
            }
        
        processing_times = [m.processing_time for m in successful]
        vram_usages = [m.vram_used_gb for m in successful if m.gpu_available]
        
        summary = {
            'total_processed': len(self.metrics_history),
            'successful': len(successful),
            'failed': len(self.metrics_history) - len(successful),
            'processing_time': {
                'min': min(processing_times),
                'max': max(processing_times),
                'avg': sum(processing_times) / len(processing_times),
                'total': sum(processing_times)
            }
        }
        
        if vram_usages:
            summary['vram_usage_gb'] = {
                'min': min(vram_usages),
                'max': max(vram_usages),
                'avg': sum(vram_usages) / len(vram_usages)
            }
        
        return summary
    
    def export_report(self, output_path: str = "outputs/performance_report.json"):
        """
        匯出效能報告
        
        Args:
            output_path: 輸出檔案路徑
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_summary(),
            'metrics': [m.to_dict() for m in self.metrics_history]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"效能報告已匯出至: {output_file}")
        return output_file
    
    def clear_history(self):
        """清除歷史記錄"""
        self.metrics_history.clear()
        logger.info("效能追蹤歷史已清除")


# 全域追蹤器實例
_global_tracker = PerformanceTracker()


def get_tracker() -> PerformanceTracker:
    """取得全域追蹤器實例"""
    return _global_tracker


def track_performance(func):
    """
    效能追蹤裝飾器
    
    使用範例:
        @track_performance
        def process_image(image_path):
            # ... 處理邏輯
            return result
    """
    def wrapper(*args, **kwargs):
        tracker = get_tracker()
        tracker.start_tracking()
        
        try:
            result = func(*args, **kwargs)
            # 假設第一個參數是 image_path
            image_path = args[0] if args else "unknown"
            tracker.stop_tracking(
                image_size=(0, 0),
                file_path=str(image_path),
                success=True
            )
            return result
        except Exception as e:
            image_path = args[0] if args else "unknown"
            tracker.stop_tracking(
                image_size=(0, 0),
                file_path=str(image_path),
                success=False
            )
            raise
    
    return wrapper
