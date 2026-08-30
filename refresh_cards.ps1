# refresh_cards.ps1
# Daily auto-refresh for GitHub Profile cards (streak / activity / wakatime timeline).
# Run by Windows Task Scheduler from the Agying3 repo root.
# Depends on: gen_gh_cards.py, gen_wakatime_cards.py (same dir) and git-push-retry.ps1 (repo).
$ErrorActionPreference = "Stop"
$Repo = "H:\Agying3"
$Py   = "C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"

Set-Location $Repo

# 0. remove stale index.lock so git add/commit never silently fails
$lock = Join-Path $Repo ".git/index.lock"
if (Test-Path $lock) { Remove-Item $lock -Force -ErrorAction SilentlyContinue }

# 1. re-fetch data and render SVG (scripts only output into assets/)
& $Py gen_gh_cards.py; $g = $LASTEXITCODE
& $Py gen_wakatime_cards.py; $w = $LASTEXITCODE
if ($g -ne 0 -or $w -ne 0) { Write-Warning "generator failed (gh=$g waka=$w), skip commit"; exit 0 }

# 2. stage: git add -A plus explicit key files (belt and suspenders for untracked files)
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
