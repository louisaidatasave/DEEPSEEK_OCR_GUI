#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
效能監控腳本
即時顯示 GPU 使用率、VRAM、處理速度
"""

import sys
import os
import time
import argparse
from pathlib import Path

if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, '.')

import torch
import psutil
from datetime import datetime


def clear_screen():
    """清除螢幕"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_system_info():
    """取得系統資訊"""
    info = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'cpu_percent': psutil.cpu_percent(interval=0.1),
        'cpu_count': psutil.cpu_count(),
        'ram': psutil.virtual_memory(),
        'cuda_available': torch.cuda.is_available()
    }
    
    if info['cuda_available']:
        info['gpu_name'] = torch.cuda.get_device_name(0)
        info['vram_used'] = torch.cuda.memory_allocated(0) / 1024**3
        info['vram_total'] = torch.cuda.get_device_properties(0).total_memory / 1024**3
        info['vram_reserved'] = torch.cuda.memory_reserved(0) / 1024**3
        info['vram_percent'] = (info['vram_used'] / info['vram_total']) * 100
    
    return info


def format_bytes(bytes_value):
    """格式化位元組"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def get_progress_bar(percent, width=30):
    """取得進度條"""
    filled = int(width * percent / 100)
    bar = '█' * filled + '░' * (width - filled)
    return bar


def display_monitor(info, compact=False):
    """顯示監控資訊"""
    if not compact:
        clear_screen()
    
    print("=" * 70)
    print(f"  DeepSeek-OCR 效能監控 - {info['timestamp']}")
    print("=" * 70)
    print()
    
    # CPU 資訊
    print("【CPU】")
    cpu_bar = get_progress_bar(info['cpu_percent'])
    print(f"  使用率: {cpu_bar} {info['cpu_percent']:.1f}%")
    print(f"  核心數: {info['cpu_count']}")
    print()
    
    # RAM 資訊
    print("【RAM】")
    ram = info['ram']
    ram_percent = ram.percent
    ram_bar = get_progress_bar(ram_percent)
    print(f"  使用率: {ram_bar} {ram_percent:.1f}%")
    print(f"  已使用: {format_bytes(ram.used)} / {format_bytes(ram.total)}")
    print(f"  可用:   {format_bytes(ram.available)}")
    print()
    
    # GPU 資訊
    if info['cuda_available']:
        print("【GPU】")
        print(f"  裝置:   {info['gpu_name']}")
        vram_bar = get_progress_bar(info['vram_percent'])
        print(f"  VRAM:   {vram_bar} {info['vram_percent']:.1f}%")
        print(f"  已使用: {info['vram_used']:.2f} GB / {info['vram_total']:.2f} GB")
        print(f"  已保留: {info['vram_reserved']:.2f} GB")
    else:
        print("【GPU】")
        print("  ✗ CUDA 不可用")
    
    print()
    print("=" * 70)
    
    if not compact:
        print("按 Ctrl+C 停止監控")


def monitor_loop(interval=1.0, compact=False, export_file=None):
    """監控循環"""
    history = []
    
    try:
        while True:
            info = get_system_info()
            display_monitor(info, compact)
            
            if export_file:
                history.append(info)
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\n監控已停止")
        
        if export_file and history:
            export_report(history, export_file)


def export_report(history, output_file):
    """匯出效能報告"""
    import json
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 計算統計資料
    cpu_values = [h['cpu_percent'] for h in history]
    ram_values = [h['ram'].percent for h in history]
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'duration_seconds': len(history),
        'samples': len(history),
        'cpu': {
            'avg': sum(cpu_values) / len(cpu_values),
            'max': max(cpu_values),
            'min': min(cpu_values)
        },
        'ram': {
            'avg': sum(ram_values) / len(ram_values),
            'max': max(ram_values),
            'min': min(ram_values)
        }
    }
    
    if history[0]['cuda_available']:
        vram_values = [h['vram_percent'] for h in history]
        report['gpu'] = {
            'name': history[0]['gpu_name'],
            'vram_avg': sum(vram_values) / len(vram_values),
            'vram_max': max(vram_values),
            'vram_min': min(vram_values)
        }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n效能報告已匯出至: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='DeepSeek-OCR 效能監控工具')
    parser.add_argument('--interval', type=float, default=1.0, help='更新間隔（秒）')
    parser.add_argument('--compact', action='store_true', help='緊湊模式（不清除螢幕）')
    parser.add_argument('--export', help='匯出報告檔案路徑')
    
    args = parser.parse_args()
    
    print("啟動效能監控...")
    print(f"更新間隔: {args.interval} 秒")
    if args.export:
        print(f"將匯出報告至: {args.export}")
    print()
    
    time.sleep(1)
    
    monitor_loop(
        interval=args.interval,
        compact=args.compact,
        export_file=args.export
    )


if __name__ == '__main__':
    main()
