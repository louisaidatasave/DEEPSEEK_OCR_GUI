# Requirements Document

## Introduction

本文件定義 DeepSeek OCR 本地部署 V1 版本的需求規格。目標是在 MSI 筆電（AMD Ryzen 7 8845HS、64GB RAM、NVIDIA RTX 4060 8GB VRAM）上建立一套完整的 OCR 部署流程，包含環境設定、模型安裝、測試驗證及標準作業程序（SOP）文件。

## Glossary

- **DeepSeek-OCR**: DeepSeek-AI 開發的開源 OCR 模型，專注於視覺上下文壓縮和文檔理解
- **WSL2**: Windows Subsystem for Linux 2，Windows 上的 Linux 子系統
- **VRAM**: Video Random Access Memory，顯示記憶體
- **Flash Attention**: 用於加速 Transformer 模型注意力機制的優化技術
- **vLLM**: 高效能大型語言模型推理引擎
- **Conda**: Python 環境和套件管理系統
- **CUDA**: NVIDIA 的平行運算平台和 API
- **SOP**: Standard Operating Procedure，標準作業程序

## Requirements

### Requirement 1: 環境準備與驗證

**User Story:** 作為系統管理員，我希望能夠驗證硬體環境並準備必要的軟體工具，以確保系統符合 DeepSeek-OCR 的運行需求。

#### Acceptance Criteria

1. WHEN 執行硬體檢查指令時，THE System SHALL 顯示 NVIDIA RTX 4060 顯卡資訊及驅動版本（≥535）
2. WHEN 檢查 CUDA 版本時，THE System SHALL 回報 CUDA 11.8 或 12.x 版本已正確安裝
3. WHEN 驗證系統記憶體時，THE System SHALL 確認可用 RAM 達到 60GB 以上
4. WHEN 檢查 Windows 環境時，THE System SHALL 確認 Miniconda 已安裝並可執行 conda 指令
5. THE System SHALL 安裝 Anaconda 或 Miniconda 並可執行 conda 指令

### Requirement 2: Python 環境建立

**User Story:** 作為開發者，我希望建立獨立的 Python 虛擬環境，以避免套件衝突並確保版本一致性。

#### Acceptance Criteria

1. WHEN 建立 Conda 環境時，THE System SHALL 使用 Python 3.12.9 版本
2. WHEN 啟動虛擬環境時，THE System SHALL 正確切換到 deepseek-ocr 環境
3. WHEN 安裝 PyTorch 時，THE System SHALL 安裝 PyTorch 搭配 CUDA 12.x 支援（相容現有 CUDA 12.8）
4. WHEN 驗證 GPU 可用性時，THE System SHALL 回報 torch.cuda.is_available() 為 True
5. THE System SHALL 安裝 transformers 4.46.3、tokenizers 0.20.3 及相關依賴套件

### Requirement 3: DeepSeek-OCR 模型部署

**User Story:** 作為 AI 工程師，我希望能夠下載並部署 DeepSeek-OCR 模型，以便進行文字辨識任務。

#### Acceptance Criteria

1. WHEN 克隆 GitHub 倉庫時，THE System SHALL 成功下載 DeepSeek-OCR 專案程式碼
2. WHEN 下載模型權重時，THE System SHALL 從 Hugging Face 取得完整的模型檔案（約 6.67GB）
3. WHEN 嘗試安裝 Flash Attention 時，THE System SHALL 嘗試編譯並安裝 flash-attn（選用加速組件）
4. IF Flash Attention 編譯失敗，THEN THE System SHALL 自動使用 transformers 標準模式並通知使用者
5. THE System SHALL 將模型檔案儲存於指定的本地目錄

### Requirement 4: 基礎推理測試

**User Story:** 作為測試人員，我希望能夠執行單張圖片的 OCR 測試，以驗證模型部署成功且功能正常。

#### Acceptance Criteria

1. WHEN 載入測試圖片時，THE System SHALL 支援 PNG、JPG、JPEG 等常見圖片格式
2. WHEN 執行 OCR 推理時，THE System SHALL 在 10 秒內完成單張圖片的文字辨識
3. WHEN 輸出辨識結果時，THE System SHALL 以 Markdown 格式呈現文字內容
4. WHEN 處理中文文字時，THE System SHALL 正確辨識繁體中文字元
5. THE System SHALL 記錄推理時間、GPU 記憶體使用量及辨識準確度

### Requirement 5: 批次處理能力

**User Story:** 作為使用者，我希望能夠批次處理多張圖片或 PDF 文件，以提高工作效率。

#### Acceptance Criteria

1. WHEN 處理多張圖片時，THE System SHALL 採用逐頁處理模式以避免 VRAM 溢位
2. WHEN 處理 PDF 文件時，THE System SHALL 先將 PDF 轉換為圖片後再進行 OCR
3. WHILE VRAM 使用率超過 90% 時，THE System SHALL 自動調整批次大小或啟用 CPU fallback
4. WHEN 批次處理完成時，THE System SHALL 輸出所有頁面的辨識結果並儲存為單一檔案
5. THE System SHALL 支援處理最多 100 頁的文件而不發生記憶體錯誤

### Requirement 6: Web UI 介面（選用功能）

**User Story:** 作為非技術使用者，我希望透過網頁介面上傳圖片並取得 OCR 結果，而不需要使用命令列。

#### Acceptance Criteria

1. WHEN 啟動 Web UI 時，THE System SHALL 在 localhost:7860 提供可存取的網頁介面
2. WHEN 上傳圖片時，THE System SHALL 接受拖放或點選上傳的操作方式
3. WHEN 辨識完成時，THE System SHALL 在網頁上即時顯示辨識結果
4. WHERE Web UI 功能啟用時，THE System SHALL 支援同時處理多個使用者請求
5. THE System SHALL 提供下載辨識結果為文字檔的功能

### Requirement 7: 效能監控與優化

**User Story:** 作為系統管理員，我希望能夠監控系統效能並進行優化，以確保穩定運行。

#### Acceptance Criteria

1. WHEN 執行 OCR 任務時，THE System SHALL 記錄 GPU 使用率、VRAM 佔用及處理時間
2. WHEN VRAM 不足時，THE System SHALL 提供降低解析度或使用量化模型的建議
3. WHEN 處理速度低於預期時，THE System SHALL 檢查並回報可能的瓶頸原因
4. THE System SHALL 在單張圖片處理時間超過 30 秒時發出警告
5. THE System SHALL 提供效能報告，包含平均處理時間、成功率及錯誤日誌

### Requirement 8: SOP 文件產出

**User Story:** 作為文件管理員，我希望產出完整的 SOP 文件，以便團隊成員能夠依循標準流程進行部署和操作。

#### Acceptance Criteria

1. THE System SHALL 產出包含環境準備、安裝步驟、測試驗證的完整 SOP 文件
2. THE SOP Document SHALL 包含每個步驟的預期輸出和錯誤排除指引
3. THE SOP Document SHALL 提供 Windows 原生環境的操作指令（PowerShell/CMD），並在附錄提供 WSL2 備援方案
4. THE SOP Document SHALL 包含硬體需求、軟體版本及相依性清單
5. THE SOP Document SHALL 以 Markdown 格式撰寫並包含目錄、圖表及範例程式碼

### Requirement 9: 錯誤處理與疑難排解

**User Story:** 作為支援人員，我希望系統能夠提供清楚的錯誤訊息和解決方案，以快速排除問題。

#### Acceptance Criteria

1. WHEN CUDA 無法偵測時，THE System SHALL 提供驅動安裝和環境變數設定的指引
2. WHEN Flash Attention 編譯失敗時，THE System SHALL 自動切換到相容模式並通知使用者
3. WHEN 模型下載失敗時，THE System SHALL 提供鏡像站點或手動下載的替代方案
4. WHEN 記憶體不足錯誤發生時，THE System SHALL 建議調整批次大小或圖片解析度
5. THE System SHALL 記錄所有錯誤訊息並提供對應的疑難排解步驟

### Requirement 10: 版本控制與更新機制

**User Story:** 作為維護人員，我希望能夠追蹤系統版本並進行更新，以確保使用最新的功能和修正。

#### Acceptance Criteria

1. THE System SHALL 記錄當前安裝的 DeepSeek-OCR 版本、PyTorch 版本及 CUDA 版本
2. WHEN 檢查更新時，THE System SHALL 比對本地版本與官方最新版本
3. WHEN 執行更新時，THE System SHALL 備份現有環境設定和模型檔案
4. THE System SHALL 提供版本回退機制以因應更新失敗的情況
5. THE System SHALL 在 SOP 文件中註明版本資訊和更新日期
