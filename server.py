#!/usr/bin/env python3
"""Tavily MCP Server - 搜索和抓取网页"""

import os
import sys
import json
import logging
import urllib.request
import urllib.error

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("tavily-mcp")

# 配置
API_KEY = os.getenv("TAVILY_API_KEY")
BASE_URL = "https://api.tavily.com"
TIMEOUT = 30


def validate_api_key() -> None:
    """启动时验证 API Key"""
    if not API_KEY:
        logger.error("未配置 TAVILY_API_KEY 环境变量")
        sys.exit(1)
    logger.info("TAVILY_API_KEY 已配置")


def api_call(endpoint: str, payload: dict) -> dict:
    """调用 Tavily API"""
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{BASE_URL}/{endpoint}",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.readable() else str(e)
        logger.error(f"API 错误 [{e.code}]: {error_body}")
        raise RuntimeError(f"API 请求失败: HTTP {e.code}")
    except urllib.error.URLError as e:
        logger.error(f"网络错误: {e.reason}")
        raise RuntimeError(f"网络连接失败: {e.reason}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析错误: {e}")
        raise RuntimeError(f"API 响应格式错误")


def search(
    query: str,
    search_depth: str = "basic",
    max_results: int = 5,
    include_answer: bool = True,
    include_raw_content: bool = False,
    include_images: bool = False,
    include_domains: list = None,
    exclude_domains: list = None,
    topic: str = "general",
    days: int = None,
) -> str:
    """搜索互联网"""
    payload = {
        "api_key": API_KEY,
        "query": query,
        "search_depth": search_depth,
        "max_results": max_results,
        "include_answer": include_answer,
        "include_raw_content": include_raw_content,
        "include_images": include_images,
        "include_domains": include_domains or [],
        "exclude_domains": exclude_domains or [],
        "topic": topic,
    }
    if days is not None:
        payload["days"] = days

    logger.info(f"搜索: {query}")
    data = api_call("search", payload)

    result = f"搜索：{query}\n\n"
    if data.get("answer"):
        result += f"AI 摘要：{data['answer']}\n\n"
    if data.get("images"):
        result += "图片：\n"
        for i, img in enumerate(data["images"], 1):
            result += f"  {i}. {img}\n"
        result += "\n"
    result += "搜索结果：\n"
    for i, r in enumerate(data.get("results", []), 1):
        content = r.get("content", "")
        result += f"{i}. {r['title']}\n"
        result += f"   URL: {r['url']}\n"
        if content:
            result += f"   {content[:200]}{'...' if len(content) > 200 else ''}\n"
        result += "\n"
    return result


def extract(
    urls: list[str],
    include_images: bool = False,
    extract_depth: str = "basic",
) -> str:
    """抓取网页内容"""
    payload = {
        "api_key": API_KEY,
        "urls": urls,
        "include_images": include_images,
        "extract_depth": extract_depth,
    }

    logger.info(f"抓取: {urls}")
    data = api_call("extract", payload)

    result = "网页抓取结果：\n\n"
    for i, r in enumerate(data.get("results", []), 1):
        content = r.get("raw_content", "")
        result += f"### {i}. {r['url']}\n"
        result += f"{content[:2000]}{'...' if len(content) > 2000 else ''}\n\n"
        if r.get("images"):
            result += "图片：\n"
            for j, img in enumerate(r["images"], 1):
                result += f"  {j}. {img}\n"
            result += "\n"
    return result


def quick_search(query: str) -> str:
    """快速搜索"""
    payload = {
        "api_key": API_KEY,
        "query": query,
        "max_results": 3,
        "include_answer": True,
    }

    logger.info(f"快速搜索: {query}")
    data = api_call("search", payload)

    result = ""
    if data.get("answer"):
        result += f"{data['answer']}\n\n"
    for i, r in enumerate(data.get("results", []), 1):
        result += f"{i}. {r['title']} - {r['url']}\n"
    return result


# ========== MCP JSON-RPC ==========

TOOLS = {
    "search": {
        "name": "search",
        "description": "搜索互联网（支持 AI 摘要、域名过滤、新闻搜索等）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"},
                "search_depth": {"type": "string", "enum": ["basic", "advanced"], "default": "basic"},
                "max_results": {"type": "number", "default": 5},
                "include_answer": {"type": "boolean", "default": True},
                "include_raw_content": {"type": "boolean", "default": False},
                "include_images": {"type": "boolean", "default": False},
                "include_domains": {"type": "array", "items": {"type": "string"}, "default": []},
                "exclude_domains": {"type": "array", "items": {"type": "string"}, "default": []},
                "topic": {"type": "string", "enum": ["general", "news"], "default": "general"},
                "days": {"type": "number"},
            },
            "required": ["query"],
        },
    },
    "extract": {
        "name": "extract",
        "description": "抓取网页内容（支持深度抓取、图片提取）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "urls": {"type": "array", "items": {"type": "string"}, "description": "要抓取的 URL 列表"},
                "include_images": {"type": "boolean", "default": False},
                "extract_depth": {"type": "string", "enum": ["basic", "advanced"], "default": "basic"},
            },
            "required": ["urls"],
        },
    },
    "quick_search": {
        "name": "quick_search",
        "description": "快速搜索（返回简洁结果）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"},
            },
            "required": ["query"],
        },
    },
}

HANDLERS = {
    "search": search,
    "extract": extract,
    "quick_search": quick_search,
}


def make_response(req_id, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def make_error(req_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def handle_request(request: dict):
    method = request.get("method", "")
    req_id = request.get("id")
    params = request.get("params", {})

    if method == "initialize":
        return make_response(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "tavily-mcp", "version": "1.0.0"},
        })

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return make_response(req_id, {"tools": list(TOOLS.values())})

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        handler = HANDLERS.get(tool_name)
        if not handler:
            return make_error(req_id, -32601, f"未知工具: {tool_name}")
        try:
            result = handler(**arguments)
            return make_response(req_id, {"content": [{"type": "text", "text": result}]})
        except Exception as e:
            logger.error(f"工具 {tool_name} 执行失败: {e}")
            return make_error(req_id, -32000, str(e))

    return make_error(req_id, -32601, f"未知方法: {method}")


def main() -> None:
    validate_api_key()
    logger.info("Tavily MCP 服务器已启动")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            logger.debug(f"收到请求: {request.get('method')}")
            response = handle_request(request)
            if response:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 解析错误: {e}")
            continue


if __name__ == "__main__":
    main()
