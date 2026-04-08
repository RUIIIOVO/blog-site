---
title: "3X-UI 配置"
date: 2026-04-08T10:33:58+08:00
draft: false
---

前提：购买一台境外服务器，最好是美国节点，便于访问ai网站（如Gemini、Claude）

1. 切换root账户 进行安装
```
su root

bash <(curl -Ls https://raw.githubusercontent.com/MHSanaei/3x-ui/master/install.sh)
```

2. 出现下面的提示时，输入y确定
```
Would you like to customize the Panel Port settings? (If not, a random port will be applied) [y/n]: y
```

3. 根据提示设置3X-UI的面板端口
```
Please set up the panel port: 54321

Your Panel Port is: 54321

Port set successfully: 54321

Username and password updated successfully

Base URI path set successfully
```

4. 选择2模式，然后一路按回车就完事了
```
Choose SSL certificate setup method:

1. Let's Encrypt for Domain (90-day validity, auto-renews)

2. Let's Encrypt for IP Address (6-day validity, auto-renews)

Note: Both options require port 80 open. IP certs use shortlived profile.

Choose an option (default 2 for IP): 2

Using Let's Encrypt for IP certificate (shortlived profile)...

Do you have an IPv6 address to include? (leave empty to skip): 

Setting up Let's Encrypt IP certificate (shortlived profile)...

Note: IP certificates are valid for ~6 days and will auto-renew.

Port 80 must be open and accessible from the internet.

Installing acme.sh for SSL certificate management...

acme.sh installed successfully

```

5. 重置管理员账号密码，root账户下，输入 `x-ui` 进入控制终端，输入6，如下
![Pasted image 20260226100243](/uploads/Pasted%20image%2020260226100243.png)

6. 开启 54321、443 端口
```
sudo ufw allow 54321,443/tcp

sudo ufw status
```

7. 在腾讯云/阿里云/ucloud 防火墙中开放54321、443端口
![Pasted image 20260226100527](/uploads/Pasted%20image%2020260226100527.png)

8. 访问x-ui面板，root账户输入 `x-ui settings` 复制Access URL，在浏览器中访问
```
root@10-11-183-195:/home/ubuntu# x-ui settings
The OS release is: ubuntu
[INF] current panel settings as follows:
Panel is secure with SSL
hasDefaultCredential: false
port: 54321
webBasePath: /jctEtK95lYLdk8BmSc/ 
Access URL: https://你的IP地址:54321/jctEtK95lYLdk8BmSc/
```

9. x-ui面板配置
输入账户密码，进入面板，点击入站列表，点击添加入站
端口：443
安全选择 Reality 
Target 输入www.microsoft.com:443
SNI 输入 www.microsoft.com
![Pasted image 20260226105631](/uploads/Pasted%20image%2020260226105631.png)
点击Get New Cert以及Get New Seed，生成公钥私钥，这里还会自动生成Short IDs，后续配置yaml会用到
![Pasted image 20260226105720](/uploads/Pasted%20image%2020260226105720.png)
点击完成

点击添加客户端，可以修改下电子邮箱，推荐修改为用户名方便区分，这里的ID后续配置yaml会用到，点击添加客户端按钮即可：
![Pasted image 20260226105841](/uploads/Pasted%20image%2020260226105841.png)

10. 下载clash verge
	官网： [https://github.com/clash-verge-rev/clash-verge-rev/releases](https://www.clashverge.dev/install.html)
	Github地址： [https://github.com/clash-verge-rev/clash-verge-rev/releases](https://github.com/clash-verge-rev/clash-verge-rev/releases)

11. clash verge配置
本地使用记事本新建一个文件，将下方配置粘贴进去并修改，然后将文件名后缀改为yaml
**需要修改：服务器IP、uuid、public-key、short-id**
这里是两个节点的配置，做了基础的规则配置，若需要修改节点数量或者修改规则可以让ai改一下
```yaml
# 端口和基础设置

mixed-port: 7890

allow-lan: true

mode: rule

log-level: info

ipv6: false # 建议关闭，防止DNS泄露

  

# DNS 设置 (优化：引入 DoH 防污染与国内外分流)

dns:

  enable: true

  listen: 0.0.0.0:53

  enhanced-mode: fake-ip

  fake-ip-range: 198.18.0.1/16

  nameserver:

    - https://doh.pub/dns-query        # 腾讯 DoH，防劫持

    - https://dns.alidns.com/dns-query # 阿里 DoH

  fallback:

    - https://dns.google/dns-query     # Google DoH (用于解析国外域名)

    - https://cloudflare-dns.com/dns-query

  fallback-filter:

    geoip: true

    geoip-code: CN

  

# 代理组策略 (优化：增加 AI 专属分组，修复自动选择逻辑)

proxy-groups:

  - name: 🚀 节点选择

    type: select

    proxies:

      - 🌍 自动选择

      - "美国"

      - "新加坡"

      - DIRECT

  

  - name: 🤖 AI 服务

    type: select

    proxies:

      - "美国"      # AI 服务通常对美国原生 IP 支持更好，建议默认放前面

      - "新加坡"

      - 🚀 节点选择

  

  - name: 🌍 自动选择

    type: url-test

    url: http://www.gstatic.com/generate_204

    interval: 300

    tolerance: 50

    proxies:

      - "美国"

      - "新加坡"

  

# 代理节点配置 (保持不变)

proxies:

  - name: "美国"

    type: vless

    server: 服务器IP地址

    port: 443

    uuid: x-ui面板中的用户id，见步骤9

    network: tcp

    tls: true

    udp: true

    flow: xtls-rprx-vision

    servername: www.microsoft.com

    client-fingerprint: chrome

    reality-opts:

      public-key: x-ui面板中的站点公钥，见步骤9

      short-id: 对应x-ui面板中的Short IDs，注意Short IDs是用逗号隔开的，这里只需要复制一个id，见步骤9

  

  - name: "新加坡"

    type: vless

    server: 服务器IP地址

    port: 443

    uuid: x-ui面板中的用户id，见步骤9

    network: tcp

    tls: true

    udp: true

    flow: xtls-rprx-vision

    servername: www.microsoft.com

    client-fingerprint: chrome

    reality-opts:

      public-key: x-ui面板中的站点公钥，见步骤9

      short-id: 对应x-ui面板中的Short IDs，注意Short IDs是用逗号隔开的，这里只需要复制一个id，见步骤9

  

# 规则设置 (优化：完善 AI、开发工具及局域网规则)

rules:

  # 1. 局域网防环路直连 (非常重要，防止本地开发服务走代理)

  - DOMAIN-SUFFIX,local,DIRECT

  - IP-CIDR,127.0.0.0/8,DIRECT

  - IP-CIDR,192.168.0.0/16,DIRECT

  - IP-CIDR,10.0.0.0/8,DIRECT

  - IP-CIDR,172.16.0.0/12,DIRECT

  

  # 2. 🤖 核心 AI 服务 (单独走 AI 策略组)

  - DOMAIN-SUFFIX,openai.com,🤖 AI 服务

  - DOMAIN-SUFFIX,chatgpt.com,🤖 AI 服务

  - DOMAIN-SUFFIX,anthropic.com,🤖 AI 服务    # Claude

  - DOMAIN-SUFFIX,claude.ai,🤖 AI 服务

  - DOMAIN-KEYWORD,gemini,🤖 AI 服务          # Google Gemini

  - DOMAIN-SUFFIX,midjourney.com,🤖 AI 服务

  - DOMAIN-SUFFIX,discord.com,🤖 AI 服务       # Midjourney 强依赖 Discord

  - DOMAIN-SUFFIX,huggingface.co,🤖 AI 服务   # 开源 AI 社区

  - DOMAIN-SUFFIX,civitai.com,🤖 AI 服务      # AI 绘图模型社区

  

  # 3. 👨‍💻 开发者与技术依赖

  - DOMAIN-SUFFIX,github.com,🚀 节点选择

  - DOMAIN-SUFFIX,githubusercontent.com,🚀 节点选择

  - DOMAIN-SUFFIX,docker.com,🚀 节点选择       # 解决 Docker pull 镜像慢/失败问题

  - DOMAIN-SUFFIX,docker.io,🚀 节点选择

  - DOMAIN-SUFFIX,stackoverflow.com,🚀 节点选择

  

  # 4. 🌍 常见国外服务

  - DOMAIN-SUFFIX,google.com,🚀 节点选择

  - DOMAIN-SUFFIX,googleapis.com,🚀 节点选择

  - DOMAIN-SUFFIX,youtube.com,🚀 节点选择

  - DOMAIN-SUFFIX,twitter.com,🚀 节点选择

  - DOMAIN-SUFFIX,x.com,🚀 节点选择

  - DOMAIN-SUFFIX,telegram.org,🚀 节点选择

  

  # 5. 🇨🇳 国内流量直连

  - GEOSITE,cn,DIRECT      # 依赖 Clash Meta 的 Geo 数据，精确匹配国内域名

  - GEOIP,CN,DIRECT

  - DOMAIN-SUFFIX,cn,DIRECT

  

  # 6. 兜底规则 (剩下的全部走代理)

  - MATCH,🚀 节点选择
```
安装clash verge后，点击左侧导航栏的订阅，点击新建，选择local，选择刚刚编辑好的yaml文件
![Pasted image 20260226110820](/uploads/Pasted%20image%2020260226110820.png)
保存后可以进行测试，没有显示红色的Timeout就大功告成了
![Pasted image 20260226112017](/uploads/Pasted%20image%2020260226112017.png)
最后推荐在clash verge里开启虚拟网卡以及tun模式，这样能正常访问cursor或Antigravity
![Pasted image 20260226112159](/uploads/Pasted%20image%2020260226112159.png)
