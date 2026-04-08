---
title: "Ubuntu nvm下载"
date: 2026-04-08T10:42:52+08:00
tags:
  - JavaScript
  - Git
  - Ubuntu
draft: false
---

安装：
```
# 安装 curl
sudo apt install curl
# 安装 git
sudo apt install git
# 安装 nvm
bash -c "$(curl -fsSL https://gitee.com/RubyMetric/nvm-cn/raw/main/install.sh)"

```

- 重开终端，或重新打开 ssh 窗口

使用：

|命令行|作用|
|---|---|
|nvm ls|已安装的列表|
|nvm ls-remote|所有可安装版本|
|nvm install v12.20.1|安装某个版本Node|
|nvm use 12.20.1|切换Node版本|
|node -v|node.js 版本|
|nvm-update|更新nvm|

卸载：
```
bash -c "$(curl -fsSL https://gitee.com/RubyMetric/nvm-cn/raw/main/uninstall.sh)"
```
