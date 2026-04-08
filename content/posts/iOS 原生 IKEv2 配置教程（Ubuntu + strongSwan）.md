---
title: "iOS 原生 IKEv2 配置教程（Ubuntu + strongSwan）"
date: 2026-04-08T10:42:50+08:00
tags:
  - Ubuntu
  - Windows
  - 部署
draft: false
---

## 前言

这篇文章记录如何在 Ubuntu 服务器上部署一套可供 iPhone 原生使用的 `IKEv2/IPsec` 服务。

适用场景：

-   希望使用 iPhone 系统自带 IKEv2 功能
-   不想安装第三方客户端
-   服务器系统为 Ubuntu 24.04 或相近版本
-   服务端使用 `strongSwan`

本文使用脱敏示例，发布时请将下列占位符替换为你自己的信息：

-   `<SERVER_IP>`：服务器公网 IP
-   `<USERNAME>`：IKEv2 用户名
-   `<PASSWORD>`：IKEv2 密码
-   `<SUBNET>`：IKEv2 虚拟网段，例如 `10.20.20.0/24`
-   `<CLIENT_IP_POOL>`：客户端地址池，例如 `10.20.20.0/24`
-   `<NET_IFACE>`：服务器公网网卡名，例如 `eth0`

## 方案说明

本方案使用：

-   协议：`IKEv2/IPsec`
-   服务端：`strongSwan`
-   认证方式：`EAP-MSCHAPv2`（用户名 + 密码）
-   证书方式：自签 CA + 服务端证书
-   客户端：iPhone 系统自带 IKEv2

如果你没有域名，也可以直接用裸 IP 部署，但需要：

-   服务端证书中的 `CN` 和 `SAN` 使用服务器 IP
-   iPhone 上的 `服务器` 和 `远程ID` 也填写同一个 IP
-   手动将自签 CA 证书导入 iPhone 并开启完全信任

## 一、安装 strongSwan

更新软件源并安装依赖：

```
sudo apt update
sudo apt install -y strongswan strongswan-pki libcharon-extra-plugins iptables-persistent
```

放行 IKEv2 常用端口：

```
sudo ufw allow 500/udp
sudo ufw allow 4500/udp
```

如果服务器未启用 `ufw`，也可以只在云安全组中放行 `UDP 500` 和 `UDP 4500`。

## 二、生成 CA 和服务端证书

创建证书目录：

```
sudo mkdir -p "/etc/ipsec.d/private" "/etc/ipsec.d/cacerts" "/etc/ipsec.d/certs"
```

生成 CA 私钥和 CA 证书：

```
sudo ipsec pki --gen --type rsa --size 4096 --outform pem | sudo tee "/etc/ipsec.d/private/ca-key.pem" > /dev/null

sudo ipsec pki --self --ca --lifetime 3650 \
  --in "/etc/ipsec.d/private/ca-key.pem" --type rsa \
  --dn "CN=My IKEv2 CA" --outform pem | sudo tee "/etc/ipsec.d/cacerts/ca-cert.pem" > /dev/null
```

生成服务端私钥和服务端证书：

```
sudo ipsec pki --gen --type rsa --size 4096 --outform pem | sudo tee "/etc/ipsec.d/private/server-key.pem" > /dev/null

sudo ipsec pki --pub --in "/etc/ipsec.d/private/server-key.pem" --type rsa | \
sudo ipsec pki --issue --lifetime 1825 \
  --cacert "/etc/ipsec.d/cacerts/ca-cert.pem" \
  --cakey "/etc/ipsec.d/private/ca-key.pem" \
  --dn "CN=<SERVER_IP>" \
  --san "<SERVER_IP>" \
  --flag serverAuth --flag ikeIntermediate \
  --outform pem | sudo tee "/etc/ipsec.d/certs/server-cert.pem" > /dev/null
```

设置权限：

```
sudo chmod 600 "/etc/ipsec.d/private/ca-key.pem" "/etc/ipsec.d/private/server-key.pem"
sudo chmod 644 "/etc/ipsec.d/cacerts/ca-cert.pem" "/etc/ipsec.d/certs/server-cert.pem"
```

验证文件是否存在：

```
sudo ls -l "/etc/ipsec.d/private/ca-key.pem" "/etc/ipsec.d/cacerts/ca-cert.pem" "/etc/ipsec.d/private/server-key.pem" "/etc/ipsec.d/certs/server-cert.pem"
```

## 三、配置 strongSwan

写入 `/etc/ipsec.conf`：

```
sudo tee "/etc/ipsec.conf" > /dev/null <<'EOF'
config setup
  uniqueids=never

conn ios-ikev2
  keyexchange=ikev2
  ike=aes256-sha256-modp2048,aes128-sha256-modp2048!
  esp=aes256-sha256,aes128-sha256!
  dpdaction=clear
  dpddelay=300s
  rekey=no
  left=%any
  leftid=<SERVER_IP>
  leftcert=server-cert.pem
  leftsendcert=always
  leftsubnet=0.0.0.0/0
  right=%any
  rightid=%any
  rightauth=eap-mschapv2
  rightsourceip=<CLIENT_IP_POOL>
  rightdns=1.1.1.1,8.8.8.8
  eap_identity=%identity
  auto=add
EOF
```

写入 `/etc/ipsec.secrets`：

```
sudo tee "/etc/ipsec.secrets" > /dev/null <<'EOF'
: RSA "server-key.pem"
<USERNAME> : EAP "<PASSWORD>"
EOF
```

说明：

-   `leftid` 必须与证书中的 `CN` / `SAN` 一致。
-   如果你使用裸 IP，则 iPhone 端的 `服务器` 和 `远程ID` 也必须填写同一个 IP。

## 四、开启 IP 转发

创建 sysctl 配置：

```
sudo tee "/etc/sysctl.d/99-ikev2.conf" > /dev/null <<'EOF'
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1
EOF

sudo sysctl --system
```

检查是否生效：

```
sysctl net.ipv4.ip_forward
```

期望输出：

```
net.ipv4.ip_forward = 1
```

## 五、配置 NAT 和转发规则

先查看默认公网网卡：

```
ip route | awk '/default/ {print $5; exit}'
```

假设结果为 `<NET_IFACE>`，添加 NAT：

```
sudo iptables -t nat -A POSTROUTING -s <SUBNET> -o <NET_IFACE> -j MASQUERADE
```

添加转发规则：

```
sudo iptables -I FORWARD 1 -s <SUBNET> -j ACCEPT
sudo iptables -I FORWARD 1 -d <SUBNET> -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
```

保存规则：

```
sudo netfilter-persistent save
```

检查规则：

```
sudo iptables -t nat -S
sudo iptables -S FORWARD
```

期望至少存在：

```
-A POSTROUTING -s <SUBNET> -o <NET_IFACE> -j MASQUERADE
-A FORWARD -d <SUBNET> -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A FORWARD -s <SUBNET> -j ACCEPT
```

## 六、启动 strongSwan

```
sudo systemctl restart strongswan-starter
sudo systemctl enable strongswan-starter
```

检查服务状态：

```
sudo ipsec statusall
sudo ss -lunp | grep -E ':(500|4500)\b'
```

正常状态通常包括：

-   strongSwan 已监听 `UDP 500` 和 `UDP 4500`
-   IKEv2 连接建立后 `Security Associations` 显示 `1 up`

## 七、导出 CA 证书并安装到 iPhone

导出证书到当前用户目录：

```
cp "/etc/ipsec.d/cacerts/ca-cert.pem" "$HOME/ca-cert.cer"
```

如果需要下载到 Windows：

```
scp "ubuntu@<SERVER_IP>:/home/ubuntu/ca-cert.cer" "C:\Users\YourName\Desktop\ca-cert.cer"
```

然后通过微信、邮件、AirDrop 等方式把 `ca-cert.cer` 发到 iPhone。

iPhone 上安装步骤：

1.  下载证书到文件
2.  打开 `设置 -> 通用 -> magic与设备管理 -> 配置描述文件` 完成安装
3.  打开 `设置 -> 通用 -> 关于本机 -> 证书信任设置`
4.  找到刚安装的 CA，开启“完全信任”

注意：

-   只安装证书不够
-   必须手动开启完全信任，否则 IKEv2 无法通过证书校验

## 八、iPhone 端 IKEv2 填写方法

在 iPhone 中进入：  
`设置 -> 通用 -> magic 与设备管理 -> 添加配置`

填写如下：

-   类型：`IKEv2`
-   描述：自定义，例如 `MyIKEv2`
-   服务器：`<SERVER_IP>`
-   远程ID：`<SERVER_IP>`
-   本地ID：留空
-   用户鉴定：`用户名`
-   用户名：`<USERNAME>`
-   密码：`<PASSWORD>`
-   代理：`关闭`

## 九、连接后如何验证

连接成功后，建议按顺序测试：

1.  访问 `https://1.1.1.1`
2.  访问 `https://8.8.8.8`
3.  访问 `https://google.com`

判断方法：

-   如果 IP 地址能访问，但域名不能访问，优先检查 DNS 配置
-   如果 IP 地址也不能访问，优先检查 NAT、FORWARD、云安全组、防火墙

服务器端可以通过以下命令查看状态：

```
sudo ipsec statusall
```

重点观察：

-   `Security Associations (1 up, 0 connecting)`
-   `bytes_i` 和 `bytes_o` 是否都在增长

如果出现：

-   `bytes_i` 有增长
-   `bytes_o = 0`

通常说明：

-   客户端流量已到服务器
-   但服务器没有把响应流量正确转发回客户端
-   优先检查 `FORWARD` 和 `MASQUERADE`

## 十、常见问题

### 1. 证书生成时报 `Permission denied`

错误示例：

```
sudo ipsec pki ... > /etc/ipsec.d/...
```

原因：

-   `>` 重定向由当前 shell 执行，不会跟随 `sudo` 提权

解决：

-   使用 `sudo tee` 写入文件

### 2. 连接成功但无法访问任何网站

常见原因：

-   未开启 IP 转发
-   缺少 NAT
-   缺少 FORWARD 放行规则
-   云安全组未放通必要端口

重点检查：

```
sysctl net.ipv4.ip_forward
sudo iptables -t nat -S
sudo iptables -S FORWARD
sudo ipsec statusall
```

### 3. 连接成功但只能访问 IP，不能访问域名

优先检查：

-   `/etc/ipsec.conf` 中的 `rightdns`
-   iPhone 是否拿到 magic DNS

可用示例：

```
rightdns=1.1.1.1,8.8.8.8
```

### 4. `plugin 'xxx': failed to load`

strongSwan 在证书生成或启动时，可能会输出部分可选插件未加载的警告。

通常只要满足以下条件，就可以继续：

-   核心证书文件已成功生成
-   `strongSwan` 可以正常启动
-   IKEv2 可以正常建立连接

## 十一、建议

如果只是自用，裸 IP + 自签 CA 的方式已经可以正常工作。

如果后续需要更稳定、更易维护，建议逐步升级到：

1.  使用域名而不是裸 IP
2.  使用公网可信证书而不是自签 CA
3.  将 `iptables` 规则固化到统一的防火墙策略中
4.  为不同设备分别创建独立账号

## 十二、总结

这套方案的核心点并不复杂，真正容易踩坑的地方主要有三个：

1.  证书身份必须与 iPhone 中填写的 `服务器` / `远程ID` 完全一致
2.  自签 CA 必须手动安装到 iPhone，并开启完全信任
3.  IKEv2 连接成功后，还必须确保服务器已完成 IP 转发、NAT 和 FORWARD 放行

只要这三部分都正确，iPhone 系统自带的 IKEv2 一般就可以稳定工作。
