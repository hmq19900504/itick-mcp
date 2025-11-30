# Claude Desktop 接入指南

## 🚀 快速开始

### 1. 启动 MCP 服务器

在项目目录下运行：

```bash
cd /Users/miracle.hong/baidusync/code/itick-mcp
python -m src.server
```

你会看到：
```
🚀 iTick MCP Server 启动中...
📍 Server URL:    http://0.0.0.0:3000
📡 MCP Endpoint:  http://0.0.0.0:3000/mcp
💚 Health Check:  http://0.0.0.0:3000/health
📚 API Docs:      http://0.0.0.0/docs
🔧 Available Tools: 9
```

### 2. 配置 Claude Desktop

#### macOS 配置路径
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### Windows 配置路径
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 3. 配置文件内容

打开或创建 `claude_desktop_config.json`，添加以下内容：

```json
{
  "mcpServers": {
    "itick-stock": {
      "type": "streamableHttp",
      "url": "http://localhost:3000/mcp",
      "timeout": 600,
      "headers": {
        "X-Itick-Token": "你的iTick API Key"
      }
    }
  }
}
```

**重要参数说明**：

| 参数 | 值 | 说明 |
|------|-------|------|
| `type` | `"streamableHttp"` | MCP 传输协议类型（固定） |
| `url` | `"http://localhost:3000/mcp"` | MCP 端点地址 |
| `timeout` | `600` | 请求超时时间（秒） |
| `X-Itick-Token` | 你的 API Key | iTick API 认证密钥 |

### 4. 获取 iTick API Key

1. 访问 https://itick.org/
2. 使用 Google 或 GitHub 账号登录
3. 在 Dashboard 中获取 API Key
4. 将 API Key 填入配置文件的 `X-Itick-Token` 字段

### 5. 重启 Claude Desktop

配置完成后，**完全退出并重启** Claude Desktop：

- **macOS**: `Cmd + Q` 退出，然后重新打开
- **Windows**: 右键托盘图标 → 退出，然后重新打开

### 6. 验证连接

在 Claude Desktop 中输入：

```
你好，请帮我查询一下腾讯控股(700.HK)的实时报价
```

如果配置成功，Claude 会自动调用 iTick MCP 工具获取数据。

---

## 📋 完整配置示例

### 方案1: 基础配置（推荐）

```json
{
  "mcpServers": {
    "itick-stock": {
      "type": "streamableHttp",
      "url": "http://localhost:3000/mcp",
      "timeout": 600,
      "headers": {
        "X-Itick-Token": "d3de0307d463469697ac2faf27f5f5e02cedbde8e2d1400c9476d45adcf6a859"
      }
    }
  }
}
```

### 方案2: 多服务器配置

如果你有其他 MCP 服务器，可以这样配置：

```json
{
  "mcpServers": {
    "itick-stock": {
      "type": "streamableHttp",
      "url": "http://localhost:3000/mcp",
      "timeout": 600,
      "headers": {
        "X-Itick-Token": "你的iTick API Key"
      }
    },
    "其他服务": {
      "type": "streamableHttp",
      "url": "http://localhost:4000/mcp",
      "timeout": 300
    }
  }
}
```

### 方案3: 使用环境变量（高级）

```json
{
  "mcpServers": {
    "itick-stock": {
      "type": "streamableHttp",
      "url": "http://localhost:3000/mcp",
      "timeout": 600,
      "headers": {
        "X-Itick-Token": "${ITICK_API_KEY}"
      }
    }
  }
}
```

然后在系统环境变量中设置：
```bash
export ITICK_API_KEY="你的API Key"
```

---

## 🔧 故障排查

### 问题1: Claude 无法连接到 MCP 服务器

**症状**: Claude 提示无法使用工具

**解决方案**:
1. 确认 MCP 服务器正在运行
   ```bash
   curl http://localhost:3000/health
   ```
   应该返回: `{"status":"healthy",...}`

2. 检查端口是否被占用
   ```bash
   lsof -i :3000
   ```

3. 检查配置文件路径是否正确
   ```bash
   # macOS
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

### 问题2: API Key 无效

**症状**: 返回 "API 认证失败" 错误

**解决方案**:
1. 检查 API Key 是否正确复制（没有多余空格）
2. 登录 https://itick.org/ 确认 API Key 有效
3. 检查配置文件中 `X-Itick-Token` 字段是否正确

### 问题3: 超时错误

**症状**: 请求超时

**解决方案**:
1. 增加 timeout 值（如改为 900）
2. 检查网络连接
3. 查看服务器日志是否有错误

### 问题4: 工具列表为空

**症状**: Claude 说没有可用的工具

**解决方案**:
1. 完全退出 Claude Desktop（不是最小化）
2. 重新启动 Claude Desktop
3. 检查服务器日志确认工具已注册

---

## 📊 可用工具列表

配置成功后，Claude 可以使用以下 9 个工具：

### 基础行情工具
1. **itick_stock_quote** - 实时股票报价
2. **itick_stock_kline** - K线历史数据
3. **itick_stock_tick** - 逐笔成交数据
4. **itick_stock_depth** - 盘口深度数据
5. **itick_current_timestamp** - 当前时间戳

### 技术分析工具
6. **itick_technical_indicators** - 技术指标分析（MACD、RSI、KDJ、BOLL）
7. **itick_money_flow** - 资金流向分析

### 宏观分析工具
8. **itick_index_analysis** - 指数分析（大盘、板块指数）
9. **itick_sector_analysis** - 板块分析（行业、概念板块）

---

## 💡 使用示例

配置完成后，你可以这样跟 Claude 交互：

### 示例1: 查询个股
```
用户: "查询腾讯控股(700.HK)的实时报价"
Claude: 调用 itick_stock_quote → 返回实时行情
```

### 示例2: 技术分析
```
用户: "帮我分析一下茅台(600519.SH)的技术指标"
Claude: 调用 itick_technical_indicators → 返回MACD、RSI等指标
```

### 示例3: 大盘分析
```
用户: "今天A股市场表现怎么样？"
Claude: 调用 itick_index_analysis → 分析上证、深证、创业板指数
```

### 示例4: 板块分析
```
用户: "白酒板块今天涨了吗？"
Claude: 调用 itick_sector_analysis → 分析白酒板块各股表现
```

### 示例5: 综合分析
```
用户: "帮我做个全面的市场分析"
Claude: 
1. 调用 itick_index_analysis - 看大盘
2. 调用 itick_sector_analysis - 选板块
3. 调用 itick_technical_indicators - 看个股技术面
4. 调用 itick_money_flow - 看资金流向
5. 给出综合投资建议
```

---

## 🔒 安全建议

1. **API Key 保护**
   - 不要将 API Key 提交到 Git
   - 不要在公开场合分享 API Key
   - 定期更换 API Key

2. **本地运行**
   - MCP 服务器建议只在本地运行（localhost）
   - 如需远程访问，请配置防火墙和认证

3. **数据使用**
   - iTick 数据仅供个人研究使用
   - 请遵守 iTick 服务条款

---

## 📞 技术支持

### 查看服务器日志
```bash
cd /Users/miracle.hong/baidusync/code/itick-mcp
python -m src.server
# 日志会实时显示在终端
```

### 测试 MCP 端点
```bash
# 健康检查
curl http://localhost:3000/health

# 查看工具列表
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "X-Itick-Token: 你的API_Key" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### 常用命令
```bash
# 启动服务器
python -m src.server

# 查看端口占用
lsof -i :3000

# 停止服务器
# 在服务器终端按 Ctrl+C

# 后台运行（生产环境）
nohup python -m src.server > server.log 2>&1 &
```

---

## 🎓 进阶配置

### 使用 systemd 自动启动（Linux）

创建 `/etc/systemd/system/itick-mcp.service`:

```ini
[Unit]
Description=iTick MCP Server
After=network.target

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/path/to/itick-mcp
Environment="ITICK_API_KEY=你的API_Key"
ExecStart=/usr/bin/python3 -m src.server
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl enable itick-mcp
sudo systemctl start itick-mcp
sudo systemctl status itick-mcp
```

### 使用 Docker 运行

```bash
# 构建镜像
docker build -t itick-mcp .

# 运行容器
docker run -d \
  -p 3000:3000 \
  -e ITICK_API_KEY=你的API_Key \
  --name itick-mcp \
  itick-mcp

# 查看日志
docker logs -f itick-mcp
```

---

## 📝 配置文件完整路径

根据你的操作系统，配置文件路径如下：

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

完整路径示例:
```
/Users/miracle.hong/Library/Application Support/Claude/claude_desktop_config.json
```

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

完整路径示例:
```
C:\Users\YourUsername\AppData\Roaming\Claude\claude_desktop_config.json
```

### Linux
```
~/.config/Claude/claude_desktop_config.json
```

---

## ✅ 验证清单

配置完成后，请确认：

- [ ] MCP 服务器正在运行（http://localhost:3000）
- [ ] 健康检查通过（http://localhost:3000/health）
- [ ] 配置文件路径正确
- [ ] API Key 正确填写
- [ ] Claude Desktop 已完全重启
- [ ] 能在 Claude 中看到工具列表
- [ ] 测试查询返回正确数据

---

**祝你使用愉快！** 🎉

如有问题，请查看项目 README 或提交 Issue：
https://github.com/hmq19900504/itick-mcp
