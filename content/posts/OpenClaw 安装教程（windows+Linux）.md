---
title: "OpenClaw 安装教程（windows+Linux）"
date: 2026-04-08T10:42:50+08:00
tags:
  - Linux
  - Ubuntu
  - Windows
draft: false
---


官方文档：[https://docs.openclaw.ai/start/getting-started](https://docs.openclaw.ai/start/getting-started)
需要先安装node22 使用nvm安装
windows使用下面的命令会自动安装node22，linux则需要自行手动安装，并安装git
安装命令
windows： 
```
iwr -useb https://openclaw.ai/install.ps1 | iex
```
linux/mac：
```
curl -fsSL https://openclaw.ai/install.sh | bash
```

运行引导程序（并安装服务）：
```
openclaw onboard --install-daemon
```
安装过程可参考 [https://developer.aliyun.com/article/1709615](https://developer.aliyun.com/article/1709615) 这篇文章，其中有些命令是旧版本的，例如clawdbot status，正确的是openclaw status
选择quickstart qwen模型，其他的则跳过，最后一步选择TUI，选择后会自动在后台运行openclaw，类似nohup

常用命令：
```
查看状态
openclaw status
启动网关
openclaw gateway
重启网关（修改openclaw.json后执行）
openclaw gateway restart
查看仪表盘网址
openclaw dashboard
检查修复
openclaw doctor --fix
引导配置
openclaw onboard
```

windows使用powershell执行即可，执行完成后，输入 `openclaw dashboard` 查看网址，复制Dashboard URL查看即可，若访问的是没有token的url，直接访问 127.0.0.1:18789 则会出现 `disconnected (1008): device identity required` 


linux本机部署后，默认是在服务器内网环境的，可以进行端口映射，实现外网访问
1. 修改openclaw.json，添加controlUi 并将gateway下的bind由loopback 改为lan
```
    "controlUi": {
      "allowInsecureAuth": true
    },
    "bind": "lan",
```
完整gateway：
```
  "gateway": {
    "controlUi": {
      "allowInsecureAuth": true
    },
    "auth": {
      "mode": "token",
      "token": "你的token"
    },
    "mode": "local",
    "port": 18789,
    "bind": "lan",
    "tailscale": {
      "mode": "off",
      "resetOnExit": false
    }
  },
```

修改后需要重启网关，执行：`openclaw gateway restart`

2. 腾讯云、服务器内部开放tcp端口（18789端口）
ufw 方式开放端口：
```
sudo apt install ufw
sudo ufw status
sudo ufw enable
sudo ufw allow 18789/tcp
```

3. 访问 服务器IP:18789/?token=XXXX  （token通过`openclaw dashboard` 查看）



完整openclaw.json：
```
ubuntu@VM-0-7-ubuntu:~$ cat  ~/.openclaw/openclaw.json
{
  "meta": {
    "lastTouchedVersion": "2026.2.1",
    "lastTouchedAt": "2026-02-04T01:38:02.479Z"
  },
  "wizard": {
    "lastRunAt": "2026-02-04T01:38:02.475Z",
    "lastRunVersion": "2026.2.1",
    "lastRunCommand": "onboard",
    "lastRunMode": "local"
  },
  "commands": {
    "native": "auto",
    "nativeSkills": "auto"
  },
  "gateway": {
    "controlUi": {
      "allowInsecureAuth": true
    },
    "auth": {
      "mode": "token",
      "token": "你的token"
    },
    "mode": "local",
    "port": 18789,
    "bind": "lan",
    "tailscale": {
      "mode": "off",
      "resetOnExit": false
    }
  },
  "agents": {
    "defaults": {
      "maxConcurrent": 4,
      "subagents": {
        "maxConcurrent": 8
      },
      "workspace": "/home/ubuntu/.openclaw/workspace",
      "models": {
        "qwen-portal/coder-model": {
          "alias": "qwen"
        },
        "qwen-portal/vision-model": {}
      },
      "model": {
        "primary": "qwen-portal/vision-model"
      }
    }
  },
  "messages": {
    "ackReactionScope": "group-mentions"
  },
  "plugins": {
    "entries": {
      "qwen-portal-auth": {
        "enabled": true
      }
    }
  },
  "models": {
    "providers": {
      "qwen-portal": {
        "baseUrl": "https://portal.qwen.ai/v1",
        "apiKey": "qwen-oauth",
        "api": "openai-completions",
        "models": [
          {
            "id": "coder-model",
            "name": "Qwen Coder",
            "reasoning": false,
            "input": [
              "text"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 128000,
            "maxTokens": 8192
          },
          {
            "id": "vision-model",
            "name": "Qwen Vision",
            "reasoning": false,
            "input": [
              "text",
              "image"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 128000,
            "maxTokens": 8192
          }
        ]
      }
    }
  },
  "auth": {
    "profiles": {
      "qwen-portal:default": {
        "provider": "qwen-portal",
        "mode": "oauth"
      }
    }
  }
}
ubuntu@VM-0-7-ubuntu:~$ 

```

在飞书中配置机器人，可参考： [https://developer.aliyun.com/article/1709615](https://developer.aliyun.com/article/1709615) 这篇文章
同样其中的命令需要由clawdbot更换为openclaw，如下：

```
openclaw plugins install @m1heng-clawd/feishu

openclaw config set channels.feishu.appId "飞书 app id"

openclaw config set channels.feishu.appSecret "飞书 app secret"

openclaw config set channels.feishu.enabled true

# 推荐使用 websocket
openclaw config set channels.feishu.connectionMode websocket

openclaw config set channels.feishu.dmPolicy pairing

openclaw config set channels.feishu.groupPolicy allowlist

openclaw config set channels.feishu.requireMention true

openclaw gateway restart

```
注意：若只是个人使用，使用飞书个人版创建即可，若需要分享给好友，则需要在飞书创建企业后再创建机器人，飞书个人版无法将机器人分享给其他人
