---
title: "ufw 开放端口"
date: 2026-04-08T10:42:54+08:00
draft: false
---

安装
```
sudo apt install ufw
```
查看状态
```
sudo ufw status
```
开启ufw
```
sudo ufw enable
```
开放单个端口
```
sudo ufw allow 18789/tcp
```
开放多个端口
```
sudo ufw allow 80,443,8080,8085,9001,9090,15672/tcp
```
禁止端口22
```
sudo ufw delete allow 22
```
