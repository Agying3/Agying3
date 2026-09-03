# refresh_cards.ps1
# Daily auto-refresh for GitHub Profile cards (streak / activity / wakatime timeline).
# Only refreshes + commits when a REAL (non-auto) commit was actually PUSHED to
# origin/main since the last refresh. This kills the "clock-in machine" loop two ways:
#   1. the auto-commit itself is excluded from the trigger (invert-grep)
#   2. local-only commits (made but NOT pushed) are ignored, because we compare
#      against origin/main, not the local log.
# Run by Windows Task Scheduler from the Agying3 repo root.
$ErrorActionPreference = "Stop"
$Repo = "H:\Agying3"
$Py   = "C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"
$StateFile = Join-Path $env:LOCALAPPDATA "agying3_last_refresh_commit.txt"

Set-Location $Repo

# 0. remove stale index.lock so git add/commit never silently fail
$lock = Join-Path $Repo ".git/index.lock"
if (Test-Path $lock) { Remove-Item $lock -Force -ErrorAction SilentlyContinue }

# 1. fetch remote (light). retry a few times; if it fails, skip (never push stale data)
$fetched = $false
for ($i = 0; $i -lt 3; $i++) {
    git fetch origin --quiet 2>$null
    if ($LASTEXITCODE -eq 0) { $fetched = $true; break }
    Start-Sleep -Seconds 3
}
if (-not $fetched) { Write-Host "fetch failed, skip"; exit 0 }

# 2. latest REAL (non-auto) commit actually pushed to origin/main
$current = (git log origin/main --format=%H --grep="auto refresh cards" --invert-grep -1).Trim()
if (-not $current) { Write-Host "no commits on remote yet, skip"; exit 0 }

$last = if (Test-Path $StateFile) { (Get-Content $StateFile -Raw).Trim() } else { "" }

if ($last -eq "") {
    # first run: just record state, do NOT commit (avoid an immediate +1 contribution)
    Set-Content -Path $StateFile -Value $current -NoNewline
    Write-Host "first run: state initialized, no commit"
    exit 0
}

if ($current -eq $last) {
    Write-Host "no new real push on remote since last refresh, skip"
    exit 0
}

# 3. a real push happened -> regenerate and commit
& $Py gen_gh_cards.py; $g = $LASTEXITCODE
& $Py gen_wakatime_cards.py; $w = $LASTEXITCODE
if ($g -ne 0 -or $w -ne 0) { Write-Warning "generator failed (gh=$g waka=$w), skip"; exit 0 }

git add -A 2>$null
git add assets/streak.svg assets/activity_graph.svg assets/wakatime_day.svg gen_gh_cards.py gen_wakatime_cards.py refresh_cards.ps1 2>$null

$status = git status --porcelain
if ($status) {
    $d = (Get-Date).ToString("yyyy-MM-dd")
    git commit -m "chore: auto refresh cards $d"
    if ($LASTEXITCODE -eq 0) {
        Set-Content -Path $StateFile -Value $current -NoNewline
        & ".\git-push-retry.ps1"
    } else {
        Write-Warning "commit failed, skip push"
    }
} else {
    # real push detected but cards unchanged -> still advance state
    Set-Content -Path $StateFile -Value $current -NoNewline
    Write-Host "real push detected but cards unchanged, state advanced"
}
