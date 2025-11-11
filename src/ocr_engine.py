"""
OCR 推理引擎模組
提供 DeepSeek-OCR 模型的推理功能
"""

import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
from pathlib import Path
from typing import Union, Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime
import time
import logging

from .image_processor import ImageProcessor
from .memory_manager import get_memory_manager

# 設定日誌
logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """OCR 辨識結果資料類別"""
    text_content: str                      # 辨識文字（Markdown 格式）
    file_path: str                         # 原始檔案路徑
    processing_time: float                 # 處理時間（秒）
    image_size: tuple                      # 圖片尺寸
    vram_used_gb: float                    # VRAM 使用量（GB）
    timestamp: datetime                    # 處理時間戳
    model_config: Dict                     # 模型配置
    success: bool = True                   # 是否成功
    error_message: Optional[str] = None    # 錯誤訊息


class OCREngine:
    """OCR 推理引擎類別"""
    
    def __init__(
        self,
        model_path: str = "./models/deepseek-ocr",
        device: str = "cuda",
        torch_dtype = torch.bfloat16,
        max_image_size: Optional[int] = None
    ):
        """
        初始化 OCR 引擎
        
        Args:
            model_path: 模型路徑
            device: 運算裝置 (cuda/cpu)
            torch_dtype: PyTorch 資料類型
            max_image_size: 最大圖片尺寸
        """
        self.model_path = model_path
        self.device = device
        self.torch_dtype = torch_dtype
        self.max_image_size = max_image_size
        
        # 初始化圖片處理器
        self.image_processor = ImageProcessor(max_size=max_image_size)
        
        # 模型和 tokenizer（延遲載入）
        self.model = None
        self.tokenizer = None
        self._model_loaded = False
        
        logger.info(f"OCREngine 初始化完成")
        logger.info(f"  模型路徑: {model_path}")
        logger.info(f"  裝置: {device}")
        logger.info(f"  資料類型: {torch_dtype}")
    
    def load_model(self):
        """載入模型和 tokenizer"""
        if self._model_loaded:
            logger.debug("模型已載入，跳過")
            return
        
        logger.info("開始載入模型...")
        
        try:
            # 載入 tokenizer
            logger.debug("載入 tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            
            # 載入模型
            logger.debug("載入模型...")
            self.model = AutoModel.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                torch_dtype=self.torch_dtype,
                device_map="auto"  # 使用 auto 自動選擇 GPU
            )
            self.model = self.model.eval()
            
            # 確認模型在 GPU 上
            if torch.cuda.is_available() and self.device == "cuda":
                logger.info(f"  模型裝置: GPU (CUDA)")
            else:
                logger.warning(f"  模型裝置: {self.device}")
            
            self._model_loaded = True
            logger.info("✓ 模型載入成功")
            
            # 記錄 VRAM 使用並驗證 GPU
            if torch.cuda.is_available():
                vram_used = torch.cuda.memory_allocated(0) / 1024**3
                logger.info(f"  VRAM 使用: {vram_used:.2f} GB")
                
                # 驗證模型確實在 GPU 上
                if vram_used > 0.1:  # 如果 VRAM > 0.1 GB，表示模型在 GPU
                    logger.info("  ✓ 確認：模型已載入到 GPU")
                else:
                    logger.warning("  ⚠ 警告：VRAM 使用量過低，模型可能在 CPU")
            else:
                logger.warning("  ⚠ CUDA 不可用，使用 CPU 模式")
            
        except Exception as e:
            logger.error(f"模型載入失敗: {e}")
            raise
    
    def process_image(
        self,
        image_path: Union[str, Path],
        prompt: str = "<image>\n<|grounding|>Convert the document to markdown. ",
        base_size: int = 1024,
        image_size: int = 1024,
        crop_mode: bool = False,
        output_path: Optional[str] = None,
        save_results: bool = False
    ) -> OCRResult:
        """
        處理單張圖片進行 OCR
        
        Args:
            image_path: 圖片檔案路徑
            prompt: 提示詞
            base_size: 基礎尺寸
            image_size: 圖片尺寸
            crop_mode: 是否使用裁切模式
            output_path: 輸出路徑
            save_results: 是否儲存結果
            
        Returns:
            OCRResult 物件
        """
        # 確保模型已載入
        if not self._model_loaded:
            self.load_model()
        
        image_path = Path(image_path)
        start_time = time.time()
        
        try:
            logger.info(f"開始處理圖片: {image_path.name}")
            
            # 載入圖片資訊
            image_info = self.image_processor.get_image_info(image_path)
            logger.debug(f"  圖片尺寸: {image_info['size']}")
            
            # 執行 OCR（使用模型的 infer 方法）
            logger.debug("  執行 OCR 推理...")
            output_dir = output_path or "outputs/temp"
            result_text = self.model.infer(
                self.tokenizer,
                prompt=prompt,
                image_file=str(image_path),
                output_path=output_dir,
                base_size=base_size,
                image_size=image_size,
                crop_mode=crop_mode,
                save_results=save_results,
                test_compress=False  # 不顯示壓縮資訊
            )
            
            # 如果 infer 沒有返回文字，從檔案讀取
            if not result_text or (isinstance(result_text, str) and result_text.strip() == ""):
                result_file = Path(output_dir) / "result.mmd"
                if result_file.exists():
                    logger.debug(f"  從檔案讀取結果: {result_file}")
                    with open(result_file, 'r', encoding='utf-8') as f:
                        result_text = f.read()
                    logger.debug(f"  讀取到 {len(result_text)} 字元")
                else:
                    logger.warning(f"  未找到結果檔案: {result_file}")
                    result_text = ""
            
            # 計算處理時間
            processing_time = time.time() - start_time
            
            # 取得 VRAM 使用
            vram_used = 0.0
            if torch.cuda.is_available():
                vram_used = torch.cuda.memory_allocated(0) / 1024**3
            
            # 建立結果物件
            result = OCRResult(
                text_content=result_text or "",
                file_path=str(image_path),
                processing_time=processing_time,
                image_size=image_info['size'],
                vram_used_gb=vram_used,
                timestamp=datetime.now(),
                model_config={
                    'base_size': base_size,
                    'image_size': image_size,
                    'crop_mode': crop_mode,
                    'prompt': prompt
                },
                success=True
            )
            
            logger.info(f"✓ OCR 完成，處理時間: {processing_time:.2f} 秒")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"OCR 處理失敗: {e}")
            
            # 返回錯誤結果
            return OCRResult(
                text_content="",
                file_path=str(image_path),
                processing_time=processing_time,
                image_size=(0, 0),
                vram_used_gb=0.0,
                timestamp=datetime.now(),
                model_config={},
                success=False,
                error_message=str(e)
            )
    
    def get_model_info(self) -> Dict:
        """
        取得模型資訊
        
        Returns:
            模型資訊字典
        """
        if not self._model_loaded:
            return {
                'loaded': False,
                'model_path': self.model_path
            }
        
        info = {
            'loaded': True,
            'model_path': self.model_path,
            'device': self.device,
            'torch_dtype': str(self.torch_dtype),
            'parameters': sum(p.numel() for p in self.model.parameters()) / 1e9
        }
        
        if torch.cuda.is_available():
            info['vram_used_gb'] = torch.cuda.memory_allocated(0) / 1024**3
            info['vram_total_gb'] = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        return info
    
    def batch_process(
        self,
        image_paths: List[Union[str, Path]],
        base_batch_size: int = 4,
        **kwargs
    ) -> List[OCRResult]:
        """
        批次處理多張圖片
        
        Args:
            image_paths: 圖片檔案路徑列表
            base_batch_size: 基礎批次大小
            **kwargs: 其他參數傳遞給 process_image
            
        Returns:
            OCRResult 列表
        """
        # 確保模型已載入
        if not self._model_loaded:
            self.load_model()
        
        memory_manager = get_memory_manager()
        results = []
        
        logger.info(f"開始批次處理 {len(image_paths)} 張圖片")
        
        for i, image_path in enumerate(image_paths):
            logger.info(f"處理進度: {i+1}/{len(image_paths)} - {Path(image_path).name}")
            
            try:
                # 檢查記憶體狀況
                if memory_manager.is_vram_critical():
                    logger.warning("VRAM 使用率過高，執行清理")
                    memory_manager.clear_cache()
                
                # 處理單張圖片
                result = self.process_image(image_path, **kwargs)
                results.append(result)
                
                # 記錄進度
                if (i + 1) % 10 == 0:
                    vram_info = memory_manager.get_vram_usage()
                    logger.info(f"已處理 {i+1} 張，VRAM 使用: {vram_info.vram_used_gb:.2f} GB ({vram_info.vram_usage_percent:.1f}%)")
            
            except Exception as e:
                logger.error(f"處理 {image_path} 失敗: {e}")
                # 建立錯誤結果
                error_result = OCRResult(
                    text_content="",
                    file_path=str(image_path),
                    processing_time=0.0,
                    image_size=(0, 0),
                    vram_used_gb=0.0,
                    timestamp=datetime.now(),
                    model_config={},
                    success=False,
                    error_message=str(e)
                )
                results.append(error_result)
        
        # 統計結果
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_time = sum(r.processing_time for r in results)
        
        logger.info(f"批次處理完成: 成功 {successful}, 失敗 {failed}, 總時間 {total_time:.2f} 秒")
        
        return results
    
    def process_with_fallback(
        self,
        image_path: Union[str, Path],
        **kwargs
    ) -> OCRResult:
        """
        帶 CPU fallback 的圖片處理
        
        Args:
            image_path: 圖片檔案路徑
            **kwargs: 其他參數
            
        Returns:
            OCRResult 物件
        """
        memory_manager = get_memory_manager()
        
        try:
            # 檢查 VRAM 是否足夠
            if memory_manager.is_vram_critical():
                logger.warning("VRAM 使用率過高，嘗試清理快取")
                memory_manager.clear_cache()
            
            # 嘗試 GPU 處理
            return self.process_image(image_path, **kwargs)
        
        except torch.cuda.OutOfMemoryError:
            logger.warning("GPU 記憶體不足，切換到 CPU 模式")
            
            # 清理 GPU 快取
            memory_manager.clear_cache()
            
            # 暫時切換到 CPU
            original_device = self.device
            try:
                # 重新載入模型到 CPU
                self.unload_model()
                self.device = "cpu"
                self.load_model()
                
                # 在 CPU 上處理
                result = self.process_image(image_path, **kwargs)
                
                # 恢復 GPU 模式
                self.unload_model()
                self.device = original_device
                self.load_model()
                
                return result
            
            except Exception as e:
                logger.error(f"CPU fallback 也失敗: {e}")
                return OCRResult(
                    text_content="",
                    file_path=str(image_path),
                    processing_time=0.0,
                    image_size=(0, 0),
                    vram_used_gb=0.0,
                    timestamp=datetime.now(),
                    model_config={},
                    success=False,
                    error_message=f"GPU 和 CPU 處理都失敗: {str(e)}"
                )
    
    def unload_model(self):
        """卸載模型以釋放記憶體"""
        if self._model_loaded:
            logger.info("卸載模型...")
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            self._model_loaded = False
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("✓ 模型已卸載")


# 便利函數
def process_image(
    image_path: Union[str, Path],
    model_path: str = "./models/deepseek-ocr",
    **kwargs
) -> OCRResult:
    """
    快速處理圖片的便利函數
    
    Args:
        image_path: 圖片檔案路徑
        model_path: 模型路徑
        **kwargs: 其他參數傳遞給 OCREngine.process_image
        
    Returns:
        OCRResult 物件
    """
    engine = OCREngine(model_path=model_path)
    engine.load_model()
    return engine.process_image(image_path, **kwargs)
