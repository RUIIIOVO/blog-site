---
title: "nacos安装"
date: 2026-04-08T10:42:55+08:00
draft: false
---

官方文档：
https://nacos.io/docs/latest/quickstart/quick-start/?spm=5238cd80.72a042d5.0.0.5bc0cd36gYSNAV

bin目录下 启动命令：
```
startup.cmd -m standalone
```

启动报错指南：
https://blog.csdn.net/qq_45063782/article/details/119751892
https://blog.csdn.net/weixin_45396074/article/details/135177158

需要在本地mysql手动创建nacos数据库
修改配置：
secret.key 不得少于32位，不然会报错，直接把官方的注释解开即可
```
nacos.core.auth.plugin.nacos.token.secret.key=VGhpc0lzTXlDdXN0b21TZWNyZXRLZXkwMTIzNDU2Nzg=
nacos.core.auth.server.identity.key=serverIdentity
nacos.core.auth.server.identity.value=serverIdentityValue


#*************** Datasource Related Configurations ***************#
### nacos.plugin.datasource.log.enabled=true
spring.sql.init.platform=mysql
### Count of DB:
db.num=1
### Connect URL of DB:
db.url.0=jdbc:mysql://127.0.0.1:3306/nacos?characterEncoding=utf8&connectTimeout=1000&socketTimeout=3000&autoReconnect=true&useUnicode=true&useSSL=false&serverTimezone=UTC
db.user=root
db.password=123456
```

控制台地址：
http://127.0.0.1:8080/index.html
账户名：nacos 密码 Rui@030319
