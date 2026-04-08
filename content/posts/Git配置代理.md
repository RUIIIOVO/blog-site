---
title: "Git配置代理"
date: 2026-04-08T10:42:54+08:00
draft: false
---

```
# 设置全局代理
git config --global https.proxy http://127.0.0.1:7890
git config --global https.proxy https://127.0.0.1:7890
git config --global http.proxy socks5://127.0.0.1:7890
git config --global https.proxy socks5://127.0.0.1:7890

# 取消全局代理
git config --global --unset http.proxy
git config --global --unset https.proxy

```
