# 🎉 iTick MCP Server 使用指南

## 一、项目已完成！

恭喜！基于 **FastAPI** 和 **iTick API** 的 MCP 服务器已经完整实现。

## 二、立即开始使用

### Step 1: 获取 iTick API Key

1. 访问 [iTick 官网](https://itick.org/)
2. 使用 Google 或 GitHub 登录
3. 在 Dashboard 获取 API Key

### Step 2: 配置环境

```bash
cd itick-mcp
cp .env.example .env
```

编辑 `.env` 文件：
```env
ITICK_API_KEY=粘贴您的API_Key_这里
```

### Step 3: 启动服务

**方式1：使用启动脚本（推荐）**
```bash
./start.sh
```

**方式2：手动启动**
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn src.server:app --reload --port 3000
```

### Step 4: 验证服务

打开浏览器访问：
- **健康检查**: http://localhost:3000/health
- **API 文档**: http://localhost:3000/docs

### Step 5: 配置 Claude Desktop

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

添加配置：
```json
{
  "mcpServers": {
    "itick-stock": {
      "type": "streamableHttp",
      "url": "http://localhost:3000/mcp",
      "timeout": 600,
      "headers": {
        "X-Itick-Token": "您的_iTick_API_Key"
      }
    }
  }
}
```

### Step 6: 在 Claude 中测试

重启 Claude Desktop，然后尝试：

```
"获取当前时间"
"查询腾讯控股(00700.HK)的实时报价"
"获取茅台(600519.SH)最近30天的日K线数据"
```

## 三、可用工具列表

| 工具 | 用途 | 示例 |
|-----|------|------|
| `itick_stock_quote` | 实时报价 | "查询苹果(AAPL)股价" |
| `itick_stock_kline` | K线数据 | "获取比亚迪最近3个月日K线" |
| `itick_stock_tick` | Tick数据 | "查看宁德时代Tick数据" |
| `itick_stock_depth` | 盘口深度 | "阿里巴巴盘口深度" |
| `current_timestamp` | 当前时间 | "现在几点了" |

## 四、测试服务

运行测试脚本：
```bash
python test_server.py
```

测试会检查：
- ✅ 服务器健康状态
- ✅ MCP 协议初始化
- ✅ 工具列表
- ✅ 时间戳工具
- ✅ 股票报价（需要 API Key）

## 五、常见问题

### Q1: 服务启动失败？
**检查**:
- Python 版本 ≥ 3.11
- 端口 3000 是否被占用
- `.env` 文件是否存在

**解决**:
```bash
# 检查端口
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# 修改端口（编辑 .env）
PORT=8000
```

### Q2: Claude 无法连接？
**检查**:
1. 服务是否运行：访问 http://localhost:3000/health
2. Claude 配置文件是否正确
3. URL 是否匹配（端口、路径）

### Q3: API 调用失败？
**检查**:
- iTick API Key 是否有效
- 股票代码格式是否正确（如 HK 市场用 700，不是 00700）
- 查看服务器日志中的错误信息

### Q4: 想添加更多功能？
参考 `DEVELOPMENT.md` 开发指南，学习如何：
- 添加新工具
- 扩展 iTick API 客户端
- 部署到云平台

## 六、项目结构速览

```
itick-mcp/
├── src/
│   ├── server.py          # 主服务器（FastAPI）
│   ├── config.py          # 配置管理
│   ├── itick_client.py    # iTick API 封装
│   └── tools/             # 5个工具模块
├── requirements.txt       # 依赖
├── .env.example          # 配置模板
├── start.sh              # 启动脚本
├── test_server.py        # 测试脚本
└── README.md             # 完整文档
```

## 七、下一步

### 立即使用
1. ✅ 按照上述步骤配置和启动
2. ✅ 在 Claude 中测试查询
3. ✅ 探索不同的股票市场

### 进阶开发
1. 📖 阅读 `DEVELOPMENT.md` 学习架构
2. 🔧 添加自定义工具
3. 🚀 部署到云平台（Railway, Render 等）

### 扩展功能（可选）
- 技术指标计算（MACD, RSI）
- 外汇行情查询
- 加密货币数据
- WebSocket 实时推送

## 八、获取帮助

- **项目文档**: 查看 `README.md`, `CLAUDE_CONFIG.md`, `DEVELOPMENT.md`
- **iTick API**: https://docs.itick.org/
- **FastAPI 文档**: https://fastapi.tiangolo.com/
- **MCP 协议**: https://modelcontextprotocol.io/

## 九、重要提示

⚠️ **API Key 安全**:
- 不要将 `.env` 文件提交到 Git
- 不要在代码中硬编码 API Key
- 使用环境变量或安全的密钥管理服务

✅ **最佳实践**:
- 定期更新依赖包
- 监控 API 调用次数
- 为生产环境启用 HTTPS
- 添加请求限流保护

---

## 🎊 开始使用吧！

所有准备工作已完成，现在运行：

```bash
./start.sh
```

然后在 Claude 中享受金融数据查询服务！

**祝您使用愉快！** 📈💰
