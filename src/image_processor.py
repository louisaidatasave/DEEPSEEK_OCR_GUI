"""
圖片預處理模組
提供圖片載入、調整大小、格式轉換等功能
"""

from PIL import Image
from pathlib import Path
from typing import Union, Tuple, Optional
import logging

# 設定日誌
logger = logging.getLogger(__name__)


class ImageProcessor:
    """圖片預處理類別"""
    
    # 支援的圖片格式
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
    
    def __init__(self, max_size: Optional[int] = None):
        """
        初始化圖片處理器
        
        Args:
            max_size: 最大圖片尺寸（像素），None 表示不限制
        """
        self.max_size = max_size
        logger.info(f"ImageProcessor 初始化，最大尺寸: {max_size or '無限制'}")
    
    def load_image(self, image_path: Union[str, Path]) -> Image.Image:
        """
        載入圖片
        
        Args:
            image_path: 圖片檔案路徑
            
        Returns:
            PIL Image 物件
            
        Raises:
            FileNotFoundError: 檔案不存在
            ValueError: 不支援的圖片格式
            IOError: 圖片載入失敗
        """
        image_path = Path(image_path)
        
        # 檢查檔案是否存在
        if not image_path.exists():
            raise FileNotFoundError(f"圖片檔案不存在: {image_path}")
        
        # 檢查檔案格式
        if image_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"不支援的圖片格式: {image_path.suffix}。"
                f"支援的格式: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        try:
            # 載入圖片
            image = Image.open(image_path)
            
            # 轉換為 RGB（確保格式一致）
            if image.mode != 'RGB':
                logger.debug(f"轉換圖片模式: {image.mode} -> RGB")
                image = image.convert('RGB')
            
            logger.info(f"成功載入圖片: {image_path.name}, 尺寸: {image.size}")
            return image
            
        except Exception as e:
            raise IOError(f"圖片載入失敗: {e}")
    
    def resize_image(
        self, 
        image: Image.Image, 
        max_size: Optional[int] = None,
        maintain_aspect_ratio: bool = True
    ) -> Image.Image:
        """
        調整圖片大小
        
        Args:
            image: PIL Image 物件
            max_size: 最大尺寸，None 則使用初始化時的設定
            maintain_aspect_ratio: 是否保持長寬比
            
        Returns:
            調整後的 PIL Image 物件
        """
        max_size = max_size or self.max_size
        
        # 如果沒有設定最大尺寸，直接返回
        if max_size is None:
            return image
        
        width, height = image.size
        
        # 如果圖片已經小於最大尺寸，直接返回
        if width <= max_size and height <= max_size:
            logger.debug(f"圖片尺寸 {image.size} 已小於最大限制 {max_size}，不需調整")
            return image
        
        if maintain_aspect_ratio:
            # 保持長寬比
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
        else:
            # 不保持長寬比，直接縮放到最大尺寸
            new_width = max_size
            new_height = max_size
        
        logger.info(f"調整圖片大小: {image.size} -> ({new_width}, {new_height})")
        return image.resize((new_width, new_height), Image.LANCZOS)
    
    def process_image(
        self, 
        image_path: Union[str, Path],
        max_size: Optional[int] = None,
        maintain_aspect_ratio: bool = True
    ) -> Tuple[Image.Image, dict]:
        """
        完整的圖片預處理流程
        
        Args:
            image_path: 圖片檔案路徑
            max_size: 最大尺寸
            maintain_aspect_ratio: 是否保持長寬比
            
        Returns:
            (處理後的圖片, 處理資訊字典)
        """
        image_path = Path(image_path)
        
        # 載入圖片
        image = self.load_image(image_path)
        original_size = image.size
        
        # 調整大小
        image = self.resize_image(image, max_size, maintain_aspect_ratio)
        processed_size = image.size
        
        # 處理資訊
        info = {
            'file_path': str(image_path),
            'file_name': image_path.name,
            'original_size': original_size,
            'processed_size': processed_size,
            'format': image_path.suffix.lower(),
            'mode': image.mode,
            'resized': original_size != processed_size
        }
        
        logger.info(f"圖片預處理完成: {image_path.name}")
        return image, info
    
    @staticmethod
    def get_image_info(image_path: Union[str, Path]) -> dict:
        """
        取得圖片基本資訊（不載入完整圖片）
        
        Args:
            image_path: 圖片檔案路徑
            
        Returns:
            圖片資訊字典
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"圖片檔案不存在: {image_path}")
        
        try:
            with Image.open(image_path) as img:
                info = {
                    'file_path': str(image_path),
                    'file_name': image_path.name,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'file_size_mb': image_path.stat().st_size / (1024 * 1024)
                }
            return info
        except Exception as e:
            raise IOError(f"無法讀取圖片資訊: {e}")
    
    @staticmethod
    def validate_image(image_path: Union[str, Path]) -> bool:
        """
        驗證圖片是否有效
        
        Args:
            image_path: 圖片檔案路徑
            
        Returns:
            True 如果圖片有效，False 否則
        """
        try:
            image_path = Path(image_path)
            
            if not image_path.exists():
                return False
            
            if image_path.suffix.lower() not in ImageProcessor.SUPPORTED_FORMATS:
                return False
            
            # 嘗試開啟圖片
            with Image.open(image_path) as img:
                img.verify()
            
            return True
            
        except Exception:
            return False


# 便利函數
def load_image(image_path: Union[str, Path], max_size: Optional[int] = None) -> Image.Image:
    """
    快速載入圖片的便利函數
    
    Args:
        image_path: 圖片檔案路徑
        max_size: 最大尺寸
        
    Returns:
        PIL Image 物件
    """
    processor = ImageProcessor(max_size=max_size)
    image, _ = processor.process_image(image_path, max_size=max_size)
    return image


def get_image_info(image_path: Union[str, Path]) -> dict:
    """
    快速取得圖片資訊的便利函數
    
    Args:
        image_path: 圖片檔案路徑
        
    Returns:
        圖片資訊字典
    """
    return ImageProcessor.get_image_info(image_path)
