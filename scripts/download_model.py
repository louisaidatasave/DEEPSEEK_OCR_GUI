#!/usr/bin/env python3
"""
DeepSeek-OCR 模型下載腳本
從 Hugging Face 下載模型權重到本地目錄
"""

import argparse
import os
from pathlib import Path
from huggingface_hub import snapshot_download
from tqdm import tqdm


def download_deepseek_ocr(output_dir: str = "./models/deepseek-ocr", token: str = None):
    """
    下載 DeepSeek-OCR 模型
    
    Args:
        output_dir: 模型儲存目錄
        token: Hugging Face token（如果模型需要授權）
    """
    model_name = "deepseek-ai/deepseek-ocr"
    
    print("=" * 60)
    print("DeepSeek-OCR 模型下載")
    print("=" * 60)
    print(f"模型: {model_name}")
    print(f"目標目錄: {output_dir}")
    print()
    
    # 建立輸出目錄
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        print("開始下載模型...")
        print("注意: 模型大小約 6-7 GB，請耐心等待")
        print()
        
        # 下載模型
        downloaded_path = snapshot_download(
            repo_id=model_name,
            local_dir=output_dir,
            local_dir_use_symlinks=False,
            token=token,
            resume_download=True,
        )
        
        print()
        print("=" * 60)
        print("✓ 模型下載完成！")
        print(f"儲存位置: {Path(downloaded_path).absolute()}")
        print("=" * 60)
        
        # 列出下載的檔案
        print("\n下載的檔案:")
        for file in sorted(Path(output_dir).rglob("*")):
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"  - {file.name} ({size_mb:.2f} MB)")
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ 下載失敗: {e}")
        print("=" * 60)
        print()
        print("可能的解決方案:")
        print("1. 檢查網路連線")
        print("2. 確認 Hugging Face 可以存取")
        print("3. 如果模型需要授權，請提供 token:")
        print("   python scripts/download_model.py --token YOUR_HF_TOKEN")
        print("4. 使用鏡像站點（中國地區）:")
        print("   export HF_ENDPOINT=https://hf-mirror.com")
        print()
        return False


def main():
    parser = argparse.ArgumentParser(description="下載 DeepSeek-OCR 模型")
    parser.add_argument(
        "--output",
        "-o",
        default="./models/deepseek-ocr",
        help="模型儲存目錄 (預設: ./models/deepseek-ocr)",
    )
    parser.add_argument(
        "--token",
        "-t",
        default=None,
        help="Hugging Face token（如果需要）",
    )
    
    args = parser.parse_args()
    
    success = download_deepseek_ocr(args.output, args.token)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
