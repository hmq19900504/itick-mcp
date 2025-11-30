"""
iTick MCP Server - FastAPI Implementation
基于 FastAPI 的 MCP 服务器，对接 iTick API
"""
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import logging

from .config import settings
from .tools import (
    StockQuoteTool,
    StockKlineTool,
    StockTickTool,
    StockDepthTool,
    TimestampTool,
    TechnicalIndicatorsTool,
    MoneyFlowTool,
    IndexAnalysisTool,
    SectorAnalysisTool
)

# 配置日志
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="iTick MCP Server",
    description="基于 iTick API 的金融数据 MCP 服务器",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册所有工具
TOOLS = [
    StockQuoteTool,
    StockKlineTool,
    StockTickTool,
    StockDepthTool,
    TimestampTool,
    TechnicalIndicatorsTool,
    MoneyFlowTool,
    IndexAnalysisTool,
    SectorAnalysisTool
]


def extract_api_key_from_header(request: Request) -> Optional[str]:
    """
    从请求头中提取 API Key
    优先级：X-Itick-Token > Authorization Bearer > X-Api-Key
    """
    # 方式1: X-Itick-Token
    token = request.headers.get("X-Itick-Token")
    if token:
        return token
    
    # 方式2: Authorization Bearer
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "")
    
    # 方式3: X-Api-Key
    api_key = request.headers.get("X-Api-Key")
    if api_key:
        return api_key
    
    # 回退到环境变量
    return settings.itick_api_key or None


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "iTick MCP Server",
        "version": "1.0.0",
        "transport": "streamable-http"
    }


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    MCP 主端点 - 处理 JSON-RPC 请求
    """
    try:
        body = await request.json()
        method = body.get("method")
        request_id = body.get("id")
        
        logger.info(f"[MCP] 收到请求: method={method}, id={request_id}")
        
        # 处理 initialize 请求
        if method == "initialize":
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "iTick MCP Server",
                        "version": "1.0.0"
                    }
                },
                "id": request_id
            })
        
        # 处理 tools/list 请求
        elif method == "tools/list":
            tools_list = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.parameters
                }
                for tool in TOOLS
            ]
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "tools": tools_list
                },
                "id": request_id
            })
        
        # 处理 tools/call 请求
        elif method == "tools/call":
            params = body.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # 提取 API Key
            api_key = extract_api_key_from_header(request)
            
            logger.info(f"[MCP] 调用工具: {tool_name}, has_api_key={bool(api_key)}")
            
            # 查找并执行工具
            tool_class = None
            for tool in TOOLS:
                if tool.name == tool_name:
                    tool_class = tool
                    break
            
            if not tool_class:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"工具不存在: {tool_name}"
                    },
                    "id": request_id
                }, status_code=400)
            
            # 执行工具
            try:
                result = await tool_class.run(arguments, api_key)
                logger.info(f"[MCP] 工具执行成功: {tool_name}")
                
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": request_id
                })
                
            except Exception as e:
                logger.error(f"[MCP] 工具执行失败: {tool_name}, error={str(e)}")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32000,
                        "message": str(e)
                    },
                    "id": request_id
                }, status_code=400)
        
        # 不支持的资源和提示（返回空列表）
        elif method == "resources/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "resources": []
                },
                "id": request_id
            })
        
        elif method == "prompts/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "prompts": []
                },
                "id": request_id
            })
        
        # 未知方法
        else:
            logger.warning(f"[MCP] 未知方法: {method}")
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"方法不存在: {method}"
                },
                "id": request_id
            }, status_code=400)
            
    except Exception as e:
        logger.error(f"[MCP] 处理请求失败: {str(e)}", exc_info=True)
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"内部错误: {str(e)}"
            },
            "id": None
        }, status_code=500)


@app.get("/")
async def root():
    """根路径 - 服务信息"""
    return {
        "service": "iTick MCP Server",
        "version": "1.0.0",
        "description": "基于 iTick API 的金融数据 MCP 服务器",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
            "docs": "/docs"
        },
        "tools_count": len(TOOLS)
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("🚀 iTick MCP Server 启动中...")
    logger.info("=" * 60)
    logger.info(f"📍 Server URL:    http://{settings.host}:{settings.port}")
    logger.info(f"📡 MCP Endpoint:  http://{settings.host}:{settings.port}/mcp")
    logger.info(f"💚 Health Check:  http://{settings.host}:{settings.port}/health")
    logger.info(f"📚 API Docs:      http://{settings.host}:{settings.port}/docs")
    logger.info(f"🔧 Available Tools: {len(TOOLS)}")
    logger.info("=" * 60)
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info" if not settings.debug else "debug"
    )
