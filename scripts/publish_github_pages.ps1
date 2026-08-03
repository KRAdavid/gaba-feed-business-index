[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?$')]
    [string]$RepositoryUrl,

    [ValidateSet('main', 'master')]
    [string]$Branch = 'main',

    [string]$AuthorName,
    [string]$AuthorEmail
)

$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $workspace

function Assert-LastExitCode {
    param([string]$Step)
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE."
    }
}

if (-not (Test-Path -LiteralPath '.git')) {
    throw "Git repository is not initialized: $workspace"
}

python scripts/update_public_index.py
Assert-LastExitCode 'Index refresh'
python scripts/validate_public_index.py
Assert-LastExitCode 'Index validation'
python scripts/prepare_public_site.py
Assert-LastExitCode 'Download preparation'
python scripts/validate_public_site.py --max-age-hours 2
Assert-LastExitCode 'Site validation'
python -m unittest discover -s tests -v
Assert-LastExitCode 'Automated tests'

if ($AuthorName) {
    git config user.name $AuthorName
}
if ($AuthorEmail) {
    git config user.email $AuthorEmail
}
if (-not (git config --get user.name) -or -not (git config --get user.email)) {
    throw 'Git author identity is missing. Pass -AuthorName and -AuthorEmail, or configure git first.'
}

$existingOrigin = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
    if ($existingOrigin.TrimEnd('/') -ne $RepositoryUrl.TrimEnd('/')) {
        throw "Existing origin differs from requested repository: $existingOrigin"
    }
} else {
    git remote add origin $RepositoryUrl
    Assert-LastExitCode 'Adding origin remote'
}

git add --all
Assert-LastExitCode 'Staging files'
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m 'feat: publish GABA feed business model index'
    Assert-LastExitCode 'Creating commit'
}

git branch -M $Branch
Assert-LastExitCode 'Selecting publication branch'
git push --set-upstream origin $Branch
Assert-LastExitCode 'Pushing publication branch'

$repositoryPage = $RepositoryUrl -replace '\.git$', ''
Write-Host ''
Write-Host 'Source push completed.' -ForegroundColor Green
Write-Host "Enable GitHub Pages with Source = GitHub Actions: $repositoryPage/settings/pages"
Write-Host 'After enabling Pages, run the workflow named “Refresh and publish public index”.'
