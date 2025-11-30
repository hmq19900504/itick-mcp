# iTick K线数据结构说明

## 📊 K线数据字段详解

根据 iTick API 官方文档，K线数据返回的是标准 **OHLCV 格式**（Open-High-Low-Close-Volume）。

### 响应结构

```json
{
  "code": 0,
  "msg": null,
  "data": [
    {
      "t": 1741239000000,    // 时间戳 (毫秒)
      "o": 535,              // 开盘价 (Open)
      "h": 536,              // 最高价 (High)
      "l": 534.5,            // 最低价 (Low)
      "c": 534.5,            // 收盘价 (Close)
      "v": 104799385,        // 成交量 (Volume)
      "tu": 56119888070.5    // 成交额 (Turnover)
    },
    ...
  ]
}
```

### 字段说明

| 字段名 | 类型 | 说明 | 备注 |
|-------|------|------|------|
| `t` | number | 时间戳 | 毫秒级Unix时间戳，表示该K线的时间 |
| `o` | number | 开盘价 | Open Price，该周期的第一笔成交价 |
| `h` | number | 最高价 | High Price，该周期内的最高成交价 |
| `l` | number | 最低价 | Low Price，该周期内的最低成交价 |
| `c` | number | 收盘价 | Close Price，该周期的最后一笔成交价 |
| `v` | number | 成交量 | Volume，该周期内的总成交股数 |
| `tu` | number | 成交额 | Turnover，该周期内的总成交金额 |

## 🔧 API 请求参数

### 端点
```
GET https://api.itick.org/stock/kline
```

### 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|-------|------|------|------|------|
| `region` | string | 是 | 市场代码 | HK, US, SH, SZ, SG, JP, TW, IN, TH, DE 等 |
| `code` | string | 是 | 股票代码 | 700 (腾讯), AAPL (苹果), 600519 (茅台) |
| `kType` | number | 是 | K线周期类型 | 见下表 |
| `limit` | number | 否 | 返回数据条数 | 默认100，最大1000 |
| `start_date` | string | 否 | 起始日期 | YYYYMMDD 格式，如 20240101 |
| `end_date` | string | 否 | 结束日期 | YYYYMMDD 格式，如 20240331 |

### kType 周期类型对照表

根据测试和文档，kType 使用数字编码（**待验证完整映射**）：

| kType值 | 周期名称 | 说明 |
|---------|---------|------|
| `1` | 1分钟线 | 1min |
| `2` | 日线 | day (示例中使用) |
| `3` | 周线 | week (推测) |
| `4` | 月线 | month (推测) |
| `5` | 5分钟线 | 5min (推测) |
| `6` | 15分钟线 | 15min (推测) |
| `7` | 30分钟线 | 30min (推测) |
| `8` | 60分钟线 | 60min (推测) |

**⚠️ 注意**：上述 kType 映射需要通过实际测试验证，官方文档未明确说明所有值。

## 📝 请求示例

### Python 示例

```python
import requests

url = "https://api.itick.org/stock/kline"

params = {
    "region": "HK",
    "code": "700",
    "kType": 2,      # 日线
    "limit": 10      # 最近10条
}

headers = {
    "accept": "application/json",
    "token": "your_api_key_here"
}

response = requests.get(url, params=params, headers=headers)
data = response.json()

print(f"响应码: {data['code']}")
if data['code'] == 0:
    klines = data['data']
    print(f"获取到 {len(klines)} 条K线数据")
    
    # 显示第一条
    if klines:
        k = klines[0]
        print(f"\n第一条K线:")
        print(f"  时间: {k['t']}")
        print(f"  开盘: {k['o']}")
        print(f"  最高: {k['h']}")
        print(f"  最低: {k['l']}")
        print(f"  收盘: {k['c']}")
        print(f"  成交量: {k['v']:,}")
        print(f"  成交额: {k['tu']:,.2f}")
```

### cURL 示例

```bash
curl -X GET "https://api.itick.org/stock/kline?region=HK&code=700&kType=2&limit=10" \
     -H "accept: application/json" \
     -H "token: your_api_key_here"
```

## 💡 使用建议

### 1. 时间戳处理

```python
from datetime import datetime

timestamp_ms = 1741239000000
dt = datetime.fromtimestamp(timestamp_ms / 1000)
print(dt.strftime('%Y-%m-%d %H:%M:%S'))
# 输出: 2025-01-04 09:30:00
```

### 2. 数据可视化

使用标准 OHLC 格式，可以直接对接：
- **matplotlib.finance** (mplfinance)
- **plotly**
- **TradingView**
- 其他金融图表库

```python
import pandas as pd
import mplfinance as mpf

# 转换为 DataFrame
df = pd.DataFrame(klines)
df['datetime'] = pd.to_datetime(df['t'], unit='ms')
df.set_index('datetime', inplace=True)
df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'}, inplace=True)

# 绘制K线图
mpf.plot(df, type='candle', volume=True, title='Stock Kline Chart')
```

### 3. 技术指标计算

可以使用 **TA-Lib** 或 **pandas-ta** 计算技术指标：

```python
import talib as ta

# 计算移动平均线
df['MA5'] = ta.SMA(df['Close'], timeperiod=5)
df['MA20'] = ta.SMA(df['Close'], timeperiod=20)

# 计算MACD
df['MACD'], df['Signal'], df['Hist'] = ta.MACD(df['Close'])

# 计算RSI
df['RSI'] = ta.RSI(df['Close'], timeperiod=14)
```

## 🔍 数据验证

### 检查数据完整性

```python
def validate_kline(kline):
    """验证K线数据的合理性"""
    required_fields = ['t', 'o', 'h', 'l', 'c', 'v', 'tu']
    
    # 检查必需字段
    for field in required_fields:
        if field not in kline:
            return False, f"缺少字段: {field}"
    
    # 检查价格关系
    if not (kline['l'] <= kline['o'] <= kline['h']):
        return False, "开盘价超出高低价范围"
    
    if not (kline['l'] <= kline['c'] <= kline['h']):
        return False, "收盘价超出高低价范围"
    
    # 检查成交量
    if kline['v'] < 0:
        return False, "成交量不能为负数"
    
    return True, "OK"

# 使用示例
for k in klines:
    valid, msg = validate_kline(k)
    if not valid:
        print(f"数据异常: {msg}, K线: {k}")
```

## 📚 相关文档

- [iTick API 官方文档](https://docs.itick.org/)
- [股票K线 API](https://docs.itick.org/rest-api/stocks/stock-kline)
- [REST API 基础](https://docs.itick.org/rest-api/basics/symbol-list)

---

**更新时间**: 2025-11-30  
**API 版本**: v1  
**文档状态**: kType 映射关系需进一步验证
