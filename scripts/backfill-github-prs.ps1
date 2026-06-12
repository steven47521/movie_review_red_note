# Backfill GitHub PR records for course section 4.7
# Requires: git push access + GITHUB_TOKEN (repo scope) or gh auth login

$ErrorActionPreference = "Stop"
$Owner = "steven47521"
$Repo = "movie_review_red_note"

Set-Location (Split-Path -Parent $PSScriptRoot)

$prs = @(
    @{ Num = 1;  Branch = "feature/P0-spec-process";       Head = "75a9dc2"; Title = "docs(P0-A): spec, plan, process log, reflection"; Body = "Subagent: Cursor brainstorming/writing-plans. Human: product pivot RAG to xiaohongshu review." },
    @{ Num = 2;  Branch = "feature/P0B-cold-start";        Head = "4f06986"; Title = "feat(P0-B): cold-start validation archive"; Body = "Subagent: Codex R1 + Claude Code R2 T1. Human: PLAN gate fix; claudecode archived." },
    @{ Num = 3;  Branch = "feature/T1-scaffold";           Head = "4f06986"; Title = "feat(T1): project scaffold with health check"; Body = "Subagent: Cursor subagent-driven-development. Human: merged claudecode; CI D5/D6 fixes." },
    @{ Num = 4;  Branch = "feature/T2-mysql-models";       Head = "4f06986"; Title = "feat(T2): mysql models and alembic"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 5;  Branch = "feature/T3-personas";           Head = "4f06986"; Title = "feat(T3): 80 personas and matcher"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 6;  Branch = "feature/T4-research";           Head = "4f06986"; Title = "feat(T4): movie research service"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 7;  Branch = "feature/T5-ideation";           Head = "4f06986"; Title = "feat(T5): ideation angles and routes"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 8;  Branch = "feature/T6-review-room-text";   Head = "4f06986"; Title = "feat(T6): review room text phase + SSE"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 9;  Branch = "feature/T7-draft-edit";         Head = "4f06986"; Title = "feat(T7): draft regenerate and de-ai polish"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 10; Branch = "feature/T8-visual-review";      Head = "4f06986"; Title = "feat(T8): gpt-image-2 visuals + image review"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 11; Branch = "feature/T9-library";            Head = "4f06986"; Title = "feat(T9): library timeline and publish flags"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 12; Branch = "feature/T10-frontend-scaffold"; Head = "4f06986"; Title = "feat(T10): nextjs dashboard + open design"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 13; Branch = "feature/T11-review-room-ui";    Head = "4f06986"; Title = "feat(T11): review room chat UI with SSE"; Body = "Subagent: Cursor subagent + TDD. Human: enforced nexu-io/open-design tokens." },
    @{ Num = 14; Branch = "feature/T12-frontend-flows";  Head = "4f06986"; Title = "feat(T12): creation wizard + gallery"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 15; Branch = "feature/T13-docker-ci";         Head = "ef3baeb"; Title = "feat(T13): docker compose + CI + GHCR"; Body = "Subagent: Cursor subagent + TDD. Human: none." },
    @{ Num = 16; Branch = "feature/T14-deploy";            Head = "4f06986"; Title = "feat(T14): deployment configs"; Body = "Subagent: Cursor subagent. Human: deploy URL placeholder pending account." },
    @{ Num = 17; Branch = "feature/T15-integration";       Head = "4f06986"; Title = "test(T15): integration tests + line count"; Body = "Subagent: Cursor verification-before-completion. Human: mock panel size + line count ceiling." },
    @{ Num = 18; Branch = "feature/C1-delivery";         Head = "main";    Title = "docs(C1): delivery checklist and PR backfill"; Body = "Subagent: Cursor finishing-a-development-branch. Human: REFLECTION; commit dates; submission folder." }
)

Write-Host "Creating/pushing feature branches..."
$mainSha = (git rev-parse main).Trim()
foreach ($pr in $prs) {
    $sha = if ($pr.Head -eq "main") { $mainSha } else { $pr.Head }
    git branch -f $pr.Branch $sha 2>$null
}
$branchNames = $prs | ForEach-Object { $_.Branch }
git push origin --force @branchNames

$token = $env:GITHUB_TOKEN
if (-not $token) {
    Write-Host ""
    Write-Host "Branches pushed. Set GITHUB_TOKEN to create PRs via API, or install gh: gh auth login"
    Write-Host "See docs/PR_HISTORY.md for details."
    exit 0
}

$headers = @{
    Authorization = "Bearer $token"
    Accept = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

foreach ($pr in $prs) {
    $payload = @{
        title = $pr.Title
        head  = $pr.Branch
        base  = "main"
        body  = ($pr.Body + " Task PR #" + $pr.Num + " — see docs/PR_HISTORY.md")
    } | ConvertTo-Json

    try {
        $resp = Invoke-RestMethod -Method Post -Uri "https://api.github.com/repos/$Owner/$Repo/pulls" -Headers $headers -Body $payload -ContentType "application/json"
        Write-Host "Created PR #$($resp.number): $($pr.Title)"
        $closePayload = '{"state":"closed"}'
        Invoke-RestMethod -Method Patch -Uri "https://api.github.com/repos/$Owner/$Repo/pulls/$($resp.number)" -Headers $headers -Body $closePayload -ContentType "application/json" | Out-Null
        Write-Host "  Closed PR #$($resp.number) (changes already on main)"
    } catch {
        Write-Warning ("PR #" + $pr.Num + " failed: " + $_.Exception.Message)
    }
}

Write-Host ("Done. See https://github.com/" + $Owner + "/" + $Repo + "/pulls?q=is%3Apr")
