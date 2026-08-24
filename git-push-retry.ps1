<#
.SYNOPSIS
  重试式 git push，专治国内网络环境下 GitHub push 遇到的 curl 52 / 55 连接重置、443 超时。
.DESCRIPTION
  - 每次 push 前强制 HTTP/1.1 + 放大 postBuffer（这两项是绕开连接重置的关键）。
  - 失败自动重试，最多 MaxTries 次，间隔 Delay 秒。
  - 成功立即退出；全部失败返回非 0。
.PARAMETER Remote
  远程名，默认 origin
.PARAMETER Branch
  分支名，默认 main
.PARAMETER MaxTries
  最大重试次数，默认 10
.PARAMETER Delay
  每次失败后的等待秒数，默认 3
.EXAMPLE
  .\git-push-retry.ps1
  .\git-push-retry.ps1 -Branch dev
  .\git-push-retry.ps1 -Remote upstream -MaxTries 15 -Delay 5
#>
param(
  [string]$Remote = "origin",
  [string]$Branch = "main",
  [int]$MaxTries = 10,
  [int]$Delay = 3
)

# 国内网络常见修复：强制 HTTP/1.1 长连接 + 放大缓冲，避免 curl 52/55 中途重置
git config --global http.version HTTP/1.1
git config --global http.postBuffer 524288000
#common colors: Black、DarkBlue、DarkGreen、DarkCyanDarkRed、DarkMagenta、DarkYellow、Gray、DarkGray、Blue、Green、Cyan、Red、Magenta、Yellow、White
for ($i = 1; $i -le $MaxTries; $i++) {
  Write-Host "=== try $i / $MaxTries ===" -ForegroundColor DarkYellow
  git push $Remote $Branch
  if ($LASTEXITCODE -eq 0) {
    Write-Host "PUSH OK" -ForegroundColor Green
    exit 0
  }
  Write-Host "retry in ${Delay}s..." -ForegroundColor Yellow
  Start-Sleep -Seconds $Delay
}
Write-Host "FAILED after $MaxTries tries🥴" -ForegroundColor Red
exit 1
