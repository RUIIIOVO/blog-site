---
title: "Docker部署流程"
date: 2026-04-08T10:42:53+08:00
tags:
  - JavaScript
  - Docker
  - Linux
draft: false
---

# 一、整体流程总览（先建立全局认知）

`源码  ↓ Dockerfile（定义环境）  ↓ docker build（生成不可变镜像）  ↓ docker tag（版本化）  ↓ docker push / docker save（传输）  ↓ 服务器 docker pull / load  ↓ docker run / docker compose`

👉 **核心思想：**

- 镜像 = 唯一交付物
    
- 构建 ≠ 运行
    
- 服务器不参与构建
    

---

# 二、Step 0：准备条件（一次性）

## 本地需要

- Docker
    
- 源码 + Dockerfile
    

## 服务器需要

- Docker
    
- 能访问镜像来源（registry 或 scp）
    

❌ 服务器不需要：

- node
    
- npm
    
- 源码
    

---

# 三、Step 1：编写 Dockerfile（定义“世界”）

### 示例（以 Next.js / Node 为例）

```
# ---------- 构建阶段 ----------
FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---------- 运行阶段 ----------
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]

```

### 原理说明

- `FROM`：锁定 OS + runtime
    
- **多阶段构建**：
    
    - builder：编译、生成产物
        
    - runner：只跑结果（更小、更安全）
        
- 镜像里包含 **运行所需的一切**
    

---

# 四、Step 2：本地构建镜像（最关键）

`docker build -t my-app:1.0.0 .`

### 原理说明

- Docker：
    
    - 创建隔离的 Linux 环境
        
    - 执行 Dockerfile 中的指令
        
- 生成一个 **不可变镜像**
    
- 这个镜像：
    
    - 不依赖你的电脑
        
    - 不依赖服务器
        

📌 这一步 **等同于“编译交付物”**

---

# 五、Step 3：给镜像打 Tag（版本化）

`docker tag my-app:1.0.0 registry.example.com/my-app:1.0.0`

### 原理说明

- Tag ≈ 版本号
    
- 同一个 IMAGE ID 可以有多个 tag
    
- 用于：
    
    - 回滚
        
    - 灰度
        
    - 多环境部署
        

---

# 六、Step 4：把镜像传到服务器

这里有 **两种标准方式**（选其一）

---

## ✅ 方式 A（生产推荐）：使用镜像仓库

### 1️⃣ 登录仓库

`docker login registry.example.com`

### 2️⃣ 推送镜像

`docker push registry.example.com/my-app:1.0.0`

### 3️⃣ 服务器拉取

`docker pull registry.example.com/my-app:1.0.0`

### 原理

- Registry = 镜像 CDN
    
- 镜像被拆成 layer
    
- 相同 layer 不重复传输
    
- 天然支持多服务器、回滚
    

---

## ⚠️ 方式 B（无仓库）：save / scp / load

### 本地

`docker save my-app:1.0.0 > my-app.tar scp my-app.tar user@server:/opt/`

### 服务器

`docker load < /opt/my-app.tar`

### 原理

- 镜像打包成 tar
    
- 完整拷贝
    
- 无版本管理、无缓存
    

📌 **只适合内网 / 临时**

---

# 七、Step 5：服务器运行镜像

```
docker run -d \
  --name my-app \
  -p 3000:3000 \
  -e NODE_ENV=production \
  registry.example.com/my-app:1.0.0
```

### 原理说明

- 镜像是只读的
    
- `docker run` 创建 **容器实例**
    
- 环境变量、端口、数据卷 = 运行态注入
    

---

# 八、Step 6：升级 / 回滚（生产必备）

## 升级

```
docker pull registry.example.com/my-app:1.0.1
docker stop my-app
docker rm my-app
docker run ... my-app:1.0.1
```

## 回滚

`docker run ... my-app:1.0.0`

### 原理

- 镜像不可变
    
- 切换版本 = 切换 tag
    
- 不存在“环境不一致”
    

---

# 九、docker-compose（真实生产常用）

### docker-compose.yml（服务器）

```
version: "3.9"
services:
  web:
    image: registry.example.com/my-app:1.0.0
    ports:
      - "3000:3000"
    env_file:
      - .env
    restart: always

```

`docker compose up -d`

### 原理

- 声明式
    
- 服务定义 = 基础设施代码
    
- 可复现部署
