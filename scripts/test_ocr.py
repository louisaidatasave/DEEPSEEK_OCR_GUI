#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek-OCR 測試腳本
測試單張圖片 OCR 功能，記錄處理時間和 VRAM 使用
"""

import sys
import os
import argparse
import json
from pathlib import Path

# 設定 Windows 終端機編碼
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, '.')

from src.ocr_engine import OCREngine
import torch


def main():
    parser = argparse.ArgumentParser(description='DeepSeek-OCR 測試工具')
    parser.add_argument('image', help='圖片檔案路徑')
    parser.add_argument('--model', default='./models/deepseek-ocr', help='模型路徑')
    parser.add_argument('--output', default='outputs/test_results', help='輸出目錄')
    parser.add_argument('--base-size', type=int, default=1024, help='基礎尺寸')
    parser.add_argument('--image-size', type=int, default=1024, help='圖片尺寸')
    parser.add_argument('--crop', action='store_true', help='啟用裁切模式')
    parser.add_argument('--save', action='store_true', help='儲存結果檔案')
    parser.add_argument('--json', action='store_true', help='以 JSON 格式輸出')
    
    args = parser.parse_args()
    
    # 檢查圖片檔案
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"錯誤: 圖片檔案不存在: {image_path}")
        sys.exit(1)
    
    if not args.json:
        print("=" * 60)
        print("DeepSeek-OCR 測試")
        print("=" * 60)
        print()
        print(f"圖片: {image_path.name}")
        print(f"模型: {args.model}")
        print(f"模式: Base {args.base_size}x{args.image_size}" + (" (裁切)" if args.crop else ""))
        print()
    
    # 建立 OCR 引擎
    if not args.json:
        print("載入模型...")
    
    engine = OCREngine(model_path=args.model)
    engine.load_model()
    
    if not args.json:
        model_info = engine.get_model_info()
        print(f"✓ 模型載入成功")
        print(f"  參數量: {model_info['parameters']:.2f}B")
        if 'vram_used_gb' in model_info:
            print(f"  VRAM: {model_info['vram_used_gb']:.2f} GB / {model_info['vram_total_gb']:.2f} GB")
        print()
        print("執行 OCR...")
    
    # 執行 OCR
    result = engine.process_image(
        image_path,
        base_size=args.base_size,
        image_size=args.image_size,
        crop_mode=args.crop,
        output_path=args.output,
        save_results=args.save
    )
    
    # 輸出結果
    if args.json:
        # JSON 格式輸出
        output_data = {
            'success': result.success,
            'file_path': result.file_path,
            'processing_time': result.processing_time,
            'image_size': result.image_size,
            'vram_used_gb': result.vram_used_gb,
            'timestamp': result.timestamp.isoformat(),
            'model_config': result.model_config
        }
        
        if result.success:
            # 讀取輸出檔案
            result_file = Path(args.output) / 'result.mmd'
            if result_file.exists():
                with open(result_file, 'r', encoding='utf-8') as f:
                    output_data['text_content'] = f.read()
        else:
            output_data['error_message'] = result.error_message
        
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
    else:
        # 人類可讀格式
        print()
        print("=" * 60)
        print("OCR 結果")
        print("=" * 60)
        print(f"狀態: {'成功' if result.success else '失敗'}")
        print(f"處理時間: {result.processing_time:.2f} 秒")
        print(f"圖片尺寸: {result.image_size[0]} x {result.image_size[1]} px")
        print(f"VRAM 使用: {result.vram_used_gb:.2f} GB")
        
        if torch.cuda.is_available():
            vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            vram_percent = (result.vram_used_gb / vram_total) * 100
            print(f"VRAM 使用率: {vram_percent:.1f}%")
        
        print()
        
        if result.success:
            # 讀取並顯示結果
            result_file = Path(args.output) / 'result.mmd'
            if result_file.exists():
                print("辨識文字:")
                print("-" * 60)
                with open(result_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(content)
                print("-" * 60)
            
            if args.save:
                print()
                print(f"結果已儲存至: {args.output}/")
                print(f"  - result.mmd (Markdown)")
                print(f"  - result_with_boxes.jpg (標註圖)")
        else:
            print(f"錯誤: {result.error_message}")
        
        print()
        print("=" * 60)
    
    sys.exit(0 if result.success else 1)


if __name__ == '__main__':
    main()
