# refresh_cards.ps1
# Daily auto-refresh for GitHub Profile cards (streak / activity / wakatime timeline).
# Only refreshes + commits when the USER made a real (non-auto) commit to Agying3
# since the last run. This breaks the self-perpetuating loop where the auto-commit
# itself counted as a GitHub contribution and forced a commit every single day.
# Run by Windows Task Scheduler from the Agying3 repo root.
# Depends on: gen_gh_cards.py, gen_wakatime_cards.py (same dir) and git-push-retry.ps1 (repo).
$ErrorActionPreference = "Stop"
$Repo = "H:\Agying3"
$Py   = "C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"
$StateFile = Join-Path $env:LOCALAPPDATA "agying3_last_refresh_commit.txt"

Set-Location $Repo

# 0. remove stale index.lock so git add/commit never silently fails
$lock = Join-Path $Repo ".git/index.lock"
if (Test-Path $lock) { Remove-Item $lock -Force -ErrorAction SilentlyContinue }

# 1. re-fetch data and render SVG (scripts only output into assets/)
& $Py gen_gh_cards.py; $g = $LASTEXITCODE
& $Py gen_wakatime_cards.py; $w = $LASTEXITCODE
if ($g -ne 0 -or $w -ne 0) { Write-Warning "generator failed (gh=$g waka=$w), skip commit"; exit 0 }

# 2. decide whether a REAL change happened since last refresh.
#    latest commit whose message is NOT our own auto-refresh commit.
$current = (git log --format=%H --grep="auto refresh cards" --invert-grep -1).Trim()
$last = if (Test-Path $StateFile) { (Get-Content $StateFile -Raw).Trim() } else { "" }

if ($last -eq "") {
    # first run: just record state, do NOT commit (avoid an immediate +1 contribution)
    Set-Content -Path $StateFile -Value $current -NoNewline
    Write-Host "first run: state initialized, no commit"
    exit 0
}

if ($current -eq $last) {
    Write-Host "no new real commits since last refresh, skip"
    exit 0
}

# 3. a real commit happened -> generators already ran; stage and commit
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
    # real commit detected but cards unchanged -> still advance state
    Set-Content -Path $StateFile -Value $current -NoNewline
    Write-Host "real commit detected but cards unchanged, state advanced"
}
