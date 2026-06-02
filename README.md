# Tavily MCP

简单的 Tavily 搜索 MCP 服务器（Python 版）。

## 工具

| 工具 | 说明 |
|------|------|
| `search` | 搜索互联网（完整参数） |
| `extract` | 抓取网页内容 |
| `quick_search` | 快速搜索（简洁结果） |

## 安装

```bash
pip install -r requirements.txt
```

## 配置

1. 获取 API 密钥：https://tavily.com

2. 编辑 `~/.claude/settings.json`：
```json
"mcpServers": {
  "tavily": {
    "type": "stdio",
    "command": "python3",
    "args": ["/Users/dong/scripts/tavily-mcp/server.py"],
    "env": {
      "TAVILY_API_KEY": "你的密钥"
    }
  }
}
```

3. 重启 Claude Code
