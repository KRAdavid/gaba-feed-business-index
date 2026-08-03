[CmdletBinding()]
param(
    [ValidatePattern('^[a-z0-9](?:[a-z0-9-]{0,56}[a-z0-9])?$')]
    [string]$ProjectName,

    [ValidatePattern('^[A-Za-z0-9._/-]+$')]
    [string]$Branch = 'main',

    [switch]$SkipBuild,

    [switch]$ValidateOnly
)

$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$staticOutput = Join-Path $workspace 'release\GABA_Feed_Public_Site_Static'
Set-Location -LiteralPath $workspace

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Step,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )

    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE."
    }
}

if (-not $SkipBuild) {
    Invoke-Checked 'Preparing public downloads' { python scripts/prepare_public_site.py }
    Invoke-Checked 'Validating public index' { python scripts/validate_public_index.py }
    Invoke-Checked 'Validating public site' { python scripts/validate_public_site.py }
    Invoke-Checked 'Building host-independent release' { python scripts/build_static_release.py }
}

Invoke-Checked 'Validating host-independent release' { python scripts/validate_static_release.py }

if ($ValidateOnly) {
    Write-Host "Validated static deployment folder: $staticOutput" -ForegroundColor Green
    exit 0
}

if ([string]::IsNullOrWhiteSpace($ProjectName)) {
    throw 'ProjectName is required for deployment. Pass -ProjectName <cloudflare-pages-project>.'
}
if ([string]::IsNullOrWhiteSpace($env:CLOUDFLARE_API_TOKEN)) {
    throw 'CLOUDFLARE_API_TOKEN is not set. Use a scoped Pages deployment token or upload the ZIP in the Cloudflare dashboard.'
}
if ([string]::IsNullOrWhiteSpace($env:CLOUDFLARE_ACCOUNT_ID)) {
    throw 'CLOUDFLARE_ACCOUNT_ID is not set.'
}

$npx = Get-Command npx -ErrorAction SilentlyContinue
$pnpm = Get-Command pnpm -ErrorAction SilentlyContinue
if ($npx) {
    Invoke-Checked 'Deploying to Cloudflare Pages' {
        & $npx.Source 'wrangler@4' 'pages' 'deploy' $staticOutput "--project-name=$ProjectName" "--branch=$Branch"
    }
} elseif ($pnpm) {
    Invoke-Checked 'Deploying to Cloudflare Pages' {
        & $pnpm.Source 'dlx' 'wrangler@4' 'pages' 'deploy' $staticOutput "--project-name=$ProjectName" "--branch=$Branch"
    }
} else {
    throw 'npx or pnpm is required. Install Node.js, or upload release/GABA_Feed_Public_Site_Static_Deploy.zip in the Cloudflare dashboard.'
}

Write-Host "Cloudflare Pages deployment completed for project: $ProjectName" -ForegroundColor Green
