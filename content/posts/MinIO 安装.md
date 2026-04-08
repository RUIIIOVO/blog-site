---
title: "MinIO 安装"
date: 2026-04-08T10:42:54+08:00
tags:
  - 数据库
  - Windows
  - 运维
draft: false
---

下载MinIO在Windows下的安装包，下载地址：https://dl.min.io/server/minio/release/windows-amd64/minio.exe
- 下载完成后创建MinIO的数据存储目录，并使用如下启动命令MinIO服务；

```
D:\Code\minio>minio.exe server D:\App\minio\data --console-address ":9001"
```

- 此时MinIO的API将运行在`9000`端口，MinIO Console管理页面将运行在`9001`端口；
- MinIO服务运行成功后就可访问MinIO Console的管理界面了，输入账号密码`minioadmin:minioadmin`即可登录，访问地址：http://localhost:9001
