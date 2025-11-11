#!/usr/bin/env python3
"""
硬體檢查腳本
檢查 GPU、CUDA、RAM 等硬體資訊，確保符合 DeepSeek-OCR 運行需求
"""

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


class HardwareChecker:
    """硬體檢查類別"""
    
    def __init__(self):
        self.results = {
            "system": {},
            "gpu": {},
            "cuda": {},
            "memory": {},
            "status": "unknown",
            "errors": [],
            "warnings": []
        }
    
    def check_system_info(self) -> Dict:
        """檢查系統基本資訊"""
        try:
            self.results["system"] = {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "python_version": sys.version.split()[0]
            }
            print(f"✓ 系統平台: {self.results['system']['platform']}")
            print(f"✓ Python 版本: {self.results['system']['python_version']}")
        except Exception as e:
            self.results["errors"].append(f"系統資訊檢查失敗: {str(e)}")
            print(f"✗ 系統資訊檢查失敗: {e}")
        
        return self.results["system"]

    def check_gpu_nvidia_smi(self) -> Dict:
        """使用 nvidia-smi 檢查 GPU 資訊"""
        try:
            # 執行 nvidia-smi 指令
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.free", 
                 "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout.strip().split(',')
                if len(output) >= 4:
                    self.results["gpu"] = {
                        "available": True,
                        "name": output[0].strip(),
                        "driver_version": output[1].strip(),
                        "memory_total_mb": float(output[2].strip()),
                        "memory_free_mb": float(output[3].strip()),
                        "memory_total_gb": round(float(output[2].strip()) / 1024, 2),
                        "memory_free_gb": round(float(output[3].strip()) / 1024, 2)
                    }
                    
                    print(f"✓ GPU 偵測成功: {self.results['gpu']['name']}")
                    print(f"✓ 驅動版本: {self.results['gpu']['driver_version']}")
                    print(f"✓ VRAM: {self.results['gpu']['memory_total_gb']} GB " +
                          f"(可用: {self.results['gpu']['memory_free_gb']} GB)")
                    
                    # 檢查驅動版本
                    driver_version = float(self.results['gpu']['driver_version'].split('.')[0])
                    if driver_version < 535:
                        self.results["warnings"].append(
                            f"驅動版本 {self.results['gpu']['driver_version']} 低於建議版本 535"
                        )
                        print(f"⚠ 警告: 驅動版本過舊，建議升級至 535 或更新版本")
                    
                    # 檢查 VRAM
                    if self.results['gpu']['memory_total_gb'] < 8:
                        self.results["warnings"].append(
                            f"VRAM {self.results['gpu']['memory_total_gb']} GB 低於建議的 8 GB"
                        )
                        print(f"⚠ 警告: VRAM 容量較小，可能影響效能")
                    
                    return self.results["gpu"]
            
            # nvidia-smi 執行失敗
            self.results["gpu"] = {"available": False}
            self.results["errors"].append("nvidia-smi 執行失敗，無法偵測 GPU")
            print("✗ GPU 偵測失敗: nvidia-smi 無法執行")
            
        except FileNotFoundError:
            self.results["gpu"] = {"available": False}
            self.results["errors"].append("找不到 nvidia-smi，請確認 NVIDIA 驅動已安裝")
            print("✗ 找不到 nvidia-smi，請安裝 NVIDIA 驅動")
        except subprocess.TimeoutExpired:
            self.results["gpu"] = {"available": False}
            self.results["errors"].append("nvidia-smi 執行超時")
            print("✗ nvidia-smi 執行超時")
        except Exception as e:
            self.results["gpu"] = {"available": False}
            self.results["errors"].append(f"GPU 檢查失敗: {str(e)}")
            print(f"✗ GPU 檢查失敗: {e}")
        
        return self.results["gpu"]

    def check_cuda_version(self) -> Dict:
        """檢查 CUDA 版本"""
        try:
            # 嘗試使用 nvcc 檢查 CUDA 版本
            result = subprocess.run(
                ["nvcc", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout
                # 解析 CUDA 版本
                for line in output.split('\n'):
                    if 'release' in line.lower():
                        # 例如: "Cuda compilation tools, release 11.8, V11.8.89"
                        parts = line.split('release')
                        if len(parts) > 1:
                            version_str = parts[1].split(',')[0].strip()
                            self.results["cuda"] = {
                                "available": True,
                                "version": version_str,
                                "full_output": output.strip()
                            }
                            print(f"✓ CUDA 版本: {version_str}")
                            
                            # 檢查版本是否符合需求
                            try:
                                major_version = float(version_str.split('.')[0])
                                minor_version = float(version_str.split('.')[1])
                                
                                if major_version < 11 or (major_version == 11 and minor_version < 8):
                                    self.results["warnings"].append(
                                        f"CUDA 版本 {version_str} 低於建議版本 11.8"
                                    )
                                    print(f"⚠ 警告: CUDA 版本過舊，建議使用 11.8 或 12.x")
                            except:
                                pass
                            
                            return self.results["cuda"]
            
            # nvcc 執行失敗，嘗試從 nvidia-smi 取得 CUDA 版本
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout
                for line in output.split('\n'):
                    if 'CUDA Version' in line:
                        # 例如: "| NVIDIA-SMI 535.xx    Driver Version: 535.xx    CUDA Version: 12.2 |"
                        parts = line.split('CUDA Version:')
                        if len(parts) > 1:
                            version_str = parts[1].split('|')[0].strip()
                            self.results["cuda"] = {
                                "available": True,
                                "version": version_str,
                                "source": "nvidia-smi",
                                "note": "CUDA toolkit 可能未安裝，但驅動支援此版本"
                            }
                            print(f"✓ CUDA 版本 (從驅動): {version_str}")
                            print(f"  註: 建議安裝 CUDA Toolkit 以獲得完整功能")
                            return self.results["cuda"]
            
            # 無法取得 CUDA 版本
            self.results["cuda"] = {"available": False}
            self.results["errors"].append("無法偵測 CUDA 版本，請確認 CUDA Toolkit 已安裝")
            print("✗ 無法偵測 CUDA 版本")
            
        except FileNotFoundError:
            self.results["cuda"] = {"available": False}
            self.results["errors"].append("找不到 nvcc，CUDA Toolkit 可能未安裝")
            print("✗ 找不到 nvcc，請安裝 CUDA Toolkit")
        except Exception as e:
            self.results["cuda"] = {"available": False}
            self.results["errors"].append(f"CUDA 檢查失敗: {str(e)}")
            print(f"✗ CUDA 檢查失敗: {e}")
        
        return self.results["cuda"]

    def check_memory(self) -> Dict:
        """檢查系統記憶體"""
        try:
            if platform.system() == "Windows":
                # Windows 系統 - 使用 PowerShell
                result = subprocess.run(
                    ["powershell", "-Command", 
                     "(Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory | ConvertTo-Json)"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    try:
                        import json as json_module
                        mem_data = json_module.loads(result.stdout.strip())
                        total_kb = mem_data.get('TotalVisibleMemorySize', 0)
                        free_kb = mem_data.get('FreePhysicalMemory', 0)
                        
                        if total_kb > 0:
                            self.results["memory"] = {
                                "total_gb": round(total_kb / (1024 * 1024), 2),
                                "free_gb": round(free_kb / (1024 * 1024), 2),
                                "used_gb": round((total_kb - free_kb) / (1024 * 1024), 2),
                                "usage_percent": round((total_kb - free_kb) / total_kb * 100, 2)
                            }
                    except:
                        pass
            
            elif platform.system() == "Linux":
                # Linux 系統
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                
                total_kb = 0
                available_kb = 0
                
                for line in meminfo.split('\n'):
                    if line.startswith('MemTotal:'):
                        total_kb = int(line.split()[1])
                    elif line.startswith('MemAvailable:'):
                        available_kb = int(line.split()[1])
                
                if total_kb > 0:
                    self.results["memory"] = {
                        "total_gb": round(total_kb / (1024 * 1024), 2),
                        "available_gb": round(available_kb / (1024 * 1024), 2),
                        "used_gb": round((total_kb - available_kb) / (1024 * 1024), 2),
                        "usage_percent": round((total_kb - available_kb) / total_kb * 100, 2)
                    }
            
            if self.results["memory"]:
                print(f"✓ 系統記憶體: {self.results['memory']['total_gb']} GB")
                print(f"  可用: {self.results['memory'].get('available_gb', self.results['memory'].get('free_gb', 0))} GB " +
                      f"({100 - self.results['memory']['usage_percent']:.1f}%)")
                
                # 檢查記憶體是否足夠
                available = self.results['memory'].get('available_gb', self.results['memory'].get('free_gb', 0))
                if available < 60:
                    self.results["warnings"].append(
                        f"可用記憶體 {available} GB 低於建議的 60 GB"
                    )
                    print(f"⚠ 警告: 可用記憶體較少，建議關閉其他應用程式")
            else:
                self.results["errors"].append("無法取得記憶體資訊")
                print("✗ 無法取得記憶體資訊")
                
        except Exception as e:
            self.results["errors"].append(f"記憶體檢查失敗: {str(e)}")
            print(f"✗ 記憶體檢查失敗: {e}")
        
        return self.results["memory"]

    def check_all(self) -> Dict:
        """執行所有硬體檢查"""
        print("=" * 60)
        print("DeepSeek-OCR 硬體環境檢查")
        print("=" * 60)
        print()
        
        print("【系統資訊】")
        self.check_system_info()
        print()
        
        print("【GPU 檢查】")
        self.check_gpu_nvidia_smi()
        print()
        
        print("【CUDA 檢查】")
        self.check_cuda_version()
        print()
        
        print("【記憶體檢查】")
        self.check_memory()
        print()
        
        # 判斷整體狀態
        if len(self.results["errors"]) == 0:
            if len(self.results["warnings"]) == 0:
                self.results["status"] = "pass"
                print("=" * 60)
                print("✓ 硬體檢查通過！系統符合 DeepSeek-OCR 運行需求")
                print("=" * 60)
            else:
                self.results["status"] = "pass_with_warnings"
                print("=" * 60)
                print("⚠ 硬體檢查通過（有警告）")
                print("警告項目:")
                for warning in self.results["warnings"]:
                    print(f"  - {warning}")
                print("=" * 60)
        else:
            self.results["status"] = "fail"
            print("=" * 60)
            print("✗ 硬體檢查失敗")
            print("錯誤項目:")
            for error in self.results["errors"]:
                print(f"  - {error}")
            print("=" * 60)
        
        return self.results
    
    def save_report(self, output_path: str = "hardware_report.json"):
        """儲存檢查報告為 JSON 檔案"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ 報告已儲存至: {output_file.absolute()}")
            return True
        except Exception as e:
            print(f"\n✗ 儲存報告失敗: {e}")
            return False


def main():
    """主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DeepSeek-OCR 硬體環境檢查工具')
    parser.add_argument(
        '--output', '-o',
        default='outputs/hardware_report.json',
        help='輸出報告檔案路徑 (預設: outputs/hardware_report.json)'
    )
    parser.add_argument(
        '--json-only',
        action='store_true',
        help='僅輸出 JSON 格式（不顯示詳細資訊）'
    )
    
    args = parser.parse_args()
    
    checker = HardwareChecker()
    
    if args.json_only:
        # 僅輸出 JSON
        results = checker.check_all()
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        # 顯示詳細資訊並儲存報告
        results = checker.check_all()
        checker.save_report(args.output)
    
    # 根據檢查結果設定退出碼
    if results["status"] == "fail":
        sys.exit(1)
    elif results["status"] == "pass_with_warnings":
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
