# Poppler 安裝指南（Windows）

## 什麼是 Poppler？

Poppler 是一個 PDF 渲染工具，`pdf2image` Python 套件需要它來轉換 PDF 為圖片。

---

## 🚀 快速安裝（推薦）

### 方法 1：使用 Chocolatey（最簡單）

如果你有 Chocolatey 套件管理器：

```powershell
# 以管理員身份執行 PowerShell
choco install poppler
```

### 方法 2：手動安裝

#### 步驟 1：下載 Poppler

訪問：https://github.com/oschwartz10612/poppler-windows/releases/

下載最新版本的 `Release-XX.XX.X-0.zip`（例如：`Release-24.08.0-0.zip`）

#### 步驟 2：解壓縮

解壓到：`C:\Program Files\poppler\`

目錄結構應該是：
```
C:\Program Files\poppler\
├── Library\
│   └── bin\          ← 這個目錄包含 pdftoppm.exe
│       ├── pdftoppm.exe
│       ├── pdfinfo.exe
│       └── ...
└── ...
```

#### 步驟 3：加入系統 PATH

**方法 A：圖形界面**
1. 右鍵「本機」→「內容」
2. 點擊「進階系統設定」
3. 點擊「環境變數」
4. 在「系統變數」區域找到「Path」
5. 點擊「編輯」
6. 點擊「新增」
7. 輸入：`C:\Program Files\poppler\Library\bin`
8. 點擊「確定」關閉所有視窗

**方法 B：PowerShell（管理員）**
```powershell
# 永久加入 PATH
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "Machine") + ";C:\Program Files\poppler\Library\bin",
    "Machine"
)
```

#### 步驟 4：驗證安裝

**重新開啟 PowerShell**（重要！），然後執行：

```powershell
pdftoppm -v
```

應該顯示類似：
```
pdftoppm version 24.08.0
Copyright 2005-2024 The Poppler Developers - http://poppler.freedesktop.org
...
```

---

## 🧪 測試 PDF 功能

安裝完成後，測試 PDF 轉換：

```powershell
# 啟動虛擬環境
.\.venv\Scripts\Activate.ps1

# 測試 PDF 轉換
python -c "from pdf2image import convert_from_path; print('PDF 轉換功能可用！')"
```

如果沒有錯誤，表示安裝成功！

---

## ❓ 疑難排解

### 問題 1：找不到 pdftoppm

**錯誤訊息**：
```
Unable to get page count. Is poppler installed and in PATH?
```

**解決方法**：
1. 確認 `C:\Program Files\poppler\Library\bin\pdftoppm.exe` 存在
2. 確認 PATH 已正確設定
3. **重新開啟 PowerShell**（重要！）
4. 執行 `pdftoppm -v` 驗證

### 問題 2：權限不足

**解決方法**：
- 以管理員身份執行 PowerShell
- 或將 Poppler 安裝到使用者目錄（例如：`C:\Users\你的使用者名稱\poppler\`）

### 問題 3：PATH 沒有生效

**解決方法**：
1. 完全關閉所有 PowerShell 視窗
2. 重新開啟 PowerShell
3. 執行 `$env:PATH` 檢查是否包含 Poppler 路徑

---

## 🔄 臨時使用（不修改 PATH）

如果不想修改系統 PATH，可以在每次使用前設定：

```powershell
# 在 PowerShell 中設定（僅當前會話有效）
$env:PATH += ";C:\Program Files\poppler\Library\bin"

# 然後啟動 GUI
python scripts/gui_app.py
```

---

## 📝 驗證清單

安裝完成後，確認以下項目：

- [ ] Poppler 已下載並解壓
- [ ] `pdftoppm.exe` 存在於 `Library\bin\` 目錄
- [ ] PATH 環境變數已更新
- [ ] 重新開啟 PowerShell
- [ ] `pdftoppm -v` 顯示版本資訊
- [ ] Python 測試通過
- [ ] GUI 的 PDF 功能可用

---

## 🎯 完成後

安裝完成後，DeepSeek-OCR 的 PDF 處理功能就可以正常使用了！

在 GUI 中：
1. 點擊「PDF 處理」頁籤
2. 選擇 PDF 檔案
3. 設定頁碼範圍
4. 點擊「開始處理」

應該就能正常轉換和處理 PDF 了！
