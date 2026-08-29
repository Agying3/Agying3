# refresh_cards.ps1
# 每天自动刷新 GitHub Profile 卡片（streak / activity / wakatime 时间线）。
# 由 Windows 任务计划调用，放在 Agying3 仓库根目录。
# 依赖：gen_gh_cards.py、gen_wakatime_cards.py（同目录）以及仓库内 git-push-retry.ps1。
$ErrorActionPreference = "Stop"
$Repo = "H:\Agying3"
$Py   = "C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"

Set-Location $Repo

# 0. 删除可能残留的 index.lock，避免 git add/commit 静默失败
$lock = Join-Path $Repo ".git/index.lock"
if (Test-Path $lock) { Remove-Item $lock -Force -ErrorAction SilentlyContinue }

# 1. 重新抓取数据并渲染 SVG（脚本只输出到 assets/）
& $Py gen_gh_cards.py
& $Py gen_wakatime_cards.py
if ($LASTEXITCODE -ne 0) { Write-Warning "generate returned non-zero, still trying to commit" }

# 2. 暂存：git add -A 加显式关键文件（双保险，避免漏加未跟踪文件）
git add -A 2>$null
git add assets/streak.svg assets/activity_graph.svg assets/wakatime_daily.svg assets/wakatime_langs.svg assets/wakatime_day.svg gen_gh_cards.py gen_wakatime_cards.py refresh_cards.ps1 2>$null

$status = git status --porcelain
if ($status) {
    $d = (Get-Date).ToString("yyyy-MM-dd")
    git commit -m "chore: auto refresh cards $d"
    if ($LASTEXITCODE -eq 0) {
        & ".\git-push-retry.ps1"
    } else {
        Write-Warning "commit failed, skip push"
    }
} else {
    Write-Host "no changes, skip commit"
}
