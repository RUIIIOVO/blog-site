param(
    [string]$DeployHost = "your-server-ip",
    [string]$DeployPort = "22",
    [string]$DeployUser = "ubuntu",
    [string]$DeployTargetBase = "/home/ubuntu/blog-site",
    [string]$BaseUrl = "https://your-domain.com",
    [string]$KeyPath = "$env:USERPROFILE/.ssh/id_ed25519"
)

$ErrorActionPreference = "Stop"

function Require-Command {
    param([Parameter(Mandatory = $true)][string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Missing command: $Name"
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
