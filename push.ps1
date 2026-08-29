# 一键上传脚本：开代理后运行此脚本，即可把 D:\Dustar_code 改动推送到 GitHub
# 用法（PowerShell 中）：
#   .\push.ps1              -> 用默认提交信息 "update"
#   .\push.ps1 -msg "fix bug"  -> 自定义提交信息（建议用英文，避免中文乱码）

param([string]$msg = "update")

# 临时走代理（只在当前脚本进程生效，不污染全局配置）
$env:HTTP_PROXY  = "http://127.0.0.1:7897"
$env:HTTPS_PROXY = "http://127.0.0.1:7897"

Set-Location "D:\Dustar_code"

git add -A
git commit -m $msg
git push origin main

Write-Output "--- 完成，退出码 $LASTEXITCODE ---"
