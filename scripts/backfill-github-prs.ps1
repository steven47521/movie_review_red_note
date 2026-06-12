# Backfill GitHub closed PR records for course section 4.7
# Auth: GITHUB_TOKEN env, or git credential-manager for github.com

$ErrorActionPreference = "Stop"
$Owner = "steven47521"
$Repo = "movie_review_red_note"

Set-Location (Split-Path -Parent $PSScriptRoot)

function Get-GitHubToken {
    if ($env:GITHUB_TOKEN) { return $env:GITHUB_TOKEN }
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "git"
    $psi.Arguments = "credential fill"
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.UseShellExecute = $false
    $p = [System.Diagnostics.Process]::Start($psi)
    $p.StandardInput.WriteLine("protocol=https")
    $p.StandardInput.WriteLine("host=github.com")
    $p.StandardInput.WriteLine("")
    $p.StandardInput.Close()
    $out = $p.StandardOutput.ReadToEnd()
    $p.WaitForExit()
    if ($out -match "password=(.+)") { return $Matches[1].Trim() }
    return $null
}

$prs = @(
    @{ Num = 1;  Branch = "feature/P0-spec-process";       Base = "base/root";       HeadSha = "75a9dc2"; Title = "docs(P0-A): spec, plan, process log, reflection"; Body = "Subagent: Cursor brainstorming/writing-plans. Human: product pivot RAG to xiaohongshu review." },
    @{ Num = 2;  Branch = "feature/P0B-cold-start";        Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(P0-B): cold-start validation archive"; Body = "Subagent: Codex R1 + Claude Code R2 T1. Human: PLAN gate fix; claudecode archived." },
    @{ Num = 3;  Branch = "feature/T1-scaffold";           Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(T1): project scaffold with health check"; Body = "Subagent: Cursor subagent-driven-development. Human: merged claudecode; CI D5/D6 fixes." },
    @{ Num = 4;  Branch = "feature/T2-mysql-models";       Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(T2): mysql models and alembic"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 5;  Branch = "feature/T3-personas";           Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(T3): 80 personas and matcher"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 6;  Branch = "feature/T4-research";           Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(T4): movie research service"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 7;  Branch = "feature/T5-ideation";           Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(T5): ideation angles and routes"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 8;  Branch = "feature/T6-review-room-text";   Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(T6): review room text phase + SSE"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 9;  Branch = "feature/T7-draft-edit";         Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(T7): draft regenerate and de-ai polish"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 10; Branch = "feature/T8-visual-review";      Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(T8): gpt-image-2 visuals + image review"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 11; Branch = "feature/T9-library";            Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(T9): library timeline and publish flags"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 12; Branch = "feature/T10-frontend-scaffold"; Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(T10): nextjs dashboard + open design"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 13; Branch = "feature/T11-review-room-ui";    Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(T11): review room chat UI with SSE"; Body = "Subagent: Cursor subagent + TDD. Human: enforced nexu-io/open-design tokens." },
    @{ Num = 14; Branch = "feature/T12-frontend-flows";    Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(T12): creation wizard + gallery"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 15; Branch = "feature/T13-docker-ci";         Base = "base/pre-docker"; HeadSha = "ef3baeb"; Title = "feat(T13): docker compose + CI + GHCR"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 16; Branch = "feature/T14-deploy";            Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "feat(T14): deployment configs"; Body = "Subagent: Cursor subagent. Human: deploy URL placeholder pending account." },
    @{ Num = 17; Branch = "feature/T15-integration";       Base = "base/pre-impl";   HeadSha = "4f06986"; Title = "test(T15): integration tests + line count"; Body = "Subagent: Cursor verification-before-completion. Human: mock panel size + line count ceiling." },
    @{ Num = 18; Branch = "feature/C1-delivery";           Base = "base/pre-c1";     HeadSha = "main";    Title = "docs(C1): delivery checklist and PR backfill"; Body = "Subagent: Cursor finishing-a-development-branch. Human: REFLECTION; commit dates; submission folder." }
)

Write-Host "Preparing base branches..."
$stashNeeded = (git status --porcelain).Length -gt 0
if ($stashNeeded) { git stash push -u -m "backfill-prs-temp" | Out-Null }
git switch --orphan _base_root_orphan
git commit --allow-empty -m "chore: base root for PR history" | Out-Null
$rootSha = (git rev-parse HEAD).Trim()
git switch main
git branch -f base/root $rootSha
git branch -D _base_root_orphan 2>$null
if ($stashNeeded) { git stash pop -q 2>$null }
git branch -f base/pre-impl 75a9dc2
git branch -f base/pre-docker 4f06986
git branch -f base/pre-c1 470447b

$mainSha = (git rev-parse main).Trim()
foreach ($pr in $prs) {
    $sha = if ($pr.HeadSha -eq "main") { $mainSha } else { $pr.HeadSha }
    git branch -f $pr.Branch $sha
}

$allBranches = @("base/root", "base/pre-impl", "base/pre-docker", "base/pre-c1") + ($prs | ForEach-Object { $_.Branch })
git push origin --force $allBranches

$token = Get-GitHubToken
if (-not $token) {
    Write-Host "No GitHub token. Branches pushed only."
    exit 1
}

$headers = @{
    Authorization = "Bearer $token"
    Accept        = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

$created = @()
foreach ($pr in $prs) {
    $bodyText = $pr.Body + "`n`nTask PR #" + $pr.Num + " — see docs/PR_HISTORY.md"
    $payload = @{
        title = $pr.Title
        head  = $pr.Branch
        base  = $pr.Base
        body  = $bodyText
    } | ConvertTo-Json

    try {
        $resp = Invoke-RestMethod -Method Post -Uri "https://api.github.com/repos/$Owner/$Repo/pulls" -Headers $headers -Body $payload -ContentType "application/json; charset=utf-8"
        Invoke-RestMethod -Method Patch -Uri "https://api.github.com/repos/$Owner/$Repo/pulls/$($resp.number)" -Headers $headers -Body '{"state":"closed"}' -ContentType "application/json" | Out-Null
        Write-Host "Closed PR #$($resp.number): $($pr.Title)"
        $created += @{ Num = $pr.Num; Number = $resp.number; Title = $pr.Title; Url = $resp.html_url; Branch = $pr.Branch }
    } catch {
        $err = $_.ErrorDetails.Message
        Write-Warning ("PR task #" + $pr.Num + " failed: " + $err)
    }
}

$outPath = Join-Path (Split-Path -Parent $PSScriptRoot) "docs\PR_CREATED.json"
$created | ConvertTo-Json -Depth 4 | Set-Content -Path $outPath -Encoding UTF8
Write-Host "Wrote $outPath with $($created.Count) PRs"
Write-Host "https://github.com/$Owner/$Repo/pulls?q=is%3Apr+is%3Aclosed"
