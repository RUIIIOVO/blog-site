param(
    [string]$DeployHost = "",
    [string]$DeployPort = "22",
    [string]$DeployUser = "ubuntu",
    [string]$DeployTargetBase = "/home/ubuntu/blog-site",
    [string]$BaseUrl = "https://your-domain.com",
    [string]$KeyPath = "$env:USERPROFILE/.ssh/id_ed25519",
    [string]$EnvFile = ".env"
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

$loadedEnvCount = Import-DotEnv -Path $EnvFile
if ($loadedEnvCount -gt 0) {
    Write-Host ("[env] Loaded {0} variables from {1}" -f $loadedEnvCount, $EnvFile)
}

Apply-EnvFallback -ParameterName "DeployHost" -EnvName "DEPLOY_HOST" -Target ([ref]$DeployHost)
Apply-EnvFallback -ParameterName "DeployPort" -EnvName "DEPLOY_PORT" -Target ([ref]$DeployPort)
Apply-EnvFallback -ParameterName "DeployUser" -EnvName "DEPLOY_USER" -Target ([ref]$DeployUser)
Apply-EnvFallback -ParameterName "DeployTargetBase" -EnvName "DEPLOY_TARGET_BASE" -Target ([ref]$DeployTargetBase)
Apply-EnvFallback -ParameterName "BaseUrl" -EnvName "SITE_URL" -Target ([ref]$BaseUrl)
Apply-EnvFallback -ParameterName "KeyPath" -EnvName "DEPLOY_KEY_PATH" -Target ([ref]$KeyPath)

$requiredParameters = @{
    DeployHost       = $DeployHost
    DeployUser       = $DeployUser
    DeployTargetBase = $DeployTargetBase
    BaseUrl          = $BaseUrl
}
foreach ($entry in $requiredParameters.GetEnumerator()) {
    if ([string]::IsNullOrWhiteSpace($entry.Value)) {
        throw "Missing required parameter: $($entry.Key). Provide command argument or .env value."
    }
}

Require-Command "hugo"
Require-Command "ssh"
Require-Command "scp"

$sshArgs = @("-p", $DeployPort)
$scpArgs = @("-P", $DeployPort)
if (Test-Path $KeyPath) {
    $sshArgs += @("-o", "IdentitiesOnly=yes", "-i", $KeyPath)
    $scpArgs += @("-o", "IdentitiesOnly=yes", "-i", $KeyPath)
}

Write-Host "[1/4] Build site"
& hugo --minify --baseURL $BaseUrl
if ($LASTEXITCODE -ne 0) {
    throw "hugo build failed"
}

if (-not (Test-Path "public")) {
    throw "public directory not found"
}

$timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddHHmmss")
$releaseDir = "$DeployTargetBase/releases/$timestamp"
$destination = ("{0}@{1}:{2}/" -f $DeployUser, $DeployHost, $releaseDir)
$remoteLogin = ("{0}@{1}" -f $DeployUser, $DeployHost)

Write-Host "[2/4] Create remote release directory: $releaseDir"
$mkdirCmd = "mkdir -p '$releaseDir'"
& ssh @sshArgs $remoteLogin $mkdirCmd
if ($LASTEXITCODE -ne 0) {
    throw "remote mkdir failed"
}

Write-Host "[3/4] Upload files and switch current"
& scp @scpArgs -r "public/." $destination
if ($LASTEXITCODE -ne 0) {
    throw "scp upload failed"
}

$switchCmd = "cd '$DeployTargetBase'; ln -sfn 'releases/$timestamp' 'current'"
& ssh @sshArgs $remoteLogin $switchCmd
if ($LASTEXITCODE -ne 0) {
    throw "switch current symlink failed"
}

Write-Host "[4/4] Verify site"
if (Get-Command "curl.exe" -ErrorAction SilentlyContinue) {
    & curl.exe -I $BaseUrl
    if ($LASTEXITCODE -ne 0) {
        throw "site verification failed"
    }
}
else {
    $response = Invoke-WebRequest -Method Head -Uri $BaseUrl -TimeoutSec 15
    Write-Host ("HTTP {0} {1}" -f $response.StatusCode, $response.StatusDescription)
}

Write-Host "Deploy completed: $releaseDir"
