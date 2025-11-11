# DeepSeek-OCR 環境備份腳本 (PowerShell)
# 備份虛擬環境配置和系統設定

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DeepSeek-OCR 環境備份工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 設定備份目錄
$BackupDir = "backups\env_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

Write-Host "備份目錄: $BackupDir" -ForegroundColor Green
Write-Host ""

# 1. 備份 requirements.txt
Write-Host "[1/6] 備份套件清單..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    Copy-Item "requirements.txt" "$BackupDir\requirements.txt"
    Write-Host "  ✓ requirements.txt 已備份" -ForegroundColor Green
} else {
    Write-Host "  ! requirements.txt 不存在，嘗試生成..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
    pip freeze > "$BackupDir\requirements.txt"
    Write-Host "  ✓ 已生成並備份 requirements.txt" -ForegroundColor Green
}

# 2. 備份配置檔案
Write-Host "[2/6] 備份配置檔案..." -ForegroundColor Yellow
if (Test-Path "config") {
    Copy-Item -Path "config" -Destination "$BackupDir\config" -Recurse -Force
    Write-Host "  ✓ config/ 已備份" -ForegroundColor Green
} else {
    Write-Host "  ! config/ 目錄不存在" -ForegroundColor Yellow
}

# 3. 備份環境變數
Write-Host "[3/6] 備份環境變數..." -ForegroundColor Yellow
$EnvVars = @{
    "PATH" = $env:PATH
    "PYTHONPATH" = $env:PYTHONPATH
    "CUDA_VISIBLE_DEVICES" = $env:CUDA_VISIBLE_DEVICES
}
$EnvVars | ConvertTo-Json | Out-File "$BackupDir\environment_variables.json" -Encoding UTF8
Write-Host "  ✓ 環境變數已備份" -ForegroundColor Green

# 4. 備份系統資訊
Write-Host "[4/6] 備份系統資訊..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
python -c "import sys; import platform; import json; info={'python_version': sys.version, 'platform': platform.platform(), 'architecture': platform.machine()}; print(json.dumps(info, indent=2))" > "$BackupDir\system_info.json"
Write-Host "  ✓ 系統資訊已備份" -ForegroundColor Green

# 5. 備份版本資訊
Write-Host "[5/6] 備份版本資訊..." -ForegroundColor Yellow
if (Test-Path "src\version_info.py") {
    python -c "import sys; sys.path.insert(0, '.'); from src.version_info import get_all_versions; import json; print(json.dumps(get_all_versions(), indent=2, ensure_ascii=False))" > "$BackupDir\version_info.json"
    Write-Host "  ✓ 版本資訊已備份" -ForegroundColor Green
} else {
    Write-Host "  ! version_info.py 不存在" -ForegroundColor Yellow
}

# 6. 建立還原說明
Write-Host "[6/6] 建立還原說明..." -ForegroundColor Yellow
$RestoreInstructions = @"
# DeepSeek-OCR 環境還原說明

## 備份時間
$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## 還原步驟

### 1. 建立虛擬環境
``````powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
``````

### 2. 安裝套件
``````powershell
pip install -r requirements.txt
``````

### 3. 還原配置檔案
``````powershell
Copy-Item -Path config -Destination ..\ -Recurse -Force
``````

### 4. 驗證安裝
``````powershell
python scripts/verify_gpu.py
python -c "from src.version_info import print_version_info; print_version_info()"
``````

## 備份內容
- requirements.txt: Python 套件清單
- config/: 配置檔案
- environment_variables.json: 環境變數
- system_info.json: 系統資訊
- version_info.json: 版本資訊

## 注意事項
1. 確保 Python 版本一致
2. 確保 CUDA 版本相容
3. 模型檔案需要另外備份（位於 models/ 目錄）
"@

$RestoreInstructions | Out-File "$BackupDir\RESTORE.md" -Encoding UTF8
Write-Host "  ✓ 還原說明已建立" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ 備份完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "備份位置: $BackupDir" -ForegroundColor Green
Write-Host ""
Write-Host "備份內容:" -ForegroundColor Yellow
Get-ChildItem $BackupDir -Recurse | ForEach-Object {
    Write-Host "  - $($_.FullName.Replace((Get-Location).Path + '\', ''))" -ForegroundColor Gray
}
Write-Host ""
Write-Host "請查看 $BackupDir\RESTORE.md 了解還原步驟" -ForegroundColor Cyan
