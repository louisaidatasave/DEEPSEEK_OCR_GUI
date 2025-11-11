#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次處理測試腳本
測試多張圖片和 PDF 文件的批次 OCR 處理
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import List

if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, '.')

from src import OCREngine, PDFConverter, get_memory_manager, get_tracker
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def find_image_files(directory: Path, extensions: List[str] = None) -> List[Path]:
    """尋找目錄中的圖片檔案"""
    if extensions is None:
        extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
    
    image_files = []
    for ext in extensions:
        image_files.extend(directory.glob(f"*{ext}"))
        image_files.extend(directory.glob(f"*{ext.upper()}"))
    
    return sorted(image_files)


def batch_process_images(image_paths: List[Path], output_dir: Path, engine: OCREngine) -> dict:
    """批次處理圖片"""
    print(f"\n開始批次處理 {len(image_paths)} 張圖片...")
    
    # 執行批次處理
    results = engine.batch_process(
        image_paths,
        base_batch_size=4,
        output_path=str(output_dir),
        save_results=True
    )
    
    # 統計結果
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    total_time = sum(r.processing_time for r in results)
    avg_time = total_time / len(results) if results else 0
    
    stats = {
        'total_processed': len(results),
        'successful': len(successful),
        'failed': len(failed),
        'total_time': total_time,
        'average_time': avg_time,
        'success_rate': len(successful) / len(results) * 100 if results else 0
    }
    
    print(f"\n批次處理完成:")
    print(f"  總數: {stats['total_processed']}")
    print(f"  成功: {stats['successful']}")
    print(f"  失敗: {stats['failed']}")
    print(f"  成功率: {stats['success_rate']:.1f}%")
    print(f"  總時間: {stats['total_time']:.2f} 秒")
    print(f"  平均時間: {stats['average_time']:.2f} 秒/張")
    
    if failed:
        print(f"\n失敗的檔案:")
        for result in failed:
            print(f"  - {Path(result.file_path).name}: {result.error_message}")
    
    return stats


def process_pdf_document(pdf_path: Path, output_dir: Path, engine: OCREngine, max_pages: int = 100) -> dict:
    """處理 PDF 文件"""
    print(f"\n開始處理 PDF: {pdf_path.name}")
    
    # 建立 PDF 轉換器
    pdf_converter = PDFConverter(dpi=200, max_pages=max_pages)
    
    # 取得 PDF 資訊
    pdf_info = pdf_converter.get_pdf_info(pdf_path)
    if not pdf_info.get('exists') or 'error' in pdf_info:
        return {
            'success': False,
            'error': pdf_info.get('error', 'PDF 檔案無法讀取')
        }
    
    print(f"  PDF 資訊:")
    print(f"    總頁數: {pdf_info['total_pages']}")
    print(f"    檔案大小: {pdf_info['file_size_mb']:.2f} MB")
    print(f"    預估時間: {pdf_info['estimated_conversion_time']} 秒")
    
    # 轉換 PDF 為圖片
    pdf_images_dir = output_dir / "pdf_images"
    conversion_result = pdf_converter.convert_pdf(
        pdf_path,
        pdf_images_dir,
        prefix=pdf_path.stem
    )
    
    if not conversion_result.success:
        return {
            'success': False,
            'error': conversion_result.error_message
        }
    
    print(f"  ✓ PDF 轉換完成: {conversion_result.converted_pages} 頁")
    
    # 批次處理轉換後的圖片
    image_paths = [Path(p) for p in conversion_result.image_paths]
    ocr_results = engine.batch_process(
        image_paths,
        base_batch_size=2,  # PDF 圖片通常較大，使用較小批次
        output_path=str(output_dir / "pdf_ocr"),
        save_results=True
    )
    
    # 統計結果
    successful_ocr = [r for r in ocr_results if r.success]
    total_time = sum(r.processing_time for r in ocr_results)
    
    stats = {
        'success': True,
        'pdf_info': pdf_info,
        'conversion_result': {
            'total_pages': conversion_result.total_pages,
            'converted_pages': conversion_result.converted_pages
        },
        'ocr_results': {
            'total_processed': len(ocr_results),
            'successful': len(successful_ocr),
            'failed': len(ocr_results) - len(successful_ocr),
            'total_time': total_time,
            'average_time': total_time / len(ocr_results) if ocr_results else 0
        }
    }
    
    print(f"  ✓ OCR 處理完成:")
    print(f"    成功: {len(successful_ocr)}/{len(ocr_results)} 頁")
    print(f"    總時間: {total_time:.2f} 秒")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description='批次 OCR 處理工具')
    parser.add_argument('input', help='輸入目錄或 PDF 檔案')
    parser.add_argument('--output', default='outputs/batch_results', help='輸出目錄')
    parser.add_argument('--model', default='./models/deepseek-ocr', help='模型路徑')
    parser.add_argument('--max-pages', type=int, default=100, help='PDF 最大處理頁數')
    parser.add_argument('--json', action='store_true', help='以 JSON 格式輸出結果')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_dir = Path(args.output)
    
    if not input_path.exists():
        print(f"錯誤: 輸入路徑不存在: {input_path}")
        sys.exit(1)
    
    # 建立輸出目錄
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not args.json:
        print("=" * 60)
        print("DeepSeek-OCR 批次處理")
        print("=" * 60)
        print(f"輸入: {input_path}")
        print(f"輸出: {output_dir}")
    
    # 初始化 OCR 引擎
    if not args.json:
        print("\n載入 OCR 模型...")
    
    engine = OCREngine(model_path=args.model)
    engine.load_model()
    
    # 取得記憶體管理器和效能追蹤器
    memory_manager = get_memory_manager()
    tracker = get_tracker()
    
    if not args.json:
        memory_info = memory_manager.get_vram_usage()
        if memory_info.cuda_available:
            print(f"✓ 模型載入完成")
            print(f"  GPU: {memory_info.device_name}")
            print(f"  VRAM: {memory_info.vram_used_gb:.2f} GB / {memory_info.vram_total_gb:.2f} GB")
    
    # 判斷輸入類型並處理
    results = {}
    
    if input_path.is_file() and input_path.suffix.lower() == '.pdf':
        # PDF 文件處理
        results = process_pdf_document(input_path, output_dir, engine, args.max_pages)
    
    elif input_path.is_dir():
        # 圖片目錄批次處理
        image_files = find_image_files(input_path)
        
        if not image_files:
            print(f"錯誤: 在 {input_path} 中找不到圖片檔案")
            sys.exit(1)
        
        if not args.json:
            print(f"\n找到 {len(image_files)} 張圖片")
        
        results = batch_process_images(image_files, output_dir, engine)
    
    else:
        print(f"錯誤: 不支援的輸入類型: {input_path}")
        sys.exit(1)
    
    # 輸出最終報告
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 60)
        print("處理完成")
        print("=" * 60)
        
        # 記憶體報告
        final_memory = memory_manager.get_memory_report()
        print(f"\n記憶體使用:")
        if final_memory['cuda_available']:
            print(f"  VRAM: {final_memory['vram']['used_gb']:.2f} GB / {final_memory['vram']['total_gb']:.2f} GB")
            print(f"  使用率: {final_memory['vram']['usage_percent']:.1f}%")
        
        # 效能報告
        perf_summary = tracker.get_summary()
        if perf_summary.get('total_processed', 0) > 0:
            print(f"\n效能統計:")
            print(f"  總處理數: {perf_summary['total_processed']}")
            print(f"  成功: {perf_summary['successful']}")
            print(f"  失敗: {perf_summary['failed']}")
            if 'processing_time' in perf_summary:
                print(f"  平均時間: {perf_summary['processing_time']['avg']:.2f} 秒")
        
        print(f"\n結果已儲存至: {output_dir}")
        print("=" * 60)


if __name__ == '__main__':
    main()
