#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試記憶體管理模組"""

import sys
import os

if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, '.')

from src.memory_manager import MemoryManager, get_memory_manager
import json

print("=" * 60)
print("記憶體管理模組測試")
print("=" * 60)
print()

# 建立記憶體管理器
memory_manager = MemoryManager(vram_threshold=0.8)

# 測試 1: 取得 VRAM 使用資訊
print("【測試 1】VRAM 使用資訊")
vram_info = memory_manager.get_vram_usage()
print(f"CUDA 可用: {vram_info.cuda_available}")
if vram_info.cuda_available:
    print(f"裝置: {vram_info.device_name}")
    print(f"VRAM 使用: {vram_info.vram_used_gb:.2f} GB / {vram_info.vram_total_gb:.2f} GB")
    print(f"VRAM 可用: {vram_info.vram_free_gb:.2f} GB")
    print(f"使用率: {vram_info.vram_usage_percent:.1f}%")
else:
    print("CUDA 不可用")

print()

# 測試 2: 檢查 VRAM 是否足夠
print("【測試 2】VRAM 可用性檢查")
required_amounts = [1.0, 2.0, 5.0, 10.0]
for amount in required_amounts:
    available = memory_manager.check_vram_available(amount)
    status = "✓" if available else "✗"
    print(f"  {status} 需要 {amount:.1f} GB: {'可用' if available else '不足'}")

print()

# 測試 3: 批次大小計算
print("【測試 3】最佳批次大小計算")
test_cases = [
    (4, (512, 512)),
    (8, (1024, 1024)),
    (4, (2048, 2048)),
    (2, (4096, 4096))
]

for base_size, image_size in test_cases:
    optimal = memory_manager.calculate_optimal_batch_size(base_size, image_size)
    print(f"  圖片 {image_size[0]}x{image_size[1]}: 基礎批次 {base_size} -> 建議 {optimal}")

print()

# 測試 4: 記憶體報告
print("【測試 4】詳細記憶體報告")
report = memory_manager.get_memory_report()
print(json.dumps(report, ensure_ascii=False, indent=2))

print()

# 測試 5: 自動記憶體管理
print("【測試 5】自動記憶體管理")
result = memory_manager.auto_manage_memory()
print(f"管理動作: {result['action']}")
if 'reason' in result:
    print(f"原因: {result['reason']}")
if 'freed_gb' in result:
    print(f"釋放記憶體: {result['freed_gb']:.2f} GB")

print()

# 測試 6: 全域管理器
print("【測試 6】全域記憶體管理器")
global_manager = get_memory_manager()
print(f"全域管理器類型: {type(global_manager).__name__}")
print(f"VRAM 警戒值: {global_manager.vram_threshold * 100:.1f}%")

print()
print("=" * 60)
print("✓ 測試完成！")
print("=" * 60)
