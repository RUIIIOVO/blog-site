---
title: "CSS省略号"
date: 2026-04-08T10:42:55+08:00
tags:
  - 前端
draft: false
---

单行文本
```
overflow: hidden;
white-space: nowrap;
text-overflow: ellipsis;
```
多行文本
```
display: -webkit-box;
-webkit-box-orient: vertical;
-webkit-line-clamp: 3;/* 设置为想要的行数 */
overflow: hidden;
text-overflow: ellipsis;
```
nvue
```
overflow: hidden;

text-overflow: ellipsis;

display: -webkit-box;

-webkit-box-orient: vertical;

-webkit-line-clamp: 1; /* 显示的行数 */

lines: 1; /* NVUE下要用这个属性，来让文字超出隐藏变省略号 */
```
