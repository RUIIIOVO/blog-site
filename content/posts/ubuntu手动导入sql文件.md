---
title: "ubuntu手动导入sql文件"
date: 2026-04-08T10:42:52+08:00
draft: false
---

1. 上传sql文件
2. mysql -uroot -p 进入数据库，执行命令：
	CREATE DATABASE IF NOT EXISTS your_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
	USE your_db;
	SOURCE /tmp/dump.sql;

```
CREATE DATABASE IF NOT EXISTS xnl DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE xnl;
SOURCE /home/ubuntu/xnl.sql;
```
