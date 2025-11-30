# iTick MCP Server

基于 iTick API 的金融数据 MCP 服务器，使用 FastAPI 实现，为 Claude 等 AI 助手提供实时股票行情数据。

## 🌟 功能特色

- **实时行情**：支持全球多市场股票实时报价（A股、港股、美股等）
- **K线数据**：获取多周期 K线数据（分钟线、日线、周线、月线）
- **Tick数据**：逐笔成交数据，毫秒级延迟
- **盘口深度**：五档/十档买卖盘口数据
- **多市场覆盖**：支持17+个国家和地区的股票市场

## 📋 支持的市场

| 市场代码 | 市场名称 | 示例代码 |
|---------|---------|---------|
| HK | 香港 | 700 (腾讯) |
| US | 美国 | AAPL (苹果) |
| SH | 上海 | 600519 (茅台) |
| SZ | 深圳 | 000001 (平安银行) |
| SG | 新加坡 | - |
| JP | 日本 | - |
| TW | 台湾 | - |
| IN | 印度 | - |
| TH | 泰国 | - |
| DE | 德国 | - |
| ... | 其他 | 见 iTick 文档 |

## 🚀 快速开始

### 1. 安装依赖

```bash
cd itick-mcp
pip install -r requirements.txt
```

### 2. 配置 API Key

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的 iTick API Key：

```env
ITICK_API_KEY=your_itick_api_key_here
PORT=3000
```

**如何获取 iTick API Key**：
1. 访问 [iTick 官网](https://itick.org/)
2. 使用 Google 或 GitHub 账号登录
3. 在 Dashboard 中获取 API Key

### 3. 启动服务

```bash
# 开发模式（自动重载）
uvicorn src.server:app --reload --port 3000

# 生产模式
uvicorn src.server:app --host 0.0.0.0 --port 3000
```

服务启动后：
- **MCP 端点**: `http://localhost:3000/mcp`
- **健康检查**: `http://localhost:3000/health`
- **API 文档**: `http://localhost:3000/docs`

### 4. 配置 Claude Desktop

编辑 Claude Desktop 配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

添加以下配置：

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

## 🛠️ 可用工具

### 1. itick_stock_quote - 实时股票报价

获取股票实时行情数据。

**参数**：
- `region` (必填): 市场代码（如 HK, US, SH, SZ）
- `code` (必填): 股票代码（如 700, AAPL, 600519）

**示例**：
```
"查询腾讯控股(00700.HK)的实时报价"
"获取苹果公司(AAPL)最新股价"
```

### 2. itick_stock_kline - K线数据

获取股票K线数据，支持多周期。

**参数**：
- `region` (必填): 市场代码
- `code` (必填): 股票代码
- `start_date` (必填): 起始日期 (YYYYMMDD)
- `end_date` (必填): 结束日期 (YYYYMMDD)
- `period` (可选): 周期类型，默认 'day'
  - `1min`, `5min`, `15min`, `30min`, `60min` - 分钟线
  - `day` - 日线
  - `week` - 周线
  - `month` - 月线

**示例**：
```
"获取茅台(600519.SH)最近30天的日K线"
"查看比亚迪(002594.SZ) 2024年1月1日到3月31日的周K线"
```

### 3. itick_stock_tick - Tick数据

获取逐笔成交数据。

**参数**：
- `region` (必填): 市场代码
- `code` (必填): 股票代码

**示例**：
```
"查看宁德时代(300750.SZ)的实时Tick数据"
```

### 4. itick_stock_depth - 盘口深度

获取五档/十档买卖盘数据。

**参数**：
- `region` (必填): 市场代码
- `code` (必填): 股票代码

**示例**：
```
"查看阿里巴巴(09988.HK)的盘口深度"
```

### 5. current_timestamp - 当前时间

获取当前东八区时间戳。

**参数**：
- `format` (可选): 时间格式
  - `datetime` - 完整日期时间（默认）
  - `date` - 仅日期
  - `time` - 仅时间
  - `timestamp` - Unix时间戳
  - `readable` - 可读格式

**示例**：
```
"获取当前时间"
"查看今天的日期"
```

### 🆕 6. itick_technical_indicators - 技术指标分析

计算股票的技术指标，包括MACD、RSI、KDJ、BOLL、MA等。

**参数**：
- `region` (必填): 市场代码
- `code` (必填): 股票代码
- `indicators` (可选): 指标列表，默认 ["macd", "rsi"]
  - `macd` - MACD指标（趋势跟踪）
  - `rsi` - 相对强弱指标（超买超卖）
  - `kdj` - 随机指标
  - `boll` - 布林带
  - `ma` - 移动平均线
  - `ema` - 指数移动平均线
  - `all` - 全部指标
- `period` (可选): K线周期，默认 "day"
- `limit` (可选): 数据条数，默认200

**示例**：
```
"计算腾讯(700.HK)的MACD和RSI指标"
"分析茅台(600519.SH)的KDJ超买超卖情况"
"查看苹果(AAPL)的布林带和均线系统"
```

### 🆕 7. itick_money_flow - 资金流向分析

分析股票的资金流向分布，包括主力资金、大单、中单、小单的流入流出。

**参数**：
- `region` (必填): 市场代码
- `code` (必填): 股票代码
- `period` (可选): 分析周期，默认 "day"
- `days` (可选): 分析天数，默认10

**核心指标**：
- 🐋 超大单（≥50万）- 机构/大户资金
- 🐘 大单（20-50万）- 中大户资金
- 🐕 中单（5-20万）- 中户资金
- 🐁 小单（<5万）- 散户资金
- 💪 主力资金 = 超大单 + 大单

**示例**：
```
"查看腾讯(700.HK)近期资金流向"
"分析茅台(600519.SH)主力资金动向"
"查询苹果(AAPL)大单资金流入情况"
```

### 🆕 8. itick_index_analysis - 指数分析

分析大盘指数和板块指数的实时行情、历史走势和市场强弱对比。

**参数**：
- `indices` (必填): 指数列表，格式: [{region, code, name}]
- `period` (可选): 分析周期，默认 "day"
- `days` (可选): 历史天数，默认30
- `compare` (可选): 是否对比分析，默认True

**常用指数**：
- 上证指数: 000001.SH
- 深证成指: 399001.SZ
- 创业板指: 399006.SZ
- 沪深300: 000300.SH
- 恒生指数: HSI.HK

**示例**：
```
"查看上证指数和深证成指今日表现"
"分析创业板指近期走势"
"对比沪深300和中证500的强弱"
```

### 🆕 9. itick_sector_analysis - 板块分析

分析行业板块和概念板块的强弱、资金流向和投资机会。

**参数**：
- `stocks` (必填): 板块内股票列表，格式: [{region, code, name, sector}]
- `period` (可选): 分析周期，默认 "day"
- `days` (可选): 分析天数，默认10

**分析内容**：
- 板块整体涨跌排名
- 板块资金流向统计
- 板块龙头股识别
- 板块轮动建议

**示例**：
```
"分析白酒板块的资金流向"
"对比科技和金融板块的强弱"
"查看新能源汽车板块龙头股"
```

## 💡 使用示例

### 综合分析示例

```
"分析腾讯控股(00700.HK)的当前市场表现，包括实时报价和盘口深度"

"比较茅台(600519.SH)和五粮液(000858.SZ)最近一个月的走势"

"查看苹果公司(AAPL)今天的实时Tick数据和报价信息"
```

### 技术分析示例

```
"获取比亚迪(002594.SZ)最近3个月的日K线数据，分析趋势"

"查看宁德时代(300750.SZ)的5分钟K线，观察盘中波动"

"计算腾讯(700.HK)的MACD、RSI、KDJ等技术指标，判断买卖时机"

"分析茅台(600519.SH)近20日的资金流向，查看主力资金是否流入"

"查看上证指数、深证成指和创业板指今日表现对比"

"分析白酒板块各股强弱，找出龙头股和补涨股"
```

## 🔧 开发指南

### 项目结构

```
itick-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py          # FastAPI 主服务器
│   ├── config.py          # 配置管理
│   ├── itick_client.py    # iTick API 客户端
│   └── tools/             # MCP 工具模块
│       ├── __init__.py
│       ├── stock_quote.py        # 实时报价
│       ├── stock_kline.py        # K线数据
│       ├── stock_tick.py         # 逐笔成交
│       ├── stock_depth.py        # 盘口深度
│       ├── timestamp.py          # 时间戳
│       ├── technical_indicators.py  # 🆕 技术指标
│       └── money_flow.py         # 🆕 资金流向
├── requirements.txt
├── .env.example
├── Dockerfile
├── README.md
└── NEW_FEATURES.md       # 🆕 新功能文档
```

### 添加新工具

1. 在 `src/tools/` 下创建新文件
2. 定义工具类，继承基本结构：

```python
from typing import Dict, Any

class YourTool:
    name = "your_tool_name"
    description = "工具功能描述"
    parameters = {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "参数描述"
            }
        },
        "required": ["param1"]
    }
    
    @staticmethod
    async def run(arguments: Dict[str, Any]) -> Dict[str, Any]:
        # 实现逻辑
        return {
            "content": [{
                "type": "text",
                "text": "返回内容"
            }]
        }
```

3. 在 `server.py` 中注册工具

## 🐳 Docker 部署

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

## 📊 API 错误码

| 错误码 | 说明 | 解决方案 |
|-------|------|---------|
| E001 | 产品不存在 | 检查股票代码是否正确 |
| E002 | 认证失败 | 检查 API Key 是否有效 |
| E003 | 超过订阅限制 | 联系客服升级套餐或减少订阅 |

## 🔗 相关链接

- [iTick 官网](https://itick.org/)
- [iTick API 文档](https://docs.itick.org/)
- [FinanceMCP 参考项目](https://github.com/guangxiangdebizi/FinanceMCP)
- [MCP 协议规范](https://modelcontextprotocol.io/)

## 📄 许可证

MIT License

## 👨‍💻 作者

基于 iTick API 和 MCP 协议构建

---

⭐ 如果这个项目对您有帮助，欢迎 Star！
