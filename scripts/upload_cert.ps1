param(
    [Parameter(Mandatory = $true)]
    [string]$Host,
    [Parameter(Mandatory = $true)]
    [string]$User,
    [string]$Port = "22",
    [string]$LocalCertDir = "./your-domain.com_nginx",
    [string]$RemoteCertDir = "/home/ubuntu/certs/your-domain.com"
)

$ErrorActionPreference = "Stop"

scp -P "$Port" "$LocalCertDir/your-domain.com_bundle.crt" "$User@$Host:$RemoteCertDir/your-domain.com_bundle.crt"
scp -P "$Port" "$LocalCertDir/your-domain.com.key" "$User@$Host:$RemoteCertDir/your-domain.com.key"
Write-Host "证书上传完成: $RemoteCertDir"
