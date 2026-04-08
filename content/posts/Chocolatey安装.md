---
title: "Chocolatey安装"
date: 2026-04-08T10:42:52+08:00
tags:
  - Java
  - macOS
draft: false
---

更改安装路径
```
$env:ChocolateyInstall = 'D:\Application\Chocolatey'
[Environment]::SetEnvironmentVariable('ChocolateyInstall', $env:ChocolateyInstall, 'Machine')
```
安装
```
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
更改默认下载路径
```
choco config set installLocation D:\Application
```
安装jdk1.8
```
choco install jdk8 --install-directory="D:\Application\Java\jdk8\'"
```
网址：[https://community.chocolatey.org/packages?q=java8]

