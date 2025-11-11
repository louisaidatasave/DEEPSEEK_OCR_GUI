# DeepSeek-OCR 標準作業程序 (SOP) v1.0

## 文件資訊

- **文件名稱**: DeepSeek-OCR 部署與使用標準作業程序
- **版本**: 1.0.0
- **最後更新**: 2025-11-01
- **適用對象**: Windows 使用者
- **作業系統**: Windows 10/11
- **硬體需求**: NVIDIA GPU (8GB+ VRAM 建議)

---

## 目錄

1. [硬體與軟體需求](#1-硬體與軟體需求)
2. [環境準備](#2-環境準備)
3. [模型部署](#3-模型部署)
4. [功能測試與驗證](#4-功能測試與驗證)
5. [日常使用](#5-日常使用)
6. [疑難排解](#6-疑難排解)
7. [維護與更新](#7-維護與更新)
8. [附錄](#8-附錄)

---

## 1. 硬體與軟體需求

### 1.1 硬體需求

#### 最低需求
- **CPU**: 4 核心以上
- **RAM**: 16 GB
- **GPU**: NVIDIA GPU with 6GB+ VRAM
- **儲存空間**: 20 GB 可用空間

#### 建議配置
- **CPU**: 8 核心以上
- **RAM**: 32 GB
- **GPU**: NVIDIA RTX 3060 / 4060 或更高 (8GB+ VRAM)
- **儲存空間**: 50 GB 可用空間（含模型和輸出）

#### 已驗證配置
- **GPU**: NVIDIA GeForce RTX 4060 Laptop GPU (8GB)
- **驅動**: 576.02
- **CUDA**: 12.8
- **RAM**: 62 GB

### 1.2 軟體需求

#### 必要軟體
- **作業系統**: Windows 10/11 (64-bit)
- **Python**: 3.12.9
- **NVIDIA 驅動**: 最新版本
- **CUDA**: 12.x (由 PyTorch 提供)

#### Python 套件
- PyTorch 2.5.1+cu121
- Transformers 4.57.1
- Pillow 11.3.0
- pdf2image 1.17.0
- 其他依賴（見 requirements.txt）

---

## 2. 環境準備

### 2.1 檢查硬體

執行硬體檢查腳本：

```powershell
python scripts/check_hardware.py
```

**預期輸出**：
```
✓ GPU 可用: NVIDIA GeForce RTX 4060 Laptop GPU
✓ VRAM: 8.00 GB
✓ CUDA 版本: 12.8
✓ RAM: 61.75 GB
```

### 2.2 建立 Python 虛擬環境

```powershell
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
.\.venv\Scripts\Activate.ps1

# 驗證 Python 版本
python --version
# 應顯示: Python 3.12.9
```

### 2.3 安裝依賴套件

```powershell
# 升級 pip
python -m pip install --upgrade pip

# 安裝 PyTorch (CUDA 12.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 安裝其他依賴
pip install -r requirements.txt
```

### 2.4 驗證 GPU 可用性

```powershell
python scripts/verify_gpu.py
```

**預期輸出**：
```
✓ CUDA 可用
✓ GPU: NVIDIA GeForce RTX 4060 Laptop GPU
✓ CUDA 版本: 12.1
✓ VRAM: 8.00 GB
```

---

## 3. 模型部署

### 3.1 下載模型

```powershell
python scripts/download_model.py
```

**下載資訊**：
- 模型名稱: deepseek-ai/DeepSeek-OCR
- 模型大小: 約 6.36 GB
- 儲存位置: `./models/deepseek-ocr/`
- 預估時間: 10-30 分鐘（視網路速度）

### 3.2 驗證模型

```powershell
python scripts/validate_model.py
```

**預期輸出**：
```
✓ 模型檔案完整
✓ 配置檔案正確
✓ 模型類型: DeepseekOCRForCausalLM
```

---

## 4. 功能測試與驗證

### 4.1 單張圖片 OCR 測試

```powershell
# 測試單張圖片
python scripts/test_ocr.py test_image.png

# 指定輸出目錄
python scripts/test_ocr.py test_image.png --output outputs/test1

# 儲存結果檔案
python scripts/test_ocr.py test_image.png --save
```

**預期結果**：
- 處理時間: 3-10 秒（視圖片大小）
- VRAM 使用: 2-4 GB
- 輸出格式: Markdown

### 4.2 批次處理測試

```powershell
# 批次處理圖片目錄
python scripts/batch_test.py images_folder/

# 處理 PDF 文件
python scripts/batch_test.py document.pdf --max-pages 10
```

### 4.3 效能追蹤測試

```powershell
python scripts/test_performance.py
```

---

## 5. 日常使用

### 5.1 單張圖片 OCR

**基本用法**：
```powershell
python scripts/test_ocr.py image.png
```

**進階選項**：
```powershell
# 自訂解析度
python scripts/test_ocr.py image.png --base-size 2048 --image-size 2048

# 啟用裁切模式
python scripts/test_ocr.py image.png --crop

# JSON 輸出
python scripts/test_ocr.py image.png --json
```

### 5.2 批次處理

**處理圖片目錄**：
```powershell
python scripts/batch_test.py path/to/images/
```

**處理 PDF 文件**：
```powershell
python scripts/batch_test.py document.pdf --max-pages 100
```

### 5.3 效能監控

**即時監控**：
```powershell
python scripts/monitor_performance.py
```

**匯出報告**：
```powershell
python scripts/monitor_performance.py --export outputs/perf_report.json
```

---

## 6. 疑難排解

### 6.1 CUDA 無法偵測

**症狀**：
```
CUDA 不可用
```

**解決方法**：
1. 檢查 NVIDIA 驅動是否安裝
   ```powershell
   nvidia-smi
   ```

2. 重新安裝 PyTorch CUDA 版本
   ```powershell
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

3. 驗證 CUDA
   ```powershell
   python -c "import torch; print(torch.cuda.is_available())"
   ```

### 6.2 記憶體不足 (OOM)

**症狀**：
```
RuntimeError: CUDA out of memory
```

**解決方法**：
1. 減少批次大小
2. 降低圖片解析度
3. 使用 CPU 模式
   ```powershell
   # 編輯 config/system_config.json
   # 將 "device.type" 改為 "cpu"
   ```

### 6.3 模型載入失敗

**症狀**：
```
ModelLoadError: 模型載入失敗
```

**解決方法**：
1. 重新下載模型
   ```powershell
   python scripts/download_model.py
   ```

2. 驗證模型完整性
   ```powershell
   python scripts/validate_model.py
   ```

### 6.4 PDF 轉換失敗

**症狀**：
```
PDFConversionError: PDF 轉換失敗
```

**解決方法**：
1. 確認 pdf2image 已安裝
   ```powershell
   pip install pdf2image
   ```

2. 檢查 PDF 檔案是否損壞
3. 嘗試較小的頁數範圍

### 6.5 圖片格式不支援

**症狀**：
```
ValueError: 不支援的圖片格式
```

**解決方法**：
- 支援格式: PNG, JPG, JPEG, BMP, TIFF, WEBP
- 轉換圖片格式後重試

---

## 7. 維護與更新

### 7.1 環境備份

```powershell
# 執行備份腳本
.\scripts\backup_environment.ps1
```

備份內容：
- Python 套件清單
- 配置檔案
- 環境變數
- 系統資訊

### 7.2 版本檢查

```powershell
python -c "from src.version_info import print_version_info; print_version_info()"
```

### 7.3 更新套件

```powershell
# 更新所有套件
pip install --upgrade -r requirements.txt

# 更新特定套件
pip install --upgrade transformers
```

### 7.4 清理快取

```powershell
# 清理 Python 快取
python -c "import torch; torch.cuda.empty_cache()"

# 清理輸出目錄
Remove-Item -Recurse -Force outputs/temp/*
```

---

## 8. 附錄

### 8.1 目錄結構

```
DeepSeek-OCR/
├── .venv/                  # Python 虛擬環境
├── models/                 # 模型目錄
│   └── deepseek-ocr/      # DeepSeek-OCR 模型
├── src/                    # 原始碼
│   ├── __init__.py
│   ├── image_processor.py
│   ├── ocr_engine.py
│   ├── performance_tracker.py
│   ├── memory_manager.py
│   ├── pdf_converter.py
│   ├── logger.py
│   ├── error_handler.py
│   ├── config_loader.py
│   └── version_info.py
├── scripts/                # 工具腳本
│   ├── check_hardware.py
│   ├── verify_gpu.py
│   ├── download_model.py
│   ├── validate_model.py
│   ├── test_ocr.py
│   ├── batch_test.py
│   ├── monitor_performance.py
│   └── backup_environment.ps1
├── config/                 # 配置檔案
│   └── system_config.json
├── outputs/                # 輸出目錄
│   ├── logs/              # 日誌檔案
│   └── temp/              # 暫存檔案
├── docs/                   # 文件
│   └── SOP_v1.md          # 本文件
├── requirements.txt        # Python 套件清單
├── PROGRESS.md            # 進度記錄
└── README.md              # 專案說明
```

### 8.2 常用指令速查

```powershell
# 啟動虛擬環境
.\.venv\Scripts\Activate.ps1

# 硬體檢查
python scripts/check_hardware.py

# GPU 驗證
python scripts/verify_gpu.py

# 單張 OCR
python scripts/test_ocr.py image.png

# 批次處理
python scripts/batch_test.py images/

# 效能監控
python scripts/monitor_performance.py

# 環境備份
.\scripts\backup_environment.ps1

# 版本資訊
python -c "from src.version_info import print_version_info; print_version_info()"
```

### 8.3 效能參考

| 項目 | 數值 |
|------|------|
| 單張圖片處理時間 | 3-10 秒 |
| VRAM 使用（模型載入） | 2-3 GB |
| VRAM 使用（推理） | 3-5 GB |
| 支援最大圖片尺寸 | 4096x4096 |
| 建議批次大小 | 2-4 |

### 8.4 聯絡資訊

- **專案**: DeepSeek-OCR
- **版本**: 1.0.0
- **文件版本**: 1.0.0

---

**文件結束**
