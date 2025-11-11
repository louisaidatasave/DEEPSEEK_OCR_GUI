# 變更記錄

## 2025-11-01 - 部署策略調整

### 重大變更：從 WSL2 優先改為 Windows 原生優先

**變更原因**：
- 硬體環境檢查確認 Windows 環境完全支援（CUDA 12.8、RTX 4060、驅動 576.02）
- 使用者偏好在熟悉的 Windows 環境工作
- 現代 PyTorch 對 Windows 支援已相當完善
- 減少學習曲線和環境複雜度

### 具體變更

#### 1. Design Document (design.md)
- ✅ 更新 Overview：明確標示 Windows 原生優先
- ✅ 更新系統架構圖：新增方案 A（Windows）和方案 B（WSL2 備援）
- ✅ 更新技術堆疊：CUDA 12.x、Flash Attention 改為選用
- ✅ 更新設計決策：說明選擇 Windows 原生的理由
- ✅ 更新安裝步驟：提供 PowerShell 指令

#### 2. Requirements Document (requirements.md)
- ✅ REQ-1.4：從「檢查 WSL2」改為「檢查 Windows 環境和 Miniconda」
- ✅ REQ-2.3：從「CUDA 11.8」改為「CUDA 12.x（相容 12.8）」
- ✅ REQ-3.3/3.4：Flash Attention 改為選用，編譯失敗自動降級
- ✅ REQ-8.3：SOP 文件以 Windows 為主，WSL2 放附錄

#### 3. Tasks Document (tasks.md)
- ✅ Task 1.2：從「WSL2 設定」改為「Windows 環境驗證」
- ✅ Task 1.3：Conda 腳本改為 `.bat` 或 `.ps1` 格式
- ✅ Task 2.1：依賴安裝腳本改為 Windows 版本
- ✅ Task 8.4：備份腳本改為 Windows 版本
- ✅ Task 9.2：環境準備章節以 Windows 為主
- ✅ Task 10.1：E2E 測試腳本改為 Windows 版本

### 保留的彈性

- WSL2 仍作為備援方案，在以下情況使用：
  1. Flash Attention 在 Windows 無法編譯且必須使用
  2. 特定套件僅支援 Linux
  3. 需要使用 vLLM 等 Linux-only 工具

### 下一步行動

- ✅ Task 1.1 已完成：硬體檢查腳本（Windows 原生）
- ⏭️ Task 1.2 進行中：建立 Windows 環境驗證腳本
- 後續所有腳本將優先使用 Python（跨平台）或 PowerShell（Windows）

### 技術影響評估

**優點**：
- 減少環境複雜度
- 使用者體驗更好
- 檔案路徑更直觀
- 工具整合更順暢

**風險**：
- Flash Attention 可能無法在 Windows 編譯
  - 緩解：使用 Transformers 標準模式（已驗證可行）
- 部分套件可能有 Windows 特定問題
  - 緩解：優先使用跨平台套件，問題時切換 WSL2

**結論**：風險可控，收益明顯，決策正確。
