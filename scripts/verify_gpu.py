#!/usr/bin/env python3
"""驗證 GPU 和 PyTorch CUDA 支援"""

import torch

print("=" * 60)
print("PyTorch GPU 驗證")
print("=" * 60)
print(f"PyTorch 版本: {torch.__version__}")
print(f"CUDA 可用: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA 版本: {torch.version.cuda}")
    print(f"GPU 數量: {torch.cuda.device_count()}")
    print(f"GPU 名稱: {torch.cuda.get_device_name(0)}")
    print(f"GPU 記憶體: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    print("=" * 60)
    print("✓ GPU 驗證成功！")
else:
    print("=" * 60)
    print("✗ CUDA 不可用")
print("=" * 60)
