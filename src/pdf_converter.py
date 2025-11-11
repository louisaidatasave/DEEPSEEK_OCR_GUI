"""
PDF 轉換模組
將 PDF 文件轉換為圖片以進行 OCR 處理
"""

from pdf2image import convert_from_path
from PIL import Image
from pathlib import Path
from typing import List, Union, Optional, Tuple
import logging
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)


def get_poppler_path() -> Optional[str]:
    """取得 Poppler 路徑（優先使用本地安裝）"""
    # 檢查專案本地 Poppler
    local_poppler = Path(__file__).parent.parent / "tools" / "poppler" / "Library" / "bin"
    if local_poppler.exists():
        return str(local_poppler.absolute())
    
    # 檢查環境變數中的 Poppler
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    for path_dir in path_dirs:
        pdftoppm = Path(path_dir) / "pdftoppm.exe"
        if pdftoppm.exists():
            return path_dir
    
    return None


@dataclass
class PDFConversionResult:
    """PDF 轉換結果資料類別"""
    success: bool
    pdf_path: str
    total_pages: int
    converted_pages: int
    image_paths: List[str]
    output_dir: str
    error_message: Optional[str] = None


class PDFConverter:
    """PDF 轉換器類別"""
    
    def __init__(
        self,
        dpi: int = 200,
        output_format: str = 'PNG',
        max_pages: Optional[int] = None
    ):
        """
        初始化 PDF 轉換器
        
        Args:
            dpi: 輸出圖片的 DPI（解析度）
            output_format: 輸出格式 (PNG, JPEG)
            max_pages: 最大處理頁數，None 表示無限制
        """
        self.dpi = dpi
        self.output_format = output_format.upper()
        self.max_pages = max_pages
        self.poppler_path = get_poppler_path()
        
        logger.info(f"PDFConverter 初始化")
        logger.info(f"  DPI: {dpi}")
        logger.info(f"  格式: {output_format}")
        logger.info(f"  最大頁數: {max_pages or '無限制'}")
        logger.info(f"  Poppler 路徑: {self.poppler_path or '系統 PATH'}")
    
    def convert_pdf(
        self,
        pdf_path: Union[str, Path],
        output_dir: Union[str, Path],
        page_range: Optional[Tuple[int, int]] = None,
        prefix: str = "page"
    ) -> PDFConversionResult:
        """
        轉換 PDF 為圖片
        
        Args:
            pdf_path: PDF 檔案路徑
            output_dir: 輸出目錄
            page_range: 頁碼範圍 (start, end)，None 表示全部
            prefix: 輸出檔案前綴
            
        Returns:
            PDFConversionResult 物件
        """
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)
        
        # 檢查 PDF 檔案
        if not pdf_path.exists():
            return PDFConversionResult(
                success=False,
                pdf_path=str(pdf_path),
                total_pages=0,
                converted_pages=0,
                image_paths=[],
                output_dir=str(output_dir),
                error_message=f"PDF 檔案不存在: {pdf_path}"
            )
        
        # 建立輸出目錄
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            logger.info(f"開始轉換 PDF: {pdf_path.name}")
            
            # 設定轉換參數
            convert_kwargs = {
                'dpi': self.dpi,
                'fmt': self.output_format.lower()
            }
            
            # 加入 Poppler 路徑
            if self.poppler_path:
                convert_kwargs['poppler_path'] = self.poppler_path
            
            # 設定頁碼範圍
            if page_range:
                start_page, end_page = page_range
                convert_kwargs['first_page'] = start_page
                convert_kwargs['last_page'] = end_page
                logger.info(f"  頁碼範圍: {start_page}-{end_page}")
            
            # 轉換 PDF
            images = convert_from_path(str(pdf_path), **convert_kwargs)
            
            total_pages = len(images)
            logger.info(f"  總頁數: {total_pages}")
            
            # 檢查最大頁數限制
            if self.max_pages and total_pages > self.max_pages:
                logger.warning(f"頁數 {total_pages} 超過限制 {self.max_pages}，僅處理前 {self.max_pages} 頁")
                images = images[:self.max_pages]
            
            # 儲存圖片
            image_paths = []
            for i, image in enumerate(images, 1):
                # 生成檔案名稱
                if page_range:
                    page_num = page_range[0] + i - 1
                else:
                    page_num = i
                
                filename = f"{prefix}_{page_num:04d}.{self.output_format.lower()}"
                image_path = output_dir / filename
                
                # 儲存圖片
                image.save(image_path, self.output_format)
                image_paths.append(str(image_path))
                
                logger.debug(f"  已儲存: {filename}")
            
            converted_pages = len(image_paths)
            logger.info(f"✓ PDF 轉換完成: {converted_pages} 頁")
            
            return PDFConversionResult(
                success=True,
                pdf_path=str(pdf_path),
                total_pages=total_pages,
                converted_pages=converted_pages,
                image_paths=image_paths,
                output_dir=str(output_dir)
            )
        
        except Exception as e:
            logger.error(f"PDF 轉換失敗: {e}")
            return PDFConversionResult(
                success=False,
                pdf_path=str(pdf_path),
                total_pages=0,
                converted_pages=0,
                image_paths=[],
                output_dir=str(output_dir),
                error_message=str(e)
            )
    
    def get_pdf_info(self, pdf_path: Union[str, Path]) -> dict:
        """
        取得 PDF 基本資訊
        
        Args:
            pdf_path: PDF 檔案路徑
            
        Returns:
            PDF 資訊字典
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            return {
                'exists': False,
                'error': f'檔案不存在: {pdf_path}'
            }
        
        try:
            # 準備轉換參數
            convert_kwargs = {}
            poppler_path = get_poppler_path()
            if poppler_path:
                convert_kwargs['poppler_path'] = poppler_path
            
            # 嘗試轉換第一頁來取得資訊
            images = convert_from_path(
                str(pdf_path),
                dpi=72,  # 低解析度，僅用於取得資訊
                first_page=1,
                last_page=1,
                **convert_kwargs
            )
            
            if images:
                first_page = images[0]
                
                # 嘗試取得總頁數（轉換所有頁面的低解析度版本）
                all_images = convert_from_path(str(pdf_path), dpi=72, **convert_kwargs)
                total_pages = len(all_images)
                
                return {
                    'exists': True,
                    'file_path': str(pdf_path),
                    'file_name': pdf_path.name,
                    'file_size_mb': pdf_path.stat().st_size / (1024 * 1024),
                    'total_pages': total_pages,
                    'first_page_size': first_page.size,
                    'estimated_conversion_time': total_pages * 2  # 估計每頁 2 秒
                }
            else:
                return {
                    'exists': True,
                    'error': 'PDF 無法讀取或為空白文件'
                }
        
        except Exception as e:
            return {
                'exists': True,
                'error': f'讀取 PDF 失敗: {str(e)}'
            }
    
    def convert_pages_range(
        self,
        pdf_path: Union[str, Path],
        output_dir: Union[str, Path],
        start_page: int,
        end_page: int,
        **kwargs
    ) -> PDFConversionResult:
        """
        轉換指定頁碼範圍
        
        Args:
            pdf_path: PDF 檔案路徑
            output_dir: 輸出目錄
            start_page: 起始頁碼（從 1 開始）
            end_page: 結束頁碼
            **kwargs: 其他參數
            
        Returns:
            PDFConversionResult 物件
        """
        return self.convert_pdf(
            pdf_path,
            output_dir,
            page_range=(start_page, end_page),
            **kwargs
        )
    
    def convert_single_page(
        self,
        pdf_path: Union[str, Path],
        output_dir: Union[str, Path],
        page_number: int,
        **kwargs
    ) -> PDFConversionResult:
        """
        轉換單一頁面
        
        Args:
            pdf_path: PDF 檔案路徑
            output_dir: 輸出目錄
            page_number: 頁碼（從 1 開始）
            **kwargs: 其他參數
            
        Returns:
            PDFConversionResult 物件
        """
        return self.convert_pdf(
            pdf_path,
            output_dir,
            page_range=(page_number, page_number),
            **kwargs
        )


# 便利函數
def convert_pdf_to_images(
    pdf_path: Union[str, Path],
    output_dir: Union[str, Path],
    dpi: int = 200,
    max_pages: Optional[int] = None,
    **kwargs
) -> PDFConversionResult:
    """
    快速轉換 PDF 的便利函數
    
    Args:
        pdf_path: PDF 檔案路徑
        output_dir: 輸出目錄
        dpi: 解析度
        max_pages: 最大頁數
        **kwargs: 其他參數
        
    Returns:
        PDFConversionResult 物件
    """
    converter = PDFConverter(dpi=dpi, max_pages=max_pages)
    return converter.convert_pdf(pdf_path, output_dir, **kwargs)


def get_pdf_info(pdf_path: Union[str, Path]) -> dict:
    """
    快速取得 PDF 資訊的便利函數
    
    Args:
        pdf_path: PDF 檔案路徑
        
    Returns:
        PDF 資訊字典
    """
    converter = PDFConverter()
    return converter.get_pdf_info(pdf_path)
