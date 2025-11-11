#!/usr/bin/env python3
"""
Windows 環境驗證腳本
檢查 Conda/Miniconda 安裝狀態、環境變數設定
"""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


class WindowsEnvironmentChecker:
    """Windows 環境檢查類別"""

    def __init__(self):
        self.results = {
            "conda": {},
            "python": {},
            "environment_variables": {},
            "status": "unknown",
            "errors": [],
            "warnings": [],
            "recommendations": [],
        }

    def check_conda_installed(self) -> Dict:
        """檢查 Conda/Miniconda 是否已安裝"""
        try:
            # 嘗試執行 conda --version
            result = subprocess.run(
                ["conda", "--version"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                version_output = result.stdout.strip()
                # 例如: "conda 24.7.1"
                version = version_output.split()[-1] if version_output else "unknown"

                # 取得 Conda 安裝路徑
                conda_info_result = subprocess.run(
                    ["conda", "info", "--base"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                conda_base = (
                    conda_info_result.stdout.strip()
                    if conda_info_result.returncode == 0
                    else "unknown"
                )

                self.results["conda"] = {
                    "installed": True,
                    "version": version,
                    "base_path": conda_base,
                    "executable": "conda",
                }

                print(f"✓ Conda 已安裝")
                print(f"  版本: {version}")
                print(f"  安裝路徑: {conda_base}")

                return self.results["conda"]

            # conda 指令執行失敗
            self.results["conda"] = {"installed": False}
            self.results["errors"].append("Conda 未安裝或無法執行")
            print("✗ Conda 未安裝")

        except FileNotFoundError:
            self.results["conda"] = {"installed": False}
            self.results["errors"].append("找不到 conda 指令，Conda 可能未安裝")
            print("✗ 找不到 conda 指令")
        except subprocess.TimeoutExpired:
            self.results["conda"] = {"installed": False}
            self.results["errors"].append("conda 指令執行超時")
            print("✗ conda 指令執行超時")
        except Exception as e:
            self.results["conda"] = {"installed": False}
            self.results["errors"].append(f"Conda 檢查失敗: {str(e)}")
            print(f"✗ Conda 檢查失敗: {e}")

        return self.results["conda"]

    def check_python_environment(self) -> Dict:
        """檢查 Python 環境"""
        try:
            self.results["python"] = {
                "version": sys.version.split()[0],
                "executable": sys.executable,
                "is_conda": "conda" in sys.executable.lower()
                or "miniconda" in sys.executable.lower()
                or "anaconda" in sys.executable.lower(),
                "platform": platform.platform(),
            }

            print(f"✓ Python 環境")
            print(f"  版本: {self.results['python']['version']}")
            print(f"  執行檔: {self.results['python']['executable']}")
            print(
                f"  來源: {'Conda 環境' if self.results['python']['is_conda'] else '系統 Python'}"
            )

            # 檢查是否為建議版本
            major, minor = sys.version_info[:2]
            if major == 3 and minor == 12:
                print(f"  ✓ Python 版本符合建議（3.12.x）")
            else:
                self.results["warnings"].append(
                    f"Python 版本 {major}.{minor} 不是建議版本 3.12.x"
                )
                print(f"  ⚠ 建議使用 Python 3.12.x")

        except Exception as e:
            self.results["errors"].append(f"Python 環境檢查失敗: {str(e)}")
            print(f"✗ Python 環境檢查失敗: {e}")

        return self.results["python"]

    def check_environment_variables(self) -> Dict:
        """檢查環境變數設定"""
        try:
            env_vars = {
                "PATH": os.environ.get("PATH", ""),
                "CUDA_PATH": os.environ.get("CUDA_PATH", ""),
                "CUDA_HOME": os.environ.get("CUDA_HOME", ""),
                "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
            }

            self.results["environment_variables"] = env_vars

            print(f"✓ 環境變數檢查")

            # 檢查 PATH 中是否包含 Conda
            if "conda" in env_vars["PATH"].lower() or "miniconda" in env_vars[
                "PATH"
            ].lower():
                print(f"  ✓ PATH 包含 Conda 路徑")
            else:
                if not self.results["conda"].get("installed", False):
                    print(f"  ℹ PATH 未包含 Conda 路徑（Conda 未安裝）")
                else:
                    self.results["warnings"].append("PATH 未包含 Conda 路徑")
                    print(f"  ⚠ PATH 未包含 Conda 路徑")

            # 檢查 CUDA 相關環境變數
            if env_vars["CUDA_PATH"] or env_vars["CUDA_HOME"]:
                cuda_path = env_vars["CUDA_PATH"] or env_vars["CUDA_HOME"]
                print(f"  ✓ CUDA 環境變數已設定: {cuda_path}")
            else:
                self.results["warnings"].append("CUDA_PATH 或 CUDA_HOME 未設定")
                print(f"  ⚠ CUDA_PATH/CUDA_HOME 未設定（可能不影響運作）")

        except Exception as e:
            self.results["errors"].append(f"環境變數檢查失敗: {str(e)}")
            print(f"✗ 環境變數檢查失敗: {e}")

        return self.results["environment_variables"]

    def provide_installation_guide(self):
        """提供 Miniconda 安裝指引"""
        if not self.results["conda"].get("installed", False):
            print("\n" + "=" * 60)
            print("📦 Miniconda 安裝指引")
            print("=" * 60)
            print()
            print("Miniconda 是輕量級的 Conda 發行版，建議安裝以管理 Python 環境。")
            print()
            print("【下載連結】")
            print(
                "  Windows 64-bit: https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
            )
            print()
            print("【安裝步驟】")
            print("  1. 下載上述安裝程式")
            print("  2. 執行安裝程式（建議使用預設設定）")
            print('  3. 安裝時勾選 "Add Miniconda3 to my PATH environment variable"')
            print("  4. 安裝完成後，重新開啟 PowerShell 或 CMD")
            print("  5. 執行 'conda --version' 驗證安裝")
            print()
            print("【或使用 Chocolatey 安裝（進階）】")
            print("  choco install miniconda3")
            print()
            print("【或使用 winget 安裝（Windows 11）】")
            print("  winget install Anaconda.Miniconda3")
            print()
            print("安裝完成後，請重新執行此腳本進行驗證。")
            print("=" * 60)

            self.results["recommendations"].append(
                "請安裝 Miniconda: https://docs.conda.io/en/latest/miniconda.html"
            )

    def check_all(self) -> Dict:
        """執行所有環境檢查"""
        print("=" * 60)
        print("DeepSeek-OCR Windows 環境驗證")
        print("=" * 60)
        print()

        print("【Conda 檢查】")
        self.check_conda_installed()
        print()

        print("【Python 環境】")
        self.check_python_environment()
        print()

        print("【環境變數】")
        self.check_environment_variables()
        print()

        # 判斷整體狀態
        if len(self.results["errors"]) == 0:
            if len(self.results["warnings"]) == 0:
                self.results["status"] = "pass"
                print("=" * 60)
                print("✓ 環境驗證通過！")
                print("=" * 60)
            else:
                self.results["status"] = "pass_with_warnings"
                print("=" * 60)
                print("⚠ 環境驗證通過（有警告）")
                print("警告項目:")
                for warning in self.results["warnings"]:
                    print(f"  - {warning}")
                print("=" * 60)
        else:
            self.results["status"] = "fail"
            print("=" * 60)
            print("✗ 環境驗證失敗")
            print("錯誤項目:")
            for error in self.results["errors"]:
                print(f"  - {error}")
            print("=" * 60)

            # 提供安裝指引
            self.provide_installation_guide()

        return self.results

    def save_report(self, output_path: str = "environment_report.json"):
        """儲存檢查報告為 JSON 檔案"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)

            print(f"\n✓ 報告已儲存至: {output_file.absolute()}")
            return True
        except Exception as e:
            print(f"\n✗ 儲存報告失敗: {e}")
            return False


def main():
    """主程式"""
    import argparse

    parser = argparse.ArgumentParser(description="DeepSeek-OCR Windows 環境驗證工具")
    parser.add_argument(
        "--output",
        "-o",
        default="outputs/environment_report.json",
        help="輸出報告檔案路徑 (預設: outputs/environment_report.json)",
    )
    parser.add_argument(
        "--json-only", action="store_true", help="僅輸出 JSON 格式（不顯示詳細資訊）"
    )

    args = parser.parse_args()

    checker = WindowsEnvironmentChecker()

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
