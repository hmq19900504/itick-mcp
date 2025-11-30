# iTick MCP Server 开发指南

## 项目架构

```
itick-mcp/
├── src/                      # 源代码目录
│   ├── __init__.py
│   ├── server.py            # FastAPI 主服务器
│   ├── config.py            # 配置管理
│   ├── itick_client.py      # iTick API 客户端封装
│   └── tools/               # MCP 工具模块
│       ├── __init__.py
│       ├── stock_quote.py   # 实时报价工具
│       ├── stock_kline.py   # K线数据工具
│       ├── stock_tick.py    # Tick数据工具
│       ├── stock_depth.py   # 盘口深度工具
│       └── timestamp.py     # 时间戳工具
├── requirements.txt         # Python 依赖
├── .env.example            # 环境变量示例
├── Dockerfile              # Docker 镜像
├── start.sh               # 快速启动脚本
├── test_server.py         # 测试脚本
└── README.md              # 项目文档
```

## 核心组件

### 1. FastAPI 服务器 (`server.py`)

负责处理 HTTP 请求和 MCP 协议：

- **端点**:
  - `GET /`: 服务信息
  - `GET /health`: 健康检查
  - `POST /mcp`: MCP JSON-RPC 端点
  - `GET /docs`: FastAPI 自动生成的 API 文档

- **MCP 方法**:
  - `initialize`: 初始化连接
  - `tools/list`: 列出所有可用工具
  - `tools/call`: 调用特定工具
  - `resources/list`: 资源列表（空）
  - `prompts/list`: 提示列表（空）

### 2. iTick 客户端 (`itick_client.py`)

封装对 iTick API 的调用：

```python
class ItickClient:
    async def get_stock_quote(region, code) -> Dict
    async def get_stock_kline(region, code, ...) -> List[Dict]
    async def get_stock_tick(region, code) -> Dict
    async def get_stock_depth(region, code) -> Dict
```

**特点**:
- 统一的错误处理（E001/E002/E003）
- 自动添加认证 Header
- 异步 HTTP 请求（基于 httpx）

### 3. 工具模块 (`tools/`)

每个工具都是一个独立的类，包含：

```python
class ToolName:
    name = "tool_name"              # 工具名称
    description = "工具描述"         # 功能说明
    parameters = {...}              # JSON Schema 参数定义
    
    @staticmethod
    async def run(arguments, api_key) -> Dict:
        # 工具执行逻辑
        return {
            "content": [{
                "type": "text",
                "text": "返回内容"
            }]
        }
```

## 开发流程

### 添加新工具

1. **创建工具文件** `src/tools/your_tool.py`:

```python
from typing import Dict, Any
from ..itick_client import get_client, ItickAPIError


class YourTool:
    name = "your_tool_name"
    description = "工具功能描述"
    
    parameters = {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "参数1描述"
            }
        },
        "required": ["param1"]
    }
    
    @staticmethod
    async def run(arguments: Dict[str, Any], api_key: str = None) -> Dict[str, Any]:
        try:
            param1 = arguments.get("param1")
            
            # 调用 iTick API
            client = get_client(api_key)
            data = await client.your_api_method(param1)
            
            # 格式化结果
            result = f"""## 标题
            
数据: {data}
"""
            
            return {
                "content": [{
                    "type": "text",
                    "text": result
                }]
            }
            
        except ItickAPIError as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"❌ iTick API 错误: [{e.code}] {e.message}"
                }],
                "isError": True
            }
```

2. **注册工具** 在 `src/tools/__init__.py`:

```python
from .your_tool import YourTool

__all__ = [
    # ... 现有工具
    "YourTool"
]
```

3. **在服务器中引入** `src/server.py`:

```python
from .tools import (
    # ... 现有工具
    YourTool
)

TOOLS = [
    # ... 现有工具
    YourTool
]
```

### 扩展 iTick 客户端

如果需要调用新的 iTick API 端点，在 `itick_client.py` 中添加：

```python
async def your_new_method(self, param1: str) -> Dict[str, Any]:
    """
    新方法说明
    
    Args:
        param1: 参数说明
        
    Returns:
        返回数据
    """
    return await self._request(
        "GET",
        "/your/endpoint",
        params={"param1": param1}
    )
```

## 测试

### 1. 运行测试脚本

```bash
python test_server.py
```

### 2. 手动测试

使用 curl 或 Postman:

```bash
# 健康检查
curl http://localhost:3000/health

# 列出工具
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'

# 调用工具
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "X-Itick-Token: your_api_key" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "itick_stock_quote",
      "arguments": {
        "region": "HK",
        "code": "700"
      }
    },
    "id": 2
  }'
```

### 3. 使用 FastAPI 自动文档

访问 `http://localhost:3000/docs` 查看交互式 API 文档

## 调试

### 启用调试模式

修改 `.env`:
```env
DEBUG=true
```

查看详细日志：
```bash
uvicorn src.server:app --reload --log-level debug
```

### 常见问题

#### 1. API Key 认证失败

检查：
- `.env` 文件中的 `ITICK_API_KEY`
- 请求 Header 中的 `X-Itick-Token`
- API Key 是否过期

#### 2. 工具调用失败

检查：
- 工具名称是否正确
- 参数格式是否符合 JSON Schema
- iTick API 响应是否正常

#### 3. 端口被占用

修改 `.env` 中的 `PORT`:
```env
PORT=8000
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t itick-mcp .

# 运行容器
docker run -d \
  -p 3000:3000 \
  -e ITICK_API_KEY=your_api_key \
  --name itick-mcp \
  itick-mcp
```

### 云平台部署

#### Railway

1. 连接 GitHub 仓库
2. 添加环境变量 `ITICK_API_KEY`
3. 自动部署

#### Render

1. 创建 Web Service
2. 选择 Python 环境
3. 构建命令: `pip install -r requirements.txt`
4. 启动命令: `uvicorn src.server:app --host 0.0.0.0 --port $PORT`
5. 添加环境变量

## 性能优化

### 1. 缓存

对于不常变化的数据（如股票基本信息），可以添加缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
async def get_cached_stock_info(code):
    # ...
```

### 2. 连接池

iTick 客户端已使用 httpx.AsyncClient，自动管理连接池

### 3. 并发请求

使用 `asyncio.gather` 并发请求多个股票：

```python
results = await asyncio.gather(
    client.get_stock_quote("HK", "700"),
    client.get_stock_quote("US", "AAPL")
)
```

## 安全建议

1. **不要硬编码 API Key**: 使用环境变量
2. **限流**: 添加请求频率限制
3. **HTTPS**: 生产环境使用 HTTPS
4. **输入验证**: 严格验证所有用户输入
5. **错误信息**: 不要暴露敏感信息

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交变更
4. 推送到分支
5. 创建 Pull Request

## 参考资源

- [iTick API 文档](https://docs.itick.org/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [httpx 文档](https://www.python-httpx.org/)
