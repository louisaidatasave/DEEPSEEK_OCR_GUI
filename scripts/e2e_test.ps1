# DeepSeek-OCR 端到端測試腳本 (PowerShell)
# 執行完整流程測試：環境檢查 → 模型載入 → OCR 測試 → 批次處理

$ErrorActionPreference = "Continue"
$TestsPassed = 0
$TestsFailed = 0
$TestResults = @()

function Write-TestHeader {
    param($Title)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Write-TestResult {
    param($TestName, $Success, $Message = "")
    
    if ($Success) {
        Write-Host "✓ $TestName" -ForegroundColor Green
        $script:TestsPassed++
        $script:TestResults += @{Name=$TestName; Status="PASS"; Message=$Message}
    } else {
        Write-Host "✗ $TestName" -ForegroundColor Red
        if ($Message) {
            Write-Host "  錯誤: $Message" -ForegroundColor Yellow
        }
        $script:TestsFailed++
        $script:TestResults += @{Name=$TestName; Status="FAIL"; Message=$Message}
    }
}

# 啟動虛擬環境
Write-Host "啟動虛擬環境..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# ==================== 測試 1: 環境檢查 ====================
Write-TestHeader "測試 1: 環境檢查"

# 1.1 Python 版本
Write-Host "檢查 Python 版本..." -ForegroundColor Yellow
$PythonVersion = python --version 2>&1
if ($PythonVersion -match "Python 3\.12") {
    Write-TestResult "Python 版本" $true $PythonVersion
} else {
    Write-TestResult "Python 版本" $false "預期 Python 3.12.x，實際: $PythonVersion"
}

# 1.2 硬體檢查
Write-Host "檢查硬體..." -ForegroundColor Yellow
$HardwareCheck = python scripts/check_hardware.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-TestResult "硬體檢查" $true
} else {
    Write-TestResult "硬體檢查" $false "硬體檢查失敗"
}

# 1.3 GPU 驗證
Write-Host "驗證 GPU..." -ForegroundColor Yellow
$GPUCheck = python scripts/verify_gpu.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-TestResult "GPU 可用性" $true
} else {
    Write-TestResult "GPU 可用性" $false "GPU 驗證失敗"
}

# ==================== 測試 2: 模型驗證 ====================
Write-TestHeader "測試 2: 模型驗證"

# 2.1 模型檔案存在
Write-Host "檢查模型檔案..." -ForegroundColor Yellow
if (Test-Path "models/deepseek-ocr") {
    Write-TestResult "模型目錄存在" $true
    
    # 2.2 模型驗證
    Write-Host "驗證模型完整性..." -ForegroundColor Yellow
    $ModelCheck = python scripts/validate_model.py 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-TestResult "模型完整性" $true
    } else {
        Write-TestResult "模型完整性" $false "模型驗證失敗"
    }
} else {
    Write-TestResult "模型目錄存在" $false "模型目錄不存在"
    Write-TestResult "模型完整性" $false "跳過（模型不存在）"
}

# ==================== 測試 3: 模組測試 ====================
Write-TestHeader "測試 3: 模組測試"

# 3.1 圖片處理模組
Write-Host "測試圖片處理模組..." -ForegroundColor Yellow
$ImageProcessorTest = python scripts/test_image_processor.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-TestResult "圖片處理模組" $true
} else {
    Write-TestResult "圖片處理模組" $false
}

# 3.2 記憶體管理模組
Write-Host "測試記憶體管理模組..." -ForegroundColor Yellow
$MemoryManagerTest = python scripts/test_memory_manager.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-TestResult "記憶體管理模組" $true
} else {
    Write-TestResult "記憶體管理模組" $false
}

# 3.3 PDF 轉換模組
Write-Host "測試 PDF 轉換模組..." -ForegroundColor Yellow
$PDFConverterTest = python scripts/test_pdf_converter.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-TestResult "PDF 轉換模組" $true
} else {
    Write-TestResult "PDF 轉換模組" $false
}

# 3.4 效能追蹤模組
Write-Host "測試效能追蹤模組..." -ForegroundColor Yellow
$PerformanceTest = python scripts/test_performance.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-TestResult "效能追蹤模組" $true
} else {
    Write-TestResult "效能追蹤模組" $false
}

# ==================== 測試 4: OCR 功能測試 ====================
Write-TestHeader "測試 4: OCR 功能測試"

# 檢查是否有測試圖片
$TestImages = Get-ChildItem -Path "." -Include "*.png","*.jpg","*.jpeg" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1

if ($TestImages) {
    $TestImage = $TestImages[0].FullName
    Write-Host "使用測試圖片: $($TestImages[0].Name)" -ForegroundColor Yellow
    
    # 4.1 單張圖片 OCR
    Write-Host "測試單張圖片 OCR..." -ForegroundColor Yellow
    $OCRTest = python scripts/test_ocr.py $TestImage --output outputs/e2e_test 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-TestResult "單張圖片 OCR" $true
    } else {
        Write-TestResult "單張圖片 OCR" $false
    }
} else {
    Write-Host "找不到測試圖片，跳過 OCR 測試" -ForegroundColor Yellow
    Write-TestResult "單張圖片 OCR" $false "找不到測試圖片"
}

# ==================== 測試 5: 配置與工具 ====================
Write-TestHeader "測試 5: 配置與工具"

# 5.1 配置檔案
Write-Host "檢查配置檔案..." -ForegroundColor Yellow
if (Test-Path "config/system_config.json") {
    Write-TestResult "配置檔案存在" $true
    
    # 測試配置載入
    $ConfigTest = python -c "from src.config_loader import get_config; c = get_config(); print('OK')" 2>&1
    if ($ConfigTest -match "OK") {
        Write-TestResult "配置載入" $true
    } else {
        Write-TestResult "配置載入" $false
    }
} else {
    Write-TestResult "配置檔案存在" $false
    Write-TestResult "配置載入" $false "配置檔案不存在"
}

# 5.2 版本資訊
Write-Host "檢查版本資訊..." -ForegroundColor Yellow
$VersionTest = python -c "from src.version_info import get_version_string; print(get_version_string())" 2>&1
if ($VersionTest -match "DeepSeek-OCR") {
    Write-TestResult "版本資訊" $true $VersionTest
} else {
    Write-TestResult "版本資訊" $false
}

# 5.3 日誌系統
Write-Host "測試日誌系統..." -ForegroundColor Yellow
$LogTest = python -c "from src.logger import setup_logger; logger = setup_logger(); logger.info('Test'); print('OK')" 2>&1
if ($LogTest -match "OK") {
    Write-TestResult "日誌系統" $true
} else {
    Write-TestResult "日誌系統" $false
}

# ==================== 測試總結 ====================
Write-TestHeader "測試總結"

$TotalTests = $TestsPassed + $TestsFailed
$PassRate = if ($TotalTests -gt 0) { ($TestsPassed / $TotalTests * 100) } else { 0 }

Write-Host ""
Write-Host "總測試數: $TotalTests" -ForegroundColor Cyan
Write-Host "通過: $TestsPassed" -ForegroundColor Green
Write-Host "失敗: $TestsFailed" -ForegroundColor Red
Write-Host "通過率: $([math]::Round($PassRate, 2))%" -ForegroundColor $(if ($PassRate -ge 80) { "Green" } else { "Yellow" })
Write-Host ""

# 輸出詳細結果
Write-Host "詳細結果:" -ForegroundColor Cyan
foreach ($Result in $TestResults) {
    $StatusColor = if ($Result.Status -eq "PASS") { "Green" } else { "Red" }
    Write-Host "  [$($Result.Status)]" -ForegroundColor $StatusColor -NoNewline
    Write-Host " $($Result.Name)" -ForegroundColor Gray
    if ($Result.Message) {
        Write-Host "    → $($Result.Message)" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# 匯出測試報告
$ReportPath = "outputs/e2e_test_report.json"
$Report = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    total_tests = $TotalTests
    passed = $TestsPassed
    failed = $TestsFailed
    pass_rate = $PassRate
    results = $TestResults
}

New-Item -ItemType Directory -Path "outputs" -Force | Out-Null
$Report | ConvertTo-Json -Depth 10 | Out-File $ReportPath -Encoding UTF8

Write-Host "測試報告已儲存至: $ReportPath" -ForegroundColor Green
Write-Host ""

# 返回結果
if ($TestsFailed -eq 0) {
    Write-Host "✓ 所有測試通過！" -ForegroundColor Green
    exit 0
} else {
    Write-Host "✗ 部分測試失敗，請檢查上方錯誤訊息" -ForegroundColor Red
    exit 1
}
