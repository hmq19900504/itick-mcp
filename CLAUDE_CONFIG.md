# iTick MCP Server - Claude Desktop 配置示例

## 基本配置

将以下配置添加到 Claude Desktop 的配置文件中：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "itick-stock": {
      "type": "streamableHttp",
      "url": "http://localhost:3000/mcp",
      "timeout": 600,
      "headers": {
        "X-Itick-Token": "your_itick_api_key_here"
      }
    }
  }
}
```

## 配置说明

### 1. 服务器名称
- `itick-stock`: 可以自定义名称，在 Claude 中会显示为工具来源

### 2. 连接类型
- `type: "streamableHttp"`: 使用 HTTP 流式传输模式

### 3. 服务器地址
- `url: "http://localhost:3000/mcp"`: 本地服务器地址
- 如果部署到云端，替换为实际地址（如 `https://your-domain.com/mcp`）

### 4. 超时设置
- `timeout: 600`: 请求超时时间（秒），默认600秒

### 5. API 认证
- `X-Itick-Token`: 您的 iTick API Key
- 也支持其他认证方式：
  - `Authorization: "Bearer your_api_key"`
  - `X-Api-Key: "your_api_key"`

## 获取 iTick API Key

1. 访问 [iTick 官网](https://itick.org/)
2. 使用 Google 或 GitHub 账号登录
3. 在 Dashboard 中获取 API Key
4. 将 API Key 填入配置文件

## 验证配置

1. 启动 iTick MCP Server：
   ```bash
   ./start.sh
   # 或
   uvicorn src.server:app --reload --port 3000
   ```

2. 重启 Claude Desktop

3. 在 Claude 中测试：
   ```
   "获取当前时间"
   "查询腾讯控股(00700.HK)的实时报价"
   ```

## 多服务器配置

如果您同时使用多个 MCP 服务器，配置如下：

```json
{
  "mcpServers": {
    "itick-stock": {
      "type": "streamableHttp",
      "url": "http://localhost:3000/mcp",
      "timeout": 600,
      "headers": {
        "X-Itick-Token": "your_itick_api_key"
      }
    },
    "other-service": {
      "type": "streamableHttp",
      "url": "http://localhost:4000/mcp",
      "timeout": 300
    }
  }
}
```

## 云端部署配置

如果将服务部署到云端（如 AWS, Azure, Railway 等）：

```json
{
  "mcpServers": {
    "itick-stock": {
      "type": "streamableHttp",
      "url": "https://your-app.railway.app/mcp",
      "timeout": 600,
      "headers": {
        "X-Itick-Token": "your_itick_api_key"
      }
    }
  }
}
```

## 故障排查

### 问题1：Claude 无法连接到服务器
- 检查服务器是否正在运行：访问 `http://localhost:3000/health`
- 检查端口是否被占用
- 查看服务器日志是否有错误

### 问题2：API 认证失败
- 确认 iTick API Key 是否正确
- 检查 API Key 是否过期
- 验证 Header 名称是否正确（`X-Itick-Token`）

### 问题3：工具调用失败
- 查看服务器日志中的错误信息
- 检查股票代码格式是否正确
- 确认市场代码是否支持

## 进阶配置

### 启用调试模式

修改 `.env` 文件：
```env
DEBUG=true
```

### 修改服务器端口

修改 `.env` 文件：
```env
PORT=8000
```

然后更新 Claude 配置中的 URL：
```json
"url": "http://localhost:8000/mcp"
```

## 参考资源

- [iTick API 文档](https://docs.itick.org/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
