param(
    [string]$BaseUrl = "",
    [string]$PagesBranch = "gh-pages",
    [string]$RepoUrl = "",
    [string]$OutputDir = ".dist/github-pages-site",
    [string]$PackageDir = ".dist/packages",
    [string]$EnvFile = ".env",
    [string]$GitUserName = "github-pages-bot",
    [string]$GitUserEmail = "github-pages-bot@users.noreply.github.com",
    [switch]$PackageOnly,
    [switch]$SkipZip
)

$ErrorActionPreference = "Stop"
$ScriptBoundParameters = @{} + $PSBoundParameters

function Require-Command {
    param([Parameter(Mandatory = $true)][string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Missing command: $Name"
    }
}

function Import-DotEnv {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path $Path)) {
        return 0
    }

    $loaded = 0
    foreach ($rawLine in Get-Content $Path) {
        $line = $rawLine.Trim()
        if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#")) {
            continue
        }

        $separatorIndex = $line.IndexOf("=")
        if ($separatorIndex -lt 1) {
            continue
        }

        $key = $line.Substring(0, $separatorIndex).Trim()
        $value = $line.Substring($separatorIndex + 1).Trim().Trim('"').Trim("'")
        if ([string]::IsNullOrWhiteSpace($key)) {
            continue
        }

        [Environment]::SetEnvironmentVariable($key, $value, "Process")
        $loaded++
    }

    return $loaded
}

function Apply-EnvFallback {
    param(
        [Parameter(Mandatory = $true)][string]$ParameterName,
        [Parameter(Mandatory = $true)][string]$EnvName,
        [Parameter(Mandatory = $true)][ref]$Target
    )

    if ($ScriptBoundParameters.ContainsKey($ParameterName)) {
        return
    }

    $envValue = [Environment]::GetEnvironmentVariable($EnvName, "Process")
    if (-not [string]::IsNullOrWhiteSpace($envValue)) {
        $Target.Value = $envValue
    }
}

function Resolve-OriginRepoUrl {
    $url = (& git remote get-url origin 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($url)) {
        throw "Failed to resolve git remote origin url"
    }
    return $url.Trim()
}

function Resolve-GitHubPagesBaseUrl {
    param([Parameter(Mandatory = $true)][string]$OriginRepoUrl)

    if ($OriginRepoUrl -match '^https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$') {
        $owner = $Matches[1]
        $repo = $Matches[2]
        return "https://$owner.github.io/$repo/"
    }

    if ($OriginRepoUrl -match '^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$') {
        $owner = $Matches[1]
        $repo = $Matches[2]
        return "https://$owner.github.io/$repo/"
    }

    throw "Cannot infer GitHub Pages baseURL from repo url: $OriginRepoUrl"
}

function Reset-Dir {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (Test-Path $Path) {
        Remove-Item -Recurse -Force $Path
    }
    New-Item -ItemType Directory -Path $Path | Out-Null
}

$loadedEnvCount = Import-DotEnv -Path $EnvFile
if ($loadedEnvCount -gt 0) {
    Write-Host ("[env] Loaded {0} variables from {1}" -f $loadedEnvCount, $EnvFile)
}

Apply-EnvFallback -ParameterName "BaseUrl" -EnvName "GITHUB_PAGES_URL" -Target ([ref]$BaseUrl)
Apply-EnvFallback -ParameterName "PagesBranch" -EnvName "GITHUB_PAGES_BRANCH" -Target ([ref]$PagesBranch)
Apply-EnvFallback -ParameterName "RepoUrl" -EnvName "GITHUB_REPO_URL" -Target ([ref]$RepoUrl)
Apply-EnvFallback -ParameterName "GitUserName" -EnvName "GITHUB_PAGES_GIT_NAME" -Target ([ref]$GitUserName)
Apply-EnvFallback -ParameterName "GitUserEmail" -EnvName "GITHUB_PAGES_GIT_EMAIL" -Target ([ref]$GitUserEmail)

Require-Command "hugo"
Require-Command "git"

if ([string]::IsNullOrWhiteSpace($RepoUrl)) {
    $RepoUrl = Resolve-OriginRepoUrl
}

if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
    $BaseUrl = Resolve-GitHubPagesBaseUrl -OriginRepoUrl $RepoUrl
}

$timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddHHmmss")
$resolvedOutputDir = [IO.Path]::GetFullPath($OutputDir)
$resolvedPackageDir = [IO.Path]::GetFullPath($PackageDir)
$packagePath = Join-Path $resolvedPackageDir ("site-{0}.zip" -f $timestamp)

Write-Host ("[1/4] Build Hugo site -> {0}" -f $resolvedOutputDir)
Reset-Dir -Path $resolvedOutputDir
& hugo --minify --baseURL $BaseUrl --destination $resolvedOutputDir
if ($LASTEXITCODE -ne 0) {
    throw "hugo build failed"
}

New-Item -ItemType File -Path (Join-Path $resolvedOutputDir ".nojekyll") -Force | Out-Null

if (-not $SkipZip) {
    Write-Host ("[2/4] Package site -> {0}" -f $packagePath)
    if (-not (Test-Path $resolvedPackageDir)) {
        New-Item -ItemType Directory -Path $resolvedPackageDir | Out-Null
    }
    if (Test-Path $packagePath) {
        Remove-Item -Force $packagePath
    }
    Compress-Archive -Path (Join-Path $resolvedOutputDir "*") -DestinationPath $packagePath
}
else {
    Write-Host "[2/4] Skip zip package"
}

if ($PackageOnly) {
    Write-Host "[done] PackageOnly mode, skip deploy"
    Write-Host ("baseURL: {0}" -f $BaseUrl)
    if (-not $SkipZip) {
        Write-Host ("package: {0}" -f $packagePath)
    }
    exit 0
}

Write-Host ("[3/4] Deploy to {0}:{1}" -f $RepoUrl, $PagesBranch)
Push-Location $resolvedOutputDir
try {
    & git init
    & git checkout -B $PagesBranch
    & git config user.name $GitUserName
    & git config user.email $GitUserEmail
    & git add -A
    & git commit -m ("deploy: github pages {0}" -f $timestamp)
    & git remote add origin $RepoUrl
    & git push -f origin ("HEAD:{0}" -f $PagesBranch)
    if ($LASTEXITCODE -ne 0) {
        throw "push gh-pages failed"
    }
}
finally {
    Pop-Location
}

Write-Host "[4/4] Deploy completed"
Write-Host ("baseURL: {0}" -f $BaseUrl)
Write-Host ("branch: {0}" -f $PagesBranch)
if (-not $SkipZip) {
    Write-Host ("package: {0}" -f $packagePath)
}
