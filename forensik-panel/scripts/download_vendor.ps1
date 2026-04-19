# Vendor kutuphanelerini indir - CDN YERINE YEREL
# Windows PowerShell'de calistirilir:
#   powershell -ExecutionPolicy Bypass -File scripts\download_vendor.ps1

$ErrorActionPreference = "Stop"
$PROJECT = Split-Path -Parent $PSScriptRoot
$VENDOR = Join-Path $PROJECT "versions\v1\static\vendor"

Write-Host "==> Vendor klasoru: $VENDOR"
New-Item -ItemType Directory -Force -Path $VENDOR | Out-Null

# ========== MONACO EDITOR ==========
$monacoDir = Join-Path $VENDOR "monaco"
$monacoLoader = Join-Path $monacoDir "min\vs\loader.js"

if (-not (Test-Path $monacoLoader)) {
    Write-Host "==> Monaco Editor indiriliyor (~12 MB)..."

    $tmpDir = Join-Path $env:TEMP "monaco-dl-$(Get-Random)"
    New-Item -ItemType Directory -Path $tmpDir | Out-Null

    Push-Location $tmpDir
    try {
        Invoke-WebRequest `
            -Uri "https://registry.npmjs.org/monaco-editor/-/monaco-editor-0.47.0.tgz" `
            -OutFile "monaco.tgz" `
            -UseBasicParsing

        tar -xzf monaco.tgz

        New-Item -ItemType Directory -Force -Path $monacoDir | Out-Null
        if (Test-Path (Join-Path $monacoDir "min")) {
            Remove-Item (Join-Path $monacoDir "min") -Recurse -Force
        }
        Copy-Item "package\min" $monacoDir -Recurse -Force

        Write-Host "    Monaco indirildi"
    } finally {
        Pop-Location
        Remove-Item $tmpDir -Recurse -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "==> Monaco zaten var, atlaniyor"
}

# ========== TABULATOR ==========
$tabDir = Join-Path $VENDOR "tabulator"
$tabJs = Join-Path $tabDir "tabulator.min.js"

if (-not (Test-Path $tabJs)) {
    Write-Host "==> Tabulator indiriliyor..."
    New-Item -ItemType Directory -Force -Path $tabDir | Out-Null

    Invoke-WebRequest `
        -Uri "https://cdn.jsdelivr.net/npm/tabulator-tables@5.5.4/dist/js/tabulator.min.js" `
        -OutFile $tabJs `
        -UseBasicParsing

    Invoke-WebRequest `
        -Uri "https://cdn.jsdelivr.net/npm/tabulator-tables@5.5.4/dist/css/tabulator.min.css" `
        -OutFile (Join-Path $tabDir "tabulator.min.css") `
        -UseBasicParsing

    Write-Host "    Tabulator indirildi"
} else {
    Write-Host "==> Tabulator zaten var"
}

# ========== TAILWIND (standalone CLI) ==========
$scriptsDir = Join-Path $PROJECT "scripts"
$twCli = Join-Path $scriptsDir "tailwindcss.exe"
if (-not (Test-Path $twCli)) {
    Write-Host "==> Tailwind CLI indiriliyor..."
    Invoke-WebRequest `
        -Uri "https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-windows-x64.exe" `
        -OutFile $twCli `
        -UseBasicParsing
    Write-Host "    Tailwind CLI indirildi"
}

# Tailwind derle
$v1Dir = Join-Path $PROJECT "versions\v1"
$tailwindSrc = Join-Path $v1Dir "static\css\tailwind_src.css"

if (-not (Test-Path $tailwindSrc)) {
@"
@tailwind base;
@tailwind components;
@tailwind utilities;
"@ | Out-File $tailwindSrc -Encoding UTF8
}

$tailwindConfig = Join-Path $v1Dir "tailwind.config.js"
if (-not (Test-Path $tailwindConfig)) {
@"
module.exports = {
  content: ['./templates/**/*.html', './routes/**/*.py'],
  theme: { extend: {} },
}
"@ | Out-File $tailwindConfig -Encoding UTF8
}

Write-Host "==> Tailwind CSS derleniyor..."
Push-Location $v1Dir
try {
    $inPath = "static\css\tailwind_src.css"
    $outPath = "static\css\tailwind.min.css"
    & $twCli -i $inPath -o $outPath --minify
    Write-Host "    tailwind.min.css olusturuldu"
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "TUM VENDOR INDIRILDI" -ForegroundColor Green
$size = (Get-ChildItem $VENDOR -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host ("Toplam boyut: {0:N1} MB" -f ($size / 1MB))
