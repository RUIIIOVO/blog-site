---
title: "nohup部署"
date: 2026-04-08T10:42:55+08:00
tags:
  - Java
  - 部署
draft: false
---

启动命令：
nohup java -jar lb-permission-encrypt-sdk-0.0.1-SNAPSHOT.jar > /home/laibu/datasafe/log/output.log 2>&1 &

启动命令（混淆版）：
nohup java -javaagent:lb-permission-encrypt-sdk-0.0.1-SNAPSHOT-encrypted.jar -jar lb-permission-encrypt-sdk-0.0.1-SNAPSHOT-encrypted.jar > /dev/null 2>&1 &

设置启动参数：

nohup java -Xms1200m -Xmx2000m -Xmn600m -XX:+UseG1GC -XX:MaxGCPauseMillis=150 -XX:G1HeapRegionSize=16m -XX:MaxDirectMemorySize=256m -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/logs/heapdump/ -Xss256k -XX:+UseStringDeduplication -javaagent:lb-permission-encrypt-sdk-0.0.1-SNAPSHOT-encrypted.jar -jar lb-permission-encrypt-sdk-0.0.1-SNAPSHOT-encrypted.jar > /dev/null 2>&1 &

nohup java -Xms1500m -Xmx2g -Xmn1g -XX:+UseG1GC -XX:MaxGCPauseMillis=150 -XX:G1HeapRegionSize=16m -XX:MaxDirectMemorySize=256m -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/logs/heapdump/ -Xss256k -javaagent:lb-permission-encrypt-sdk-0.0.1-SNAPSHOT-encrypted.jar -jar lb-permission-encrypt-sdk-0.0.1-SNAPSHOT-encrypted.jar > /dev/null 2>&1 &


查看进程：
```
ps -ef|grep java
```
查看所有进程：
```
ps -A
```
杀死进程：
```
kill -9 [进程号]
```

```
cd /home/laibu/jmeter/test/10MB-100MB/
```

```
jmeter -n -t 10MB-100MB.jmx
```
