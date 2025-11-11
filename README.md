# DeepSeek-OCR 本地部署系統

[![Python](https://img.shields.io/badge/Python-3.12.9-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.5.1-red.svg)](https://pytorch.org/)
[![CUDA](https://img.shields.io/badge/CUDA-12.1-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

DeepSeek-OCR 的 Windows 本地部署解決方案，支援單張圖片和批次處理，具備完整的記憶體管理和效能追蹤功能。

## ✨ 特色功能

- 🖼️ **單張圖片 OCR**: 快速辨識單張圖片文字
- 📚 **批次處理**: 支援多張圖片和 PDF 文件批次處理
- 🧠 **智慧記憶體管理**: 自動 VRAM 監控和清理
- 📊 **效能追蹤**: 詳細的處理時間和資源使用記錄
- 📄 **PDF 支援**: 自動轉換 PDF 為圖片進行 OCR
- ⚡ **GPU 加速**: 支援 NVIDIA GPU 加速（CUDA 12.x）
- 🔄 **CPU Fallback**: GPU 記憶體不足時自動切換 CPU

## 📋 系統需求

### 硬體需求
- **CPU**: 4 核心以上
- **RAM**: 16 GB 以上
- **GPU**: NVIDIA GPU with 6GB+ VRAM（建議 8GB+）
- **儲存空間**: 20 GB 可用空間

### 軟體需求
- **作業系統**: Windows 10/11 (64-bit)
- **Python**: 3.12.9
- **NVIDIA 驅動**: 最新版本
- **CUDA**: 12.x（由 PyTorch 提供）

### 已驗證配置
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU (8GB)
- 驅動: 576.02
- CUDA: 12.8
- RAM: 62 GB

## 🚀 快速開始

### 1. 環境準備

```powershell
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
.\.venv\Scripts\Activate.ps1

# 安裝依賴
pip install -r requirements.txt
```

### 2. 下載模型

```powershell
python scripts/download_model.py
```

### 3. 驗證安裝

```powershell
# 檢查硬體
python scripts/check_hardware.py

# 驗證 GPU
python scripts/verify_gpu.py

# 驗證模型
python scripts/validate_model.py
```

### 4. 開始使用

```powershell
# 單張圖片 OCR
python scripts/test_ocr.py image.png

# 批次處理
python scripts/batch_test.py images_folder/

# PDF 處理
python scripts/batch_test.py document.pdf
```

## 📖 使用說明

### 單張圖片 OCR

```powershell
# 基本用法
python scripts/test_ocr.py image.png

# 指定輸出目錄
python scripts/test_ocr.py image.png --output outputs/result1

# 儲存結果檔案
python scripts/test_ocr.py image.png --save

# JSON 格式輸出
python scripts/test_ocr.py image.png --json
```

### 批次處理

```powershell
# 處理圖片目錄
python scripts/batch_test.py path/to/images/

# 處理 PDF（限制頁數）
python scripts/batch_test.py document.pdf --max-pages 50

# 指定輸出目錄
python scripts/batch_test.py images/ --output outputs/batch1
```

### 效能監控

```powershell
# 即時監控
python scripts/monitor_performance.py

# 匯出報告
python scripts/monitor_performance.py --export outputs/perf_report.json
```

## 📁 專案結構

```
DeepSeek-OCR/
├── .venv/                      # Python 虛擬環境
├── models/                     # 模型目錄
│   └── deepseek-ocr/          # DeepSeek-OCR 模型 (6.36 GB)
├── src/                        # 原始碼
│   ├── image_processor.py     # 圖片預處理
│   ├── ocr_engine.py          # OCR 推理引擎
│   ├── performance_tracker.py # 效能追蹤
│   ├── memory_manager.py      # 記憶體管理
│   ├── pdf_converter.py       # PDF 轉換
│   ├── logger.py              # 日誌系統
│   ├── error_handler.py       # 錯誤處理
│   ├── config_loader.py       # 配置載入
│   └── version_info.py        # 版本資訊
├── scripts/                    # 工具腳本
│   ├── check_hardware.py      # 硬體檢查
│   ├── verify_gpu.py          # GPU 驗證
│   ├── download_model.py      # 模型下載
│   ├── validate_model.py      # 模型驗證
│   ├── test_ocr.py            # OCR 測試
│   ├── batch_test.py          # 批次處理
│   ├── monitor_performance.py # 效能監控
│   ├── backup_environment.ps1 # 環境備份
│   └── e2e_test.ps1           # 端到端測試
├── config/                     # 配置檔案
│   └── system_config.json     # 系統配置
├── outputs/                    # 輸出目錄
│   ├── logs/                  # 日誌檔案
│   └── temp/                  # 暫存檔案
├── docs/                       # 文件
│   └── SOP_v1.md              # 標準作業程序
├── requirements.txt            # Python 套件清單
├── PROGRESS.md                # 進度記錄
└── README.md                  # 本文件
```

## 🔧 配置

系統配置位於 `config/system_config.json`，可調整以下參數：

- **裝置設定**: GPU/CPU 選擇
- **模型參數**: 解析度、批次大小
- **記憶體管理**: VRAM 警戒值
- **日誌設定**: 日誌等級、輸出格式

## 📊 效能參考

| 項目 | 數值 |
|------|------|
| 單張圖片處理時間 | 3-10 秒 |
| VRAM 使用（模型載入） | 2-3 GB |
| VRAM 使用（推理） | 3-5 GB |
| 支援最大圖片尺寸 | 4096x4096 |
| 建議批次大小 | 2-4 |

## 🛠️ 維護工具

### 環境備份

```powershell
.\scripts\backup_environment.ps1
```

### 端到端測試

```powershell
.\scripts\e2e_test.ps1
```

### 版本資訊

```powershell
python -c "from src.version_info import print_version_info; print_version_info()"
```

## ❓ 疑難排解

### CUDA 不可用

```powershell
# 檢查 NVIDIA 驅動
nvidia-smi

# 重新安裝 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 記憶體不足

1. 減少批次大小
2. 降低圖片解析度
3. 使用 CPU 模式（編輯 `config/system_config.json`）

### 模型載入失敗

```powershell
# 重新下載模型
python scripts/download_model.py

# 驗證模型
python scripts/validate_model.py
```

更多問題請參考 [SOP 文件](docs/SOP_v1.md)。

## 📚 文件

- [標準作業程序 (SOP)](docs/SOP_v1.md) - 完整的安裝和使用指南
- [進度記錄](PROGRESS.md) - 專案開發進度

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

本專案採用 MIT 授權條款。

## 🙏 致謝

- [DeepSeek-AI](https://github.com/deepseek-ai) - DeepSeek-OCR 模型
- [Hugging Face](https://huggingface.co/) - Transformers 函式庫
- [PyTorch](https://pytorch.org/) - 深度學習框架

---

**DeepSeek-OCR v1.0.0** | 最後更新: 2025-11-01
