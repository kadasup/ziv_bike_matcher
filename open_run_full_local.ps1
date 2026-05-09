param(
  [int]$Port = 8765
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Get-Command py -ErrorAction SilentlyContinue
if (-not $py) {
  Write-Error "找不到 py (Python Launcher)，請先安裝 Python。"
}

$url = "http://127.0.0.1:$Port/run_full_gallery.html"

# 啟動背景 http server
Start-Process -FilePath "py" -ArgumentList "-m http.server $Port --directory `"$root`"" -WorkingDirectory $root -WindowStyle Hidden

Start-Sleep -Milliseconds 800
Start-Process $url
Write-Host "已啟動：$url"
Write-Host "關閉伺服器：在工作管理員結束 python.exe，或重開機器後自動消失。"
