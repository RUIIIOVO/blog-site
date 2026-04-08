# blog-site

基于 `Hugo + PaperMod` 的博客仓库，支持：

- 从 WebDAV 同步文章与图片
- 本地构建 `public/`
- 通过 `rsync + 软链接切换` 发布到 Ubuntu 服务器
- 由网关 Nginx 提供 HTTPS 与反向代理

---

## 1. 固定部署路径（按当前线上）

- 博客目录：`/home/ubuntu/blog-site`
- 证书目录：`/home/ubuntu/certs/your-domain.com`
- Nginx 容器内博客挂载：`/usr/share/nginx/html/blog`
- Nginx 容器内证书挂载：`/etc/nginx/cert`

---

## 2. 仓库结构

- `content/posts/`：同步后的文章 Markdown
- `static/uploads/`：同步后的图片资源
- `scripts/sync_webdav.py`：WebDAV 同步脚本
- `scripts/upload_cert.ps1`：证书上传脚本（Windows PowerShell）
- `deploy/nginx/your-domain.com.conf`：Nginx 完整配置样例
- `.github/workflows/sync-build-deploy.yml`：自动同步 + 构建 + 部署

---

## 3. 本地开发与构建

### 3.1 安装依赖

```bash
pip install -r "scripts/requirements.txt"
```

安装 Hugo Extended（建议 `>= 0.125`）。

### 3.2 准备环境变量

```bash
cp ".env.example" ".env"
```

编辑仓库根目录 `.env`，填入真实值（变量含义见本文第 8 节）。

### 3.3 本地同步（可选）

预演（不落盘）：

```bash
python "scripts/sync_webdav.py" --dry-run
```

正式同步：

```bash
python "scripts/sync_webdav.py"
```

`scripts/sync_webdav.py` 会自动把 Obsidian 图片语法 `![[xxx.png]]` 转换成 Hugo 可渲染的标准 Markdown 图片链接（默认映射到 `/uploads/`）。

### 3.4 本地构建

```bash
hugo --minify
```

如果你要强制指定线上域名构建：

```bash
hugo --minify --baseURL "https://your-domain.com"
```

---

## 4. 服务器一次性初始化

以下命令假设：

- 服务器：`your-server-ip`
- 用户：`ubuntu`
- SSH 端口：`22`

### 4.1 创建目录

```bash
ssh -p "22" "ubuntu@your-server-ip" '
  set -e
  mkdir -p "/home/ubuntu/blog-site/releases"
  mkdir -p "/home/ubuntu/certs/your-domain.com"
  chmod "700" "/home/ubuntu/certs/your-domain.com"
'
```

### 4.2 上传证书

在本地仓库执行：

```powershell
./scripts/upload_cert.ps1 -Host "your-server-ip" -User "ubuntu" -Port "22" -RemoteCertDir "/home/ubuntu/certs/your-domain.com"
```

---

## 5. Nginx 配置修改命令（服务器）

> 当前仓库提供的是完整 Nginx 配置：`deploy/nginx/your-domain.com.conf`。

### 5.1 上传配置到服务器

```bash
scp -P "22" "./deploy/nginx/your-domain.com.conf" "ubuntu@your-server-ip:/home/ubuntu/your-domain.com.conf"
```

### 5.2 Docker Nginx（与本仓库配置匹配，推荐）

1) 先确保你的 Nginx 容器有以下挂载：

```yaml
volumes:
  - /home/ubuntu/rq-mall-single/mydata/nginx/html:/usr/share/nginx/html:rw
  - /home/ubuntu/certs/your-domain.com:/etc/nginx/cert:ro
```

2) 将配置覆盖到容器并重载：

```bash
ssh -p "22" "ubuntu@your-server-ip" '
  set -e
  sudo docker cp "/home/ubuntu/your-domain.com.conf" "nginx:/etc/nginx/nginx.conf"
  sudo docker exec "nginx" nginx -t
  sudo docker exec "nginx" nginx -s reload
'
```

> 如果容器名不是 `nginx`，请替换为你的真实容器名。

### 5.3 宿主机 Nginx（如果你不是容器部署）

```bash
ssh -p "22" "ubuntu@your-server-ip" '
  set -e
  sudo cp "/home/ubuntu/your-domain.com.conf" "/etc/nginx/nginx.conf"
  sudo nginx -t
  sudo systemctl reload nginx
'
```

---

## 6. 手动发布流程（完整）

### 6.1 前置环境（本地机器）

手动发布默认在**本地构建、远程服务器只接收静态文件**，因此：

- 本地必需：`hugo`、`ssh`、`scp`
- 本地可选：`rsync`（有就用，没有可用 `scp`）
- 本地可选：`python`（仅在你需要执行 `scripts/sync_webdav.py` 时）
- 服务器必需：可 SSH 登录，且目标目录可写（如 `/home/ubuntu/blog-site`）

先做可用性检查（缺哪个装哪个）：

```bash
hugo version
ssh -V
command -v scp
rsync --version
python --version
```

### 6.2 Bash / Linux / macOS（含 Git Bash）

以下流程可直接在本地执行，发布目录固定到 `/home/ubuntu/blog-site`：

```bash
# 1) 同步内容（可选）
python "scripts/sync_webdav.py"

# 2) 构建
hugo --minify --baseURL "https://your-domain.com"

# 3) 发布到服务器（时间戳版本 + current 软链接切换）
export DEPLOY_HOST="your-server-ip"
export DEPLOY_PORT="22"
export DEPLOY_USER="ubuntu"
export DEPLOY_TARGET_BASE="/home/ubuntu/blog-site"

TS="$(date -u +%Y%m%d%H%M%S)"
RELEASE_DIR="${DEPLOY_TARGET_BASE}/releases/${TS}"

# 3.1 创建 releases 目录（若已存在会跳过）
ssh -p "${DEPLOY_PORT}" "${DEPLOY_USER}@${DEPLOY_HOST}" "mkdir -p \"${RELEASE_DIR}\""

# 3.2 上传构建产物到时间戳版本目录（无需 rsync）
scp -P "${DEPLOY_PORT}" -r "public/." "${DEPLOY_USER}@${DEPLOY_HOST}:${RELEASE_DIR}/"

# 3.3 原子切换 current 软链接到新版本（使用相对软链接，兼容容器挂载）
ssh -p "${DEPLOY_PORT}" "${DEPLOY_USER}@${DEPLOY_HOST}" "cd \"${DEPLOY_TARGET_BASE}\" && ln -sfn \"releases/${TS}\" \"current\""
```

### 6.3 PowerShell（Windows 直接执行）

如果你在 `PowerShell` 里执行，请使用以下等价命令：

```powershell
# 1) 同步内容（可选）
python "scripts/sync_webdav.py"

# 2) 构建
hugo --minify --baseURL "https://your-domain.com"

# 3) 发布到服务器（时间戳版本 + current 软链接切换）
$env:DEPLOY_HOST = "your-server-ip"
$env:DEPLOY_PORT = "22"
$env:DEPLOY_USER = "ubuntu"
$env:DEPLOY_TARGET_BASE = "/home/ubuntu/blog-site"
$KEY = "$env:USERPROFILE/.ssh/id_ed25519"

$TS = (Get-Date).ToUniversalTime().ToString("yyyyMMddHHmmss")
$RELEASE_DIR = "$($env:DEPLOY_TARGET_BASE)/releases/$TS"
$DEST = "{0}@{1}:{2}/" -f $env:DEPLOY_USER, $env:DEPLOY_HOST, $RELEASE_DIR

ssh -o "IdentitiesOnly=yes" -i "$KEY" -p "$env:DEPLOY_PORT" "$env:DEPLOY_USER@$env:DEPLOY_HOST" "mkdir -p $RELEASE_DIR"
scp -o "IdentitiesOnly=yes" -i "$KEY" -P "$env:DEPLOY_PORT" -r "public/." "$DEST"
ssh -o "IdentitiesOnly=yes" -i "$KEY" -p "$env:DEPLOY_PORT" "$env:DEPLOY_USER@$env:DEPLOY_HOST" "cd $($env:DEPLOY_TARGET_BASE) && ln -sfn releases/$TS current"
```

### 6.4 一条命令发布（推荐，PowerShell）

```powershell
./scripts/deploy.ps1
```

可选参数示例：

```powershell
./scripts/deploy.ps1 `
  -DeployHost "your-server-ip" `
  -DeployPort "22" `
  -DeployUser "ubuntu" `
  -DeployTargetBase "/home/ubuntu/blog-site" `
  -BaseUrl "https://your-domain.com" `
  -KeyPath "$env:USERPROFILE/.ssh/id_ed25519"
```

发布后验证：

```bash
curl -I "https://your-domain.com"
```

---

## 7. GitHub Actions 自动部署（可选）

CI 不读取仓库内 `.env`，只读取 GitHub Secrets。  
配置位置：`GitHub 仓库 -> Settings -> Secrets and variables -> Actions`

最少需要以下 secrets：

- WebDAV：`WEBDAV_BASE_URL`、`WEBDAV_USERNAME`、`WEBDAV_PASSWORD`、`WEBDAV_POSTS_PATH`、`WEBDAV_ASSETS_PATH`
- 部署：`DEPLOY_HOST`、`DEPLOY_PORT`、`DEPLOY_USER`、`DEPLOY_SSH_KEY`、`DEPLOY_TARGET_BASE`
- 站点：`SITE_URL`、`TZ`
- 可选：`GISCUS_*`、`ANALYTICS_*`

---

## 8. `.env` 变量说明（做什么 + 在哪里配置）

`.env` 文件位置：仓库根目录（与 `hugo.toml` 同级）。

| 变量 | 作用 | 在哪里配置 |
|---|---|---|
| `WEBDAV_BASE_URL` | WebDAV 根地址 | 本地 `.env`；CI 用 GitHub Secrets |
| `WEBDAV_USERNAME` | WebDAV 用户名 | 本地 `.env`；CI 用 GitHub Secrets |
| `WEBDAV_PASSWORD` | WebDAV 密码 | 本地 `.env`；CI 用 GitHub Secrets |
| `WEBDAV_POSTS_PATH` | WebDAV 中文章目录（如 `/posts`） | 本地 `.env`；CI 用 GitHub Secrets |
| `WEBDAV_ASSETS_PATH` | WebDAV 中图片目录（如 `/assets`） | 本地 `.env`；CI 用 GitHub Secrets |
| `SITE_URL` | 构建时站点 URL（`hugo --baseURL`） | 主要用于 CI Secrets；本地可手动传参 |
| `TZ` | CI 任务时区 | GitHub Secrets |
| `DEPLOY_HOST` | 目标服务器地址 | 本地脚本环境或 CI Secrets |
| `DEPLOY_PORT` | SSH 端口，默认 `22` | 本地脚本环境或 CI Secrets |
| `DEPLOY_USER` | SSH 用户 | 本地脚本环境或 CI Secrets |
| `DEPLOY_TARGET_BASE` | 服务器发布根目录（建议 `/home/ubuntu/blog-site`） | 本地脚本环境或 CI Secrets |
| `GISCUS_ENABLED` | 是否开启 Giscus（`true/false`） | `.env` 或 `hugo.toml` |
| `GISCUS_REPO` | Giscus 仓库（如 `owner/repo`） | `.env` 或 `hugo.toml` |
| `GISCUS_REPO_ID` | Giscus 仓库 ID | `.env` 或 `hugo.toml` |
| `GISCUS_CATEGORY` | Giscus 分类名 | `.env` 或 `hugo.toml` |
| `GISCUS_CATEGORY_ID` | Giscus 分类 ID | `.env` 或 `hugo.toml` |
| `GISCUS_MAPPING` | 映射方式（如 `pathname`） | `.env` 或 `hugo.toml` |
| `GISCUS_STRICT` | 严格匹配（`0/1`） | `.env` 或 `hugo.toml` |
| `GISCUS_REACTIONS_ENABLED` | 是否启用表情反馈（`0/1`） | `.env` 或 `hugo.toml` |
| `GISCUS_EMIT_METADATA` | 是否发送元数据（`0/1`） | `.env` 或 `hugo.toml` |
| `GISCUS_INPUT_POSITION` | 输入框位置（`top/bottom`） | `.env` 或 `hugo.toml` |
| `GISCUS_LANG` | Giscus 语言（如 `zh-CN`） | `.env` 或 `hugo.toml` |
| `GISCUS_LOADING` | 加载策略（如 `lazy`） | `.env` 或 `hugo.toml` |
| `ANALYTICS_ENABLED` | 是否开启统计（`true/false`） | `.env` 或 `hugo.toml` |
| `ANALYTICS_PROVIDER` | 统计服务（`umami/plausible`） | `.env` 或 `hugo.toml` |
| `ANALYTICS_SCRIPT_URL` | 统计脚本 URL | `.env` 或 `hugo.toml` |
| `ANALYTICS_WEBSITE_ID` | Umami 的 website id | `.env` 或 `hugo.toml` |
| `ANALYTICS_DOMAIN` | Plausible 的 `data-domain` | `.env` 或 `hugo.toml` |

### 8.1 优先级说明（非常重要）

`layouts/partials/comments.html` 与 `layouts/partials/extend_head.html` 的逻辑是：  
优先读 `hugo.toml` 的 `params.*`，为空时才回退到环境变量。

所以如果你希望主要用 `.env`/Secrets 控制，建议在 `hugo.toml` 中把对应字段留空或关闭。
