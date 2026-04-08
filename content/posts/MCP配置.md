---
title: "MCP配置"
date: 2026-04-08T10:42:56+08:00
draft: false
---

https://alekschen.github.io/post/2504-cursor-figma-mcp/
figma mcp 配置：
全局下载，启动本地端口：
```shell
pnpx figma-developer-mcp --figma-api-key=<YOUR_FIGMA_API_KEY>
```
![Pasted image 20251022115557](/uploads/Pasted%20image%2020251022115557.png)
cursor中配置：
```json
{ 
	"mcpServers": { 
		"Figma": { 
			"url": "http://localhost:3333/sse" 
		} 
	} 
}
```

mastergo
```
{

  "mcpServers": {

    "mastergo-magic-mcp": {

      "command": "npx",

      "args": [

        "-y",

        "@mastergo/magic-mcp",

        "--token=<YOUR_MASTERGO_TOKEN>",

        "--url=https://mastergo.com"

      ],

      "env": {

        "NPM_CONFIG_REGISTRY": "https://registry.npmjs.org/"

      }

    }

  }

}
```


mcp-feedback-enhanced：
```
{

  "mcpServers": {

    "mcp-feedback-enhanced": {

      "command": "uvx",

      "args": [

        "mcp-feedback-enhanced@latest"

      ]

    }

  }

}
```

context7：
```
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp@latest"

      ],
      "env": {
        "DEFAULT_MINIMUM_TOKENS": "10000"
      }
    }
  }
}
```


