---
title: "Git"
date: 2026-04-08T10:42:56+08:00
tags:
  - Git
  - Java
draft: false
---

https://blog.csdn.net/Javachichi/article/details/140660754
git初始化配置
```
git config --global user.name 你的用户名  
git config --global user.email 你的邮箱地址  

```
查看配置
```
git config --list  
#如果信息太多，可以输入 q 退出  

```
初始化
```
git init
```
```
添加文件
# .的意思是当前目录下所有变化都暂存  
git add .  
git commit -m '提交的内容说明'  
查看提交日志
git log
一行输出
git log --oneline 
```

1. 开发分支（dev）上的代码达到上线的标准后，要合并到 master 分支
```
git checkout dev
git pull
git checkout master
git merge dev
git push -u origin master
```

2. 当master代码改动了，需要更新开发分支（dev）上的代码
```
git checkout master 
git pull 
git checkout dev
git merge master 
git push -u origin dev
```

 

![Pasted image 20250104235012](/uploads/Pasted%20image%2020250104235012.png)
查看提交状态
```
Rui@LAPTOP-8FUTVEPF MINGW64 /d/Code/git_test (master)
$ git status
On branch master
nothing to commit, working tree clean
```
![Pasted image 20250105151016](/uploads/Pasted%20image%2020250105151016.png)
