---
title: "Jenv使用"
date: 2026-04-08T10:42:55+08:00
tags:
  - Java
  - Git
  - Windows
draft: false
---

文档：
https://github.com/FelixSelter/JEnv-for-Windows
教程
https://blog.csdn.net/xhy18634297976/article/details/127454312
安装：
1. 下载JEnv.zip到D盘解压
https://github.com/FelixSelter/JEnv-for-Windows/releases/tag/v2.2.1
2. 修改环境变量，path中添加 D:\App\JEnv，并放在最上方
3. 执行C:\JEnv\src\jenv.ps1 使用poweshell执行
4. 安装jdk，使用下面的命令进行配置
```
jenv add jdk17 "D:\App\Java\jdk-17"
jenv add jdk8 "D:\Application\Java\jre1.8"
jenv add jdk21 "D:\App\Java\jdk-21"
jenv list
全局切换：
jenv change jdk17
java -version
```

报错：
```
无法加载文件 D:\App\JEnv\src\jenv.ps1。未对文件 D:\App\JEnv\src\jenv.ps1 进行数字签名。无法在当前系统上运行该脚本。有关 运行脚本和设置执行策略的详细信息，请参阅 https:/go.microsoft.com/fwlink/?LinkID=135170 中的 about_Execution_Policies。     + CategoryInfo          : Security
```
![Pasted image 20250514102041](/uploads/Pasted%20image%2020250514102041.png)
