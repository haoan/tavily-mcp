# Tavily MCP

完整的 Tavily 搜索 MCP 服务器。

## 工具

### search（完整版）
搜索互联网，支持所有参数。

| 参数 | 类型 | 说明 |
|------|------|------|
| query | string | 搜索关键词 |
| search_depth | "basic" \| "advanced" | 搜索深度 |
| max_results | number | 最大结果数（1-20） |
| include_answer | boolean | AI 摘要 |
| include_raw_content | boolean | 原始内容 |
| include_images | boolean | 图片 |
| include_domains | string[] | 包含域名 |
| exclude_domains | string[] | 排除域名 |
| topic | "general" \| "news" | 搜索类型 |
| days | number | 新闻天数限制 |

### extract（完整版）
抓取网页内容。

| 参数 | 类型 | 说明 |
|------|------|------|
| urls | string[] | URL 列表 |
| include_images | boolean | 图片 |
| extract_depth | "basic" \| "advanced" | 抓取深度 |

### quick_search（快速版）
快速搜索，返回简洁结果。

| 参数 | 类型 | 说明 |
|------|------|------|
| query | string | 搜索关键词 |

## 配置

1. 获取 API 密钥：https://tavily.com

2. 编辑 `~/.claude/settings.json`：
```json
"mcpServers": {
  "tavily": {
    "type": "stdio",
    "command": "node",
    "args": ["/Users/dong/scripts/tavily-mcp/dist/index.js"],
    "env": {
      "TAVILY_API_KEY": "你的密钥"
    }
  }
}
```

3. 重启 Claude Code

## 构建

```bash
npm run build
```
