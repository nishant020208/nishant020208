# Setup Global Git Hook for Real-time Profile Updates
# Run this script in PowerShell to automate the trigger setup.

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Setting up Global Git Hook for Profile Updates" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Ask for GitHub Personal Access Token (PAT)
$tokenPath = Join-Path $env:USERPROFILE ".github_token"
$token = ""

if (Test-Path $tokenPath) {
    $existingToken = Get-Content $tokenPath -Raw
    if ($existingToken -and $existingToken.Trim().Length -gt 0) {
        $response = Read-Host "A GitHub token already exists at ~/.github_token. Do you want to overwrite it? (y/N)"
        if ($response -match "^[yY]") {
            $token = Read-Host "Enter your new GitHub Personal Access Token (PAT)"
        } else {
            $token = $existingToken.Trim()
        }
    }
} else {
    Write-Host "To trigger your workflow, we need a GitHub Personal Access Token (PAT)." -ForegroundColor Yellow
    Write-Host "Generate one here: https://github.com/settings/tokens" -ForegroundColor Yellow
    Write-Host "Required scopes: 'repo' (or 'public_repo' + 'workflow')." -ForegroundColor Yellow
    Write-Host ""
    $token = Read-Host "Enter your GitHub Personal Access Token"
}

if (-not $token) {
    Write-Error "A GitHub token is required to set up the trigger hook."
}

# Save token
$token = $token.Trim()
Set-Content -Path $tokenPath -Value $token -NoNewline
Write-Host "Saved GitHub token to ~/.github_token" -ForegroundColor Green

# 2. Configure Global Hooks Directory
$hooksDir = Join-Path $env:USERPROFILE ".git_global_hooks"
if (-not (Test-Path $hooksDir)) {
    New-Item -ItemType Directory -Path $hooksDir | Out-Null
    Write-Host "Created global hooks directory at $hooksDir" -ForegroundColor Green
}

# 3. Create post-push hook
$hookPath = Join-Path $hooksDir "post-push"

$hookContent = @"
#!/bin/sh

# Read token
TOKEN_FILE="`$HOME/.github_token"
if [ ! -f "`$TOKEN_FILE" ]; then
  exit 0
fi
TOKEN=\$(cat "`$TOKEN_FILE")

if [ -z "`$TOKEN" ]; then
  exit 0
fi

# Run API trigger in background to avoid blocking the git push command
(
  echo ""
  echo "⚡ Triggering GitHub Profile Streak Update..."
  curl -s -X POST \
    -H "Authorization: token `$TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/repos/nishant020208/nishant020208/dispatches \
    -d '{"event_type": "update-stats"}' > /dev/null 2>&1 &
) &
"@

Set-Content -Path $hookPath -Value $hookContent -NoNewline
Write-Host "Created global post-push hook at $hookPath" -ForegroundColor Green

# 4. Set Git global config to point to hooks directory
# Convert Windows backslashes to forward slashes for Git config compatibility
$gitHooksDir = $hooksDir.Replace("\", "/")
git config --global core.hooksPath $gitHooksDir
Write-Host "Configured Git to use global hooks path: $gitHooksDir" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host " Setup Complete! Every time you do a 'git push' to any repo," -ForegroundColor Green
Write-Host " your streak stats & graph will update automatically." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
