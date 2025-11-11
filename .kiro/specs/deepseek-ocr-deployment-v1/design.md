# Design Document

## Overview

本設計文件定義 DeepSeek OCR 本地部署 V1 版本的技術架構。系統將**優先在 Windows 原生環境**下使用 Conda 建立隔離的 Python 環境，所有套件和模型均安裝於專案本地目錄，避免全域污染。部署目標是在 RTX 4060（8GB VRAM）上實現穩定的 OCR 推理能力。

**部署策略**: Windows 原生優先，WSL2 作為備援方案（僅在遇到無法解決的相容性問題時使用）。

## Architecture

### 系統架構圖

**方案 A: Windows 原生環境（主要方案）**

```
┌─────────────────────────────────────────────────────────────┐
│                    Windows 11 Host                          │
│                                                               │
│   Project Directory (本地安裝)                               │
│   D:\NAS_Share\Data\...\07_DEEPSEEK_OCR\                    │
│                                                               │
│   ├── .venv/              (Conda 虛擬環境)                   │
│   ├── models/             (模型權重)                         │
│   ├── DeepSeek-OCR/       (原始碼)                           │
│   ├── scripts/            (測試腳本)                         │
│   ├── src/                (自訂模組)                         │
│   ├── outputs/            (輸出結果)                         │
│   └── logs/               (日誌記錄)                         │
│                                                               │
│   GPU: NVIDIA RTX 4060 (8GB VRAM)                           │
│   CUDA: 12.8                                                 │
│   Driver: 576.02                                             │
└─────────────────────────────────────────────────────────────┘
```

**方案 B: WSL2 環境（備援方案，僅在必要時使用）**

```
┌─────────────────────────────────────────────────────────────┐
│                    Windows 11 Host                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              WSL2 Ubuntu 22.04/24.04                  │  │
│  │                                                         │  │
│  │   /mnt/d/.../07_DEEPSEEK_OCR/                         │  │
│  │   (掛載 Windows 專案目錄)                             │  │
│  │                                                         │  │
│  │   GPU Access: NVIDIA RTX 4060 (透過 WSL2)            │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 技術堆疊

- **作業系統**: Windows 11 (原生環境)
- **Python 環境**: Conda 虛擬環境 (Python 3.12.9)
- **深度學習框架**: PyTorch 2.6.0 + CUDA 12.x (相容 11.8)
- **OCR 模型**: DeepSeek-OCR (3B 參數)
- **推理引擎**: Transformers 4.46.3 / vLLM 0.8.5 (選用)
- **加速組件**: Flash Attention 2.7.3 (選用，若編譯失敗則使用標準模式)
- **Web 框架**: Gradio (選用)


## Components and Interfaces

### 1. 環境管理模組 (Environment Manager)

**職責**: 檢查硬體、安裝驅動、建立 Conda 環境

**關鍵組件**:
- `check_hardware.py`: 驗證 GPU、RAM、CUDA 版本
- `setup_conda.sh`: 建立虛擬環境腳本
- `install_dependencies.sh`: 安裝 PyTorch 和相關套件

**介面**:
```python
class EnvironmentManager:
    def check_gpu_available() -> bool
    def check_cuda_version() -> str
    def verify_memory() -> dict
    def create_conda_env(env_name: str, python_version: str) -> bool
    def install_pytorch(cuda_version: str) -> bool
```

### 2. 模型管理模組 (Model Manager)

**職責**: 下載、載入、管理 DeepSeek-OCR 模型

**關鍵組件**:
- `model_downloader.py`: 從 Hugging Face 下載模型
- `model_loader.py`: 載入模型到 GPU/CPU
- `model_config.json`: 模型配置檔案

**介面**:
```python
class ModelManager:
    def download_model(model_name: str, local_dir: str) -> bool
    def load_model(model_path: str, device: str) -> Model
    def get_model_info() -> dict
    def validate_model() -> bool
```

**模型儲存結構**:
```
models/
├── deepseek-ocr/
│   ├── config.json
│   ├── pytorch_model.bin (或 .safetensors)
│   ├── tokenizer_config.json
│   ├── tokenizer.json
│   └── special_tokens_map.json
```

### 3. OCR 推理引擎 (OCR Inference Engine)

**職責**: 執行圖片/PDF 的文字辨識

**關鍵組件**:
- `ocr_engine.py`: 核心推理邏輯
- `image_processor.py`: 圖片預處理
- `pdf_converter.py`: PDF 轉圖片
- `batch_processor.py`: 批次處理管理

**介面**:
```python
class OCREngine:
    def __init__(self, model, tokenizer, device)
    def process_image(image_path: str) -> str
    def process_pdf(pdf_path: str, pages: list) -> list[str]
    def batch_process(file_list: list, batch_size: int) -> list[str]
    def get_inference_stats() -> dict
```

**處理流程**:
```
輸入圖片 → 預處理 → 模型推理 → 後處理 → Markdown 輸出
    ↓
  調整大小
  正規化
    ↓
  Tokenization
  GPU 推理
    ↓
  解碼
  格式化
```

### 4. 記憶體管理模組 (Memory Manager)

**職責**: 監控 VRAM 使用，動態調整批次大小

**關鍵組件**:
- `vram_monitor.py`: 即時監控 GPU 記憶體
- `batch_optimizer.py`: 動態調整批次大小
- `fallback_handler.py`: CPU fallback 機制

**介面**:
```python
class MemoryManager:
    def get_vram_usage() -> dict
    def calculate_optimal_batch_size(image_size: tuple) -> int
    def enable_cpu_fallback() -> None
    def clear_cache() -> None
```

**VRAM 管理策略**:
- 單張圖片: 直接 GPU 推理
- 2-5 張: 小批次處理
- 5+ 張: 動態調整批次大小
- VRAM > 90%: 啟用 CPU fallback

### 5. Web UI 模組 (Web Interface)

**職責**: 提供網頁操作介面（選用）

**關鍵組件**:
- `gradio_app.py`: Gradio 應用程式
- `api_server.py`: REST API 端點（選用）

**介面**:
```python
class WebUI:
    def launch(port: int, share: bool) -> None
    def process_upload(file) -> str
    def get_history() -> list
```

### 6. 日誌與監控模組 (Logging & Monitoring)

**職責**: 記錄操作日誌、效能指標

**關鍵組件**:
- `logger.py`: 統一日誌管理
- `performance_tracker.py`: 效能追蹤
- `error_handler.py`: 錯誤處理

**介面**:
```python
class Logger:
    def log_info(message: str) -> None
    def log_error(error: Exception) -> None
    def log_performance(metrics: dict) -> None
    def export_logs(format: str) -> str
```


## Data Models

### 1. OCR Result Model

```python
@dataclass
class OCRResult:
    """OCR 辨識結果資料模型"""
    file_path: str                    # 原始檔案路徑
    page_number: int                  # 頁碼（PDF 用）
    text_content: str                 # 辨識文字（Markdown 格式）
    confidence_score: float           # 信心分數
    processing_time: float            # 處理時間（秒）
    image_resolution: tuple[int, int] # 圖片解析度
    vram_used: float                  # VRAM 使用量（MB）
    timestamp: datetime               # 處理時間戳
    error_message: Optional[str]      # 錯誤訊息（如有）
```

### 2. System Configuration Model

```python
@dataclass
class SystemConfig:
    """系統配置資料模型"""
    project_root: Path                # 專案根目錄
    model_path: Path                  # 模型路徑
    conda_env_name: str               # Conda 環境名稱
    python_version: str               # Python 版本
    pytorch_version: str              # PyTorch 版本
    cuda_version: str                 # CUDA 版本
    device: str                       # 運算裝置 (cuda/cpu)
    max_batch_size: int               # 最大批次大小
    vram_threshold: float             # VRAM 警戒值（%）
    output_format: str                # 輸出格式 (markdown/txt)
```

### 3. Hardware Info Model

```python
@dataclass
class HardwareInfo:
    """硬體資訊資料模型"""
    gpu_name: str                     # GPU 型號
    gpu_memory_total: float           # 總 VRAM (GB)
    gpu_memory_available: float       # 可用 VRAM (GB)
    cuda_available: bool              # CUDA 是否可用
    cuda_version: str                 # CUDA 版本
    driver_version: str               # 驅動版本
    cpu_count: int                    # CPU 核心數
    ram_total: float                  # 總 RAM (GB)
    ram_available: float              # 可用 RAM (GB)
```

### 4. Processing Job Model

```python
@dataclass
class ProcessingJob:
    """處理任務資料模型"""
    job_id: str                       # 任務 ID
    input_files: list[Path]           # 輸入檔案清單
    status: str                       # 狀態 (pending/processing/completed/failed)
    progress: float                   # 進度 (0-100%)
    results: list[OCRResult]          # 結果清單
    start_time: datetime              # 開始時間
    end_time: Optional[datetime]      # 結束時間
    total_pages: int                  # 總頁數
    processed_pages: int              # 已處理頁數
```

## Error Handling

### 錯誤分類與處理策略

#### 1. 環境錯誤 (Environment Errors)

**錯誤類型**:
- `CUDANotAvailableError`: CUDA 無法使用
- `DriverVersionError`: 驅動版本不符
- `CondaEnvError`: Conda 環境問題

**處理策略**:
```python
try:
    check_cuda_available()
except CUDANotAvailableError as e:
    logger.error(f"CUDA 檢查失敗: {e}")
    # 提供驅動安裝指引
    print_cuda_installation_guide()
    # 詢問是否使用 CPU 模式
    if user_confirm_cpu_mode():
        switch_to_cpu_mode()
```

#### 2. 模型錯誤 (Model Errors)

**錯誤類型**:
- `ModelDownloadError`: 模型下載失敗
- `ModelLoadError`: 模型載入失敗
- `ModelValidationError`: 模型驗證失敗

**處理策略**:
```python
try:
    model = load_model(model_path)
except ModelLoadError as e:
    logger.error(f"模型載入失敗: {e}")
    # 檢查模型檔案完整性
    if not validate_model_files(model_path):
        # 重新下載模型
        download_model(force=True)
    # 嘗試使用備用載入方式
    model = load_model_safe_mode(model_path)
```

#### 3. 記憶體錯誤 (Memory Errors)

**錯誤類型**:
- `OutOfMemoryError`: VRAM 不足
- `CUDAOutOfMemoryError`: GPU 記憶體溢位

**處理策略**:
```python
try:
    result = process_batch(images, batch_size=8)
except OutOfMemoryError as e:
    logger.warning(f"VRAM 不足，降低批次大小")
    # 清除 GPU 快取
    torch.cuda.empty_cache()
    # 減半批次大小重試
    result = process_batch(images, batch_size=4)
    # 若仍失敗，使用 CPU fallback
    if result is None:
        result = process_batch_cpu(images)
```

#### 4. 推理錯誤 (Inference Errors)

**錯誤類型**:
- `ImageProcessingError`: 圖片處理失敗
- `TokenizationError`: Tokenization 失敗
- `InferenceTimeoutError`: 推理超時

**處理策略**:
```python
try:
    text = ocr_engine.process_image(image_path)
except ImageProcessingError as e:
    logger.error(f"圖片處理失敗: {e}")
    # 嘗試不同的圖片格式轉換
    image = convert_image_format(image_path)
    text = ocr_engine.process_image(image)
except InferenceTimeoutError as e:
    logger.warning(f"推理超時，使用較小解析度重試")
    # 降低圖片解析度
    image = resize_image(image_path, max_size=1024)
    text = ocr_engine.process_image(image)
```

### 錯誤日誌格式

```json
{
  "timestamp": "2025-11-01T10:30:45",
  "level": "ERROR",
  "component": "OCREngine",
  "error_type": "OutOfMemoryError",
  "message": "VRAM 不足，當前使用 7.8GB/8GB",
  "stack_trace": "...",
  "context": {
    "batch_size": 8,
    "image_resolution": [2048, 1536],
    "vram_usage": 7.8
  },
  "resolution": "降低批次大小至 4 並重試"
}
```


## Testing Strategy

### 1. 單元測試 (Unit Tests)

**測試範圍**:
- 環境檢查函數
- 模型載入/卸載
- 圖片預處理
- 記憶體管理邏輯

**測試框架**: pytest

**範例測試**:
```python
def test_check_cuda_available():
    """測試 CUDA 可用性檢查"""
    result = check_cuda_available()
    assert isinstance(result, bool)
    if result:
        assert get_cuda_version() is not None

def test_image_preprocessing():
    """測試圖片預處理"""
    test_image = create_test_image(1024, 768)
    processed = preprocess_image(test_image)
    assert processed.shape[0] <= 1280  # 最大解析度限制
```

### 2. 整合測試 (Integration Tests)

**測試範圍**:
- 完整 OCR 流程（圖片 → 文字）
- 批次處理功能
- VRAM 管理機制
- 錯誤恢復流程

**測試案例**:
```python
def test_single_image_ocr():
    """測試單張圖片 OCR"""
    engine = OCREngine(model, tokenizer, device="cuda")
    result = engine.process_image("test_data/sample.png")
    assert result.text_content is not None
    assert result.processing_time < 10.0  # 10 秒內完成
    assert result.vram_used < 8000  # 不超過 8GB

def test_batch_processing_with_vram_limit():
    """測試批次處理與 VRAM 限制"""
    images = ["test_data/img1.png", "test_data/img2.png", ...]
    results = batch_process(images, max_vram_usage=0.9)
    assert len(results) == len(images)
    assert all(r.error_message is None for r in results)
```

### 3. 效能測試 (Performance Tests)

**測試指標**:
- 單張圖片處理時間
- 批次處理吞吐量
- VRAM 使用效率
- CPU fallback 效能

**基準測試**:
```python
def benchmark_inference_speed():
    """基準測試：推理速度"""
    test_images = load_test_dataset(100)
    start_time = time.time()
    
    for img in test_images:
        result = ocr_engine.process_image(img)
    
    total_time = time.time() - start_time
    avg_time = total_time / len(test_images)
    
    assert avg_time < 5.0  # 平均每張 < 5 秒
    print(f"平均處理時間: {avg_time:.2f} 秒/張")
```

### 4. 端到端測試 (E2E Tests)

**測試場景**:
- 從環境設定到完成 OCR 的完整流程
- PDF 多頁文件處理
- Web UI 操作流程
- 錯誤恢復與重試機制

**測試腳本**:
```bash
#!/bin/bash
# E2E 測試腳本

echo "1. 檢查環境..."
python scripts/check_environment.py

echo "2. 載入模型..."
python scripts/load_model.py

echo "3. 處理測試圖片..."
python scripts/test_ocr.py --input test_data/sample.png

echo "4. 批次處理測試..."
python scripts/batch_test.py --input test_data/batch/

echo "5. 驗證輸出..."
python scripts/validate_output.py
```

### 5. 驗收測試 (Acceptance Tests)

**驗收標準**（對應需求文件）:

| 需求 ID | 測試項目 | 驗收標準 | 測試方法 |
|---------|----------|----------|----------|
| REQ-1 | 環境驗證 | GPU 可用、CUDA 11.8+ | `nvidia-smi` + `torch.cuda.is_available()` |
| REQ-2 | Python 環境 | Conda 環境建立成功 | `conda env list` |
| REQ-3 | 模型部署 | 模型載入無錯誤 | `load_model()` 測試 |
| REQ-4 | 基礎推理 | 單張圖片 < 10 秒 | 計時測試 |
| REQ-5 | 批次處理 | 100 頁無 OOM 錯誤 | 批次測試 |
| REQ-6 | Web UI | 介面可存取 | HTTP 請求測試 |
| REQ-7 | 效能監控 | 日誌記錄完整 | 檢查日誌檔案 |
| REQ-8 | SOP 文件 | 文件完整且可執行 | 人工審查 |

## Installation and Deployment

### 本地安裝策略

**原則**: 所有套件和模型安裝於專案目錄，不影響全域環境

### 目錄結構

```
D:\NAS_Share\Data\08_Programming_Data\07_DEEPSEEK_OCR\
├── .venv/                          # Conda 虛擬環境（本地）
├── models/                         # 模型權重（本地）
│   └── deepseek-ocr/
├── DeepSeek-OCR/                   # 原始碼（Git clone）
├── scripts/                        # 自訂腳本
│   ├── setup_environment.sh
│   ├── download_model.py
│   ├── test_ocr.py
│   ├── batch_process.py
│   └── web_ui.py
├── test_data/                      # 測試資料
│   ├── images/
│   └── pdfs/
├── outputs/                        # 輸出結果
│   ├── results/
│   └── logs/
├── config/                         # 配置檔案
│   ├── system_config.json
│   └── model_config.json
├── docs/                           # 文件
│   └── SOP_v1.md
└── requirements.txt                # Python 依賴清單
```

### 安裝步驟概要

**方案 A: Windows 原生環境（推薦）**

1. **環境準備**
   - 檢查 NVIDIA 驅動（已確認 576.02）
   - 檢查 CUDA（已確認 12.8）
   - 安裝 Miniconda for Windows（本地安裝）

2. **建立虛擬環境**
   ```powershell
   cd D:\NAS_Share\Data\08_Programming_Data(程式資料)\07_DEEPSEEK_OCR
   conda create -p .\.venv python=3.12.9 -y
   conda activate .\.venv
   ```

3. **安裝依賴**
   ```powershell
   # PyTorch + CUDA 12.x
   conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
   
   # 核心套件
   pip install transformers tokenizers
   pip install pillow accelerate safetensors
   
   # 選用：Flash Attention（若編譯失敗可跳過）
   pip install flash-attn --no-build-isolation
   
   # 選用：Web UI
   pip install gradio
   ```

4. **下載模型**
   ```powershell
   python scripts/download_model.py --output ./models/deepseek-ocr
   ```

5. **驗證安裝**
   ```powershell
   python scripts/test_ocr.py --image test_data/sample.png
   ```

**方案 B: WSL2 環境（備援，僅在必要時使用）**

僅在 Windows 原生環境遇到無法解決的問題時才使用此方案。詳細步驟見附錄。

### 配置管理

**system_config.json**:
```json
{
  "project_root": "D:\\NAS_Share\\Data\\...\\07_DEEPSEEK_OCR",
  "model_path": "./models/deepseek-ocr",
  "conda_env_path": "./.venv",
  "device": "cuda",
  "max_batch_size": 4,
  "vram_threshold": 0.9,
  "output_format": "markdown",
  "log_level": "INFO"
}
```

## Design Decisions and Rationale

### 1. 為何選擇 Windows 原生而非 WSL2？

**決策**: 使用 Windows 原生環境作為主要執行環境，WSL2 作為備援

**理由**:
- **硬體已完全支援**: CUDA 12.8、RTX 4060 驅動 576.02 在 Windows 上運作正常
- **使用者熟悉度**: 直接在 Windows 環境工作，無需學習 Linux 指令
- **檔案存取便利**: 不需要 `/mnt/d/` 路徑轉換，直接使用 Windows 路徑
- **工具整合**: VS Code、檔案總管、PowerShell 等工具直接使用
- **效能**: 少一層虛擬化，理論效能更好
- **PyTorch 支援**: 現代 PyTorch 版本對 Windows 支援已相當完善
- **Flash Attention 非必需**: 若編譯失敗可使用 Transformers 標準模式

**WSL2 備援情境**:
- Flash Attention 在 Windows 上無法編譯且必須使用
- 遇到特定套件僅支援 Linux 的情況
- 需要使用 vLLM 等 Linux-only 工具

### 2. 為何使用 Conda 而非 venv？

**決策**: 使用 Conda 管理虛擬環境

**理由**:
- Conda 可同時管理 Python 和系統級依賴（如 CUDA）
- 更容易安裝 PyTorch 的特定 CUDA 版本
- 支援本地環境安裝（`conda create -p`）
- 社群文件和支援更完整

### 3. 為何選擇 Flash Attention？

**決策**: 優先使用 Flash Attention 2.7.3

**理由**:
- 可大幅降低 VRAM 使用（約 30-40%）
- 加速推理速度（約 2-3 倍）
- DeepSeek-OCR 官方推薦配置
- 若編譯失敗，可降級使用 Transformers 標準模式

### 4. 批次處理策略

**決策**: 動態調整批次大小 + CPU fallback

**理由**:
- RTX 4060 僅 8GB VRAM，固定批次大小容易 OOM
- 動態監控 VRAM 使用率，自動調整批次
- CPU fallback 確保任務不會失敗（雖然較慢）
- 適合處理不同解析度的混合文件

### 5. 本地安裝策略

**決策**: 所有套件和模型安裝於專案目錄

**理由**:
- 避免污染全域 Python 環境
- 方便版本控制和環境複製
- 多專案可使用不同版本的依賴
- 符合使用者需求（不要全域安裝）

### 6. SOP 文件格式

**決策**: 使用 Markdown 格式撰寫 SOP

**理由**:
- 易於版本控制（Git）
- 可直接在 GitHub/GitLab 上閱讀
- 支援程式碼區塊和表格
- 可轉換為 PDF 或 HTML

## Performance Optimization

### VRAM 優化策略

1. **使用 bfloat16 精度**
   ```python
   model = model.to(torch.bfloat16)  # 減少 50% VRAM
   ```

2. **啟用 Gradient Checkpointing**（訓練時）
   ```python
   model.gradient_checkpointing_enable()
   ```

3. **動態批次大小**
   ```python
   def calculate_batch_size(vram_available):
       if vram_available > 6.0:
           return 8
       elif vram_available > 4.0:
           return 4
       else:
           return 2
   ```

### 推理速度優化

1. **使用 vLLM 引擎**（批次處理時）
2. **預載入模型**（避免重複載入）
3. **圖片預處理快取**
4. **多執行緒 I/O**（讀取圖片時）

### 監控指標

- GPU 使用率（目標 > 80%）
- VRAM 使用率（目標 < 90%）
- 推理延遲（目標 < 5 秒/張）
- 吞吐量（目標 > 720 張/小時）
