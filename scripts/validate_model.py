#!/usr/bin/env python3
"""
模型驗證腳本
檢查 DeepSeek-OCR 模型檔案完整性並嘗試載入
"""

import argparse
import json
from pathlib import Path


def validate_model_files(model_dir: str = "./models/deepseek-ocr"):
    """驗證模型檔案完整性"""
    model_path = Path(model_dir)
    
    print("=" * 60)
    print("DeepSeek-OCR 模型驗證")
    print("=" * 60)
    print(f"模型目錄: {model_path.absolute()}")
    print()
    
    # 必要檔案清單
    required_files = [
        "config.json",
        "model.safetensors.index.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "modeling_deepseekocr.py",
    ]
    
    # 檢查目錄是否存在
    if not model_path.exists():
        print(f"✗ 模型目錄不存在: {model_path}")
        return False
    
    print("【檔案完整性檢查】")
    all_files_exist = True
    
    for file_name in required_files:
        file_path = model_path / file_name
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ {file_name} ({size_mb:.2f} MB)")
        else:
            print(f"  ✗ {file_name} (缺失)")
            all_files_exist = False
    
    # 檢查模型權重檔案
    print()
    print("【模型權重檔案】")
    safetensors_files = list(model_path.glob("model-*.safetensors"))
    
    if safetensors_files:
        total_size = 0
        for file in safetensors_files:
            size_mb = file.stat().st_size / (1024 * 1024)
            total_size += size_mb
            print(f"  ✓ {file.name} ({size_mb:.2f} MB)")
        print(f"  總大小: {total_size:.2f} MB ({total_size/1024:.2f} GB)")
    else:
        print(f"  ✗ 找不到模型權重檔案")
        all_files_exist = False
    
    print()
    
    if not all_files_exist:
        print("=" * 60)
        print("✗ 模型檔案不完整")
        print("=" * 60)
        return False
    
    # 讀取 config.json
    try:
        print("【模型配置】")
        with open(model_path / "config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        print(f"  模型類型: {config.get('model_type', 'unknown')}")
        print(f"  架構: {config.get('architectures', ['unknown'])[0]}")
        if 'hidden_size' in config:
            print(f"  Hidden size: {config['hidden_size']}")
        if 'num_hidden_layers' in config:
            print(f"  Layers: {config['num_hidden_layers']}")
        
    except Exception as e:
        print(f"  ⚠ 無法讀取配置: {e}")
    
    print()
    print("=" * 60)
    print("✓ 模型檔案驗證通過")
    print("=" * 60)
    
    return True


def test_model_loading(model_dir: str = "./models/deepseek-ocr"):
    """測試模型載入"""
    print()
    print("【模型載入測試】")
    print("嘗試載入模型...")
    
    try:
        from transformers import AutoModel, AutoTokenizer
        import torch
        
        # 載入 tokenizer
        print("  載入 tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_dir,
            trust_remote_code=True
        )
        print(f"  ✓ Tokenizer 載入成功")
        print(f"    詞彙量: {len(tokenizer)}")
        
        # 載入模型（僅配置，不載入權重以節省時間）
        print("  載入模型配置...")
        from transformers import AutoConfig
        config = AutoConfig.from_pretrained(
            model_dir,
            trust_remote_code=True
        )
        print(f"  ✓ 模型配置載入成功")
        
        # 檢查 GPU
        if torch.cuda.is_available():
            print(f"  ✓ GPU 可用: {torch.cuda.get_device_name(0)}")
        else:
            print(f"  ⚠ GPU 不可用，將使用 CPU")
        
        print()
        print("=" * 60)
        print("✓ 模型載入測試通過")
        print("=" * 60)
        print()
        print("注意: 完整模型載入將在實際 OCR 測試時進行")
        
        return True
        
    except Exception as e:
        print(f"  ✗ 模型載入失敗: {e}")
        print()
        print("=" * 60)
        print("✗ 模型載入測試失敗")
        print("=" * 60)
        return False


def main():
    parser = argparse.ArgumentParser(description="驗證 DeepSeek-OCR 模型")
    parser.add_argument(
        "--model-dir",
        "-m",
        default="./models/deepseek-ocr",
        help="模型目錄 (預設: ./models/deepseek-ocr)",
    )
    parser.add_argument(
        "--skip-loading",
        action="store_true",
        help="跳過模型載入測試（僅檢查檔案）",
    )
    
    args = parser.parse_args()
    
    # 驗證檔案
    files_ok = validate_model_files(args.model_dir)
    
    if not files_ok:
        exit(1)
    
    # 測試載入
    if not args.skip_loading:
        loading_ok = test_model_loading(args.model_dir)
        if not loading_ok:
            exit(1)
    
    print("✓ 所有驗證通過！模型已準備就緒。")


if __name__ == "__main__":
    main()
