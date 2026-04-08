param(
    [Parameter(Mandatory = $true)]
    [string]$Host,
    [Parameter(Mandatory = $true)]
    [string]$User,
    [string]$Port = "22",
    [string]$LocalCertDir = "./certs_nginx",
    [string]$RemoteCertDir = "/home/ubuntu/certs/your-domain.com",
    [string]$CertBaseName = "your-domain.com"
)

$ErrorActionPreference = "Stop"

scp -P "$Port" "$LocalCertDir/$($CertBaseName)_bundle.crt" "$User@$Host:$RemoteCertDir/$($CertBaseName)_bundle.crt"
scp -P "$Port" "$LocalCertDir/$($CertBaseName).key" "$User@$Host:$RemoteCertDir/$($CertBaseName).key"
Write-Host "证书上传完成: $RemoteCertDir"
