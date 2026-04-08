# Nginx Docker 挂载建议（模板）

建议在现有网关 Nginx 容器中新增只读挂载：

- 博客发布目录：`/home/ubuntu/blog-site -> /usr/share/nginx/html/blog`
- 证书目录：`/home/ubuntu/certs/your-domain.com -> /etc/nginx/cert`

示例（片段）：

```yaml
services:
  nginx:
    volumes:
      - /home/ubuntu/blog-site:/usr/share/nginx/html/blog:ro
      - /home/ubuntu/certs/your-domain.com:/etc/nginx/cert:ro
```

替换配置后建议执行：

```bash
docker exec -it <nginx_container> nginx -t
docker exec -it <nginx_container> nginx -s reload
```
