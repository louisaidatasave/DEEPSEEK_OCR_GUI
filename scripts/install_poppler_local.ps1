# 本地安裝 Poppler 腳本
# 將 Poppler 安裝到專案目錄，不影響系統全域設定

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Poppler 本地安裝工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 設定本地安裝目錄
$LocalDir = ".\tools\poppler"
$DownloadUrl = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip"
$ZipFile = ".\tools\poppler.zip"

Write-Host "安裝位置: $LocalDir" -ForegroundColor Green
Write-Host "下載來源: $DownloadUrl" -ForegroundColor Green
Write-Host ""

# 建立目錄
Write-Host "[1/4] 建立目錄..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path ".\tools" -Force | Out-Null
Write-Host "  ✓ 目錄已建立" -ForegroundColor Green

# 下載 Poppler
Write-Host "[2/4] 下載 Poppler..." -ForegroundColor Yellow
Write-Host "  下載中... (約 20 MB)" -ForegroundColor Gray

try {
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ZipFile -UseBasicParsing
    Write-Host "  ✓ 下載完成" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 下載失敗: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "請手動下載:" -ForegroundColor Yellow
    Write-Host "  1. 訪問: https://github.com/oschwartz10612/poppler-windows/releases/" -ForegroundColor Gray
    Write-Host "  2. 下載最新的 Release-XX.XX.X-0.zip" -ForegroundColor Gray
    Write-Host "  3. 解壓到: $LocalDir" -ForegroundColor Gray
    exit 1
}

# 解壓縮
Write-Host "[3/4] 解壓縮..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $ZipFile -DestinationPath ".\tools" -Force
    
    # 重新命名目錄
    $ExtractedDir = Get-ChildItem ".\tools" -Directory | Where-Object { $_.Name -like "poppler-*" } | Select-Object -First 1
    if ($ExtractedDir) {
        if (Test-Path $LocalDir) {
            Remove-Item -Recurse -Force $LocalDir
        }
        Move-Item $ExtractedDir.FullName $LocalDir
    }
    
    Write-Host "  ✓ 解壓完成" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 解壓失敗: $_" -ForegroundColor Red
    exit 1
}

# 清理下載檔案
Remove-Item $ZipFile -Force

# 驗證安裝
Write-Host "[4/4] 驗證安裝..." -ForegroundColor Yellow
$PopplerBin = Join-Path $LocalDir "Library\bin\pdftoppm.exe"

if (Test-Path $PopplerBin) {
    Write-Host "  ✓ Poppler 已安裝" -ForegroundColor Green
    Write-Host "  位置: $PopplerBin" -ForegroundColor Gray
    
    # 測試執行
    $Version = & $PopplerBin -v 2>&1 | Select-Object -First 1
    Write-Host "  版本: $Version" -ForegroundColor Gray
} else {
    Write-Host "  ✗ 找不到 pdftoppm.exe" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ 安裝完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Poppler 已安裝到專案本地目錄" -ForegroundColor Green
Write-Host "不會影響系統全域設定" -ForegroundColor Green
Write-Host ""

Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "  1. 執行: python scripts/setup_poppler_path.py" -ForegroundColor Gray
Write-Host "  2. 或直接啟動 GUI（會自動設定）" -ForegroundColor Gray
Write-Host ""
