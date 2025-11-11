#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試效能追蹤模組"""

import sys
import os

if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, '.')

from src.performance_tracker import PerformanceTracker
import time

print("=" * 60)
print("效能追蹤模組測試")
print("=" * 60)
print()

# 建立追蹤器
tracker = PerformanceTracker()

# 模擬處理 3 張圖片
test_images = [
    ("image1.png", (800, 600), 5.2, True),
    ("image2.png", (1024, 768), 8.5, True),
    ("image3.png", (640, 480), 3.1, False),
]

print("模擬處理圖片...")
for file_path, size, duration, success in test_images:
    print(f"\n處理: {file_path}")
    
    tracker.start_tracking()
    time.sleep(0.1)  # 模擬處理
    
    metrics = tracker.stop_tracking(
        image_size=size,
        file_path=file_path,
        success=success
    )
    
    print(f"  處理時間: {metrics.processing_time:.2f} 秒")
    print(f"  VRAM: {metrics.vram_used_gb:.2f} GB ({metrics.vram_usage_percent:.1f}%)")
    print(f"  CPU: {metrics.cpu_percent:.1f}%")
    print(f"  狀態: {'成功' if metrics.success else '失敗'}")

print()
print("=" * 60)
print("效能摘要")
print("=" * 60)

summary = tracker.get_summary()
print(f"總處理數: {summary['total_processed']}")
print(f"成功: {summary['successful']}")
print(f"失敗: {summary['failed']}")
print()
print("處理時間:")
print(f"  最小: {summary['processing_time']['min']:.2f} 秒")
print(f"  最大: {summary['processing_time']['max']:.2f} 秒")
print(f"  平均: {summary['processing_time']['avg']:.2f} 秒")
print(f"  總計: {summary['processing_time']['total']:.2f} 秒")

if 'vram_usage_gb' in summary:
    print()
    print("VRAM 使用:")
    print(f"  最小: {summary['vram_usage_gb']['min']:.2f} GB")
    print(f"  最大: {summary['vram_usage_gb']['max']:.2f} GB")
    print(f"  平均: {summary['vram_usage_gb']['avg']:.2f} GB")

print()
print("=" * 60)

# 匯出報告
output_file = tracker.export_report("outputs/test_performance_report.json")
print(f"✓ 報告已匯出至: {output_file}")

print()
print("=" * 60)
print("✓ 測試完成！")
print("=" * 60)
