---
title: "npm pnpm yarn镜像源配置"
date: 2026-04-08T10:42:51+08:00
tags:
  - JavaScript
draft: false
---

```
npm get registry
# 国内 淘宝 镜像源
npm config set registry https://registry.npmmirror.com/
# 官方镜像源
npm config set registry https://registry.npmjs.org/
```

```
pnpm get registry
# 国内 淘宝 镜像源
pnpm config set registry https://registry.npmmirror.com/
# 官方镜像源
pnpm config set registry https://registry.npmjs.org/
```

```
npm install -g yarn@1.22.19
yarn config get registry
# 国内 淘宝 镜像源
yarn config set registry https://registry.npmmirror.com/
# 官方镜像源
yarn config set registry https://registry.yarnpkg.com/
```

清除缓存
```
yarn cache clean --force
```


