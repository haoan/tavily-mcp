#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import axios from "axios";

const API_KEY = process.env.TAVILY_API_KEY;
const BASE_URL = "https://api.tavily.com";

const server = new McpServer({
  name: "tavily-mcp",
  version: "1.0.0",
});

// 搜索工具（完整参数）
server.tool(
  "search",
  "搜索互联网（支持 AI 摘要、域名过滤、新闻搜索等）",
  {
    query: z.string().describe("搜索关键词"),
    search_depth: z.enum(["basic", "advanced"]).optional().default("basic").describe("搜索深度：basic 快速，advanced 详细"),
    max_results: z.number().optional().default(5).describe("最大结果数（1-20）"),
    include_answer: z.boolean().optional().default(true).describe("是否包含 AI 摘要"),
    include_raw_content: z.boolean().optional().default(false).describe("是否包含原始网页内容"),
    include_images: z.boolean().optional().default(false).describe("是否包含图片"),
    include_domains: z.array(z.string()).optional().default([]).describe("只搜索这些域名"),
    exclude_domains: z.array(z.string()).optional().default([]).describe("排除这些域名"),
    topic: z.enum(["general", "news"]).optional().default("general").describe("搜索类型：general 通用，news 新闻"),
    days: z.number().optional().describe("新闻搜索时限制天数"),
  },
  async (params) => {
    if (!API_KEY) {
      return { content: [{ type: "text", text: "错误：未配置 TAVILY_API_KEY" }] };
    }
    try {
      const { data } = await axios.post(`${BASE_URL}/search`, {
        api_key: API_KEY,
        ...params,
      });
      let result = `搜索：${params.query}\n\n`;
      if (data.answer) result += `AI 摘要：${data.answer}\n\n`;
      if (data.images?.length) {
        result += `图片：\n`;
        data.images.forEach((img, i) => result += `  ${i + 1}. ${img}\n`);
        result += `\n`;
      }
      result += `搜索结果：\n`;
      data.results?.forEach((r, i) => {
        result += `${i + 1}. ${r.title}\n`;
        result += `   URL: ${r.url}\n`;
        result += `   ${r.content?.substring(0, 200)}...\n`;
        if (r.raw_content) result += `   原始内容: ${r.raw_content.substring(0, 300)}...\n`;
        result += `\n`;
      });
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `搜索失败：${e.message}` }] };
    }
  }
);

// 抓取工具（完整参数）
server.tool(
  "extract",
  "抓取网页内容（支持深度抓取、图片提取）",
  {
    urls: z.array(z.string()).describe("要抓取的 URL 列表"),
    include_images: z.boolean().optional().default(false).describe("是否包含图片"),
    extract_depth: z.enum(["basic", "advanced"]).optional().default("basic").describe("抓取深度：basic 快速，advanced 详细（支持 JS 渲染）"),
  },
  async (params) => {
    if (!API_KEY) {
      return { content: [{ type: "text", text: "错误：未配置 TAVILY_API_KEY" }] };
    }
    try {
      const { data } = await axios.post(`${BASE_URL}/extract`, {
        api_key: API_KEY,
        ...params,
      });
      let result = `网页抓取结果：\n\n`;
      data.results?.forEach((r, i) => {
        result += `### ${i + 1}. ${r.url}\n`;
        result += `${r.raw_content?.substring(0, 2000)}\n\n`;
        if (r.images?.length) {
          result += `图片：\n`;
          r.images.forEach((img, j) => result += `  ${j + 1}. ${img}\n`);
          result += `\n`;
        }
      });
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `抓取失败：${e.message}` }] };
    }
  }
);

// 快速搜索（简化版）
server.tool(
  "quick_search",
  "快速搜索（返回简洁结果）",
  {
    query: z.string().describe("搜索关键词"),
  },
  async ({ query }) => {
    if (!API_KEY) {
      return { content: [{ type: "text", text: "错误：未配置 TAVILY_API_KEY" }] };
    }
    try {
      const { data } = await axios.post(`${BASE_URL}/search`, {
        api_key: API_KEY,
        query,
        max_results: 3,
        include_answer: true,
      });
      let result = "";
      if (data.answer) result += `${data.answer}\n\n`;
      data.results?.forEach((r, i) => {
        result += `${i + 1}. ${r.title} - ${r.url}\n`;
      });
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `搜索失败：${e.message}` }] };
    }
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
