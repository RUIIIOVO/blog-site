---
title: "Anaconda安装 使用"
date: 2026-04-08T10:42:52+08:00
tags:
  - Python
draft: false
---

https://blog.csdn.net/qq_44000789/article/details/142214660

配置镜像源：
教程：[https://blog.csdn.net/qq_38614074/article/details/139649680]
管理员运行Anaconda Prompt

查看镜像源
```
conda config --show channels
```

```
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/msys2/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/bioconda/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/menpo/
 #设置搜索时显示通道地址
conda config --set show_channel_urls yes
```

使用教程：[https://blog.csdn.net/u011385476/article/details/105277426]
创建虚拟环境
```
conda create -n test python=3.7
conda create -n QmapCompression python=3.8
conda env list

```
激活虚拟环境
```
conda activate your_env_name
```
删除虚拟环境
```
conda remove -n  your_env_name --all
```

安装依赖
```
 pip install --upgrade pip
 pip install -r requirements.txt
```

```
pip config unset global.index-url
```
