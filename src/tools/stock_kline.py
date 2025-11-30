"""
Stock Kline Tool - 股票K线数据工具
获取股票的K线（蜡烛图）数据，用于技术分析和趋势研究
"""
from typing import Dict, Any, Optional
from datetime import datetime
from ..itick_client import get_client, ItickAPIError


class StockKlineTool:
    """股票K线数据工具 - 获取OHLCV格式的K线数据"""
    
    name = "itick_stock_kline"
    description = """获取股票的K线（蜡烛图）历史数据，包含开盘价(Open)、最高价(High)、最低价(Low)、收盘价(Close)、成交量(Volume)、成交额(Turnover)等信息。

📊 **主要用途**:
- 分析股票价格走势和趋势
- 识别支撑位和阻力位
- 计算技术指标（如MA、MACD、RSI等）
- 进行量价分析

⏰ **支持的时间周期**:
- 短周期: 1min(1分钟), 5min(5分钟), 60min(1小时)
- 长周期: day(日线), week(周线), month(月线)

📍 **使用建议**:
- 短期交易分析: 使用1min、5min周期
- 日内交易: 使用60min周期
- 趋势分析: 使用day、week周期
- 长期投资: 使用week、month周期

💡 **示例查询**:
- "获取腾讯(00700.HK)最近30天的日K线数据"
- "查看茅台(600519.SH)2024年1月到3月的周K线"
- "分析苹果(AAPL)最近3个月的日K走势"
"""
    
    parameters = {
        "type": "object",
        "properties": {
            "region": {
                "type": "string",
                "description": "股票所属市场代码。HK=香港, US=美国, SH=上海, SZ=深圳, SG=新加坡, JP=日本, TW=台湾等",
                "enum": ["HK", "US", "SH", "SZ", "SG", "JP", "TW", "IN", "TH", "DE", "MX", "MY", "TR", "ES", "NL", "GB", "ID", "VN", "KR"]
            },
            "code": {
                "type": "string",
                "description": "股票代码（不含市场后缀）。例如: 700(腾讯), AAPL(苹果), 600519(茅台), 000001(平安银行)"
            },
            "start_date": {
                "type": "string",
                "description": "查询起始日期，格式为YYYYMMDD（8位数字）。例如: 20240101表示2024年1月1日",
                "pattern": "^\\d{8}$"
            },
            "end_date": {
                "type": "string",
                "description": "查询结束日期，格式为YYYYMMDD（8位数字）。例如: 20240331表示2024年3月31日",
                "pattern": "^\\d{8}$"
            },
            "period": {
                "type": "string",
                "description": "K线时间周期。可选值: 1min(1分钟), 5min(5分钟), 60min(1小时), day(日线-默认), week(周线), month(月线)",
                "enum": ["1min", "5min", "60min", "day", "week", "month"],
                "default": "day"
            }
        },
        "required": ["region", "code", "start_date", "end_date"]
    }
    
    @staticmethod
    async def run(arguments: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """执行K线数据查询"""
        try:
            region = arguments.get("region")
            code = arguments.get("code")
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")
            period = arguments.get("period", "day")
            
            if not all([region, code, start_date, end_date]):
                return {
                    "content": [{
                        "type": "text",
                        "text": "❌ 缺少必需参数：region(市场), code(代码), start_date(起始日期), end_date(结束日期)"
                    }],
                    "isError": True
                }
            
            # 类型断言，因为上面已经检查过了
            region_str = str(region)
            code_str = str(code)
            start_date_str = str(start_date)
            end_date_str = str(end_date)
            period_str = str(period)
            
            # 调用 iTick API
            client = get_client(api_key)
            kline_data = await client.get_stock_kline(
                region_str, code_str, start_date_str, end_date_str, period_str
            )
            
            # 格式化K线数据
            if isinstance(kline_data, list) and len(kline_data) > 0:
                # 构建Markdown表格
                table_header = "| 时间 | 开盘(O) | 最高(H) | 最低(L) | 收盘(C) | 成交量(V) | 成交额(T) |\n|------|---------|---------|---------|---------|-----------|----------|\n"
                table_rows = ""
                
                # 显示最新的20条数据
                display_data = kline_data[-20:] if len(kline_data) > 20 else kline_data
                
                for item in display_data:
                    # 解析时间戳
                    timestamp = item.get('t', 0)
                    if timestamp:
                        dt = datetime.fromtimestamp(timestamp / 1000)
                        if period in ['1min', '5min', '60min']:
                            time_str = dt.strftime('%m-%d %H:%M')
                        else:
                            time_str = dt.strftime('%Y-%m-%d')
                    else:
                        time_str = 'N/A'
                    
                    open_price = item.get('o', 'N/A')
                    high = item.get('h', 'N/A')
                    low = item.get('l', 'N/A')
                    close = item.get('c', 'N/A')
                    volume = item.get('v', 0)
                    turnover = item.get('tu', 0)
                    
                    # 格式化数字
                    volume_str = f"{volume:,.0f}" if isinstance(volume, (int, float)) else str(volume)
                    turnover_str = f"{turnover:,.0f}" if isinstance(turnover, (int, float)) else str(turnover)
                    
                    table_rows += f"| {time_str} | {open_price} | {high} | {low} | {close} | {volume_str} | {turnover_str} |\n"
                
                # 计算统计信息
                total_count = len(kline_data)
                if total_count > 0:
                    first_close = kline_data[0].get('c', 0)
                    last_close = kline_data[-1].get('c', 0)
                    if first_close and last_close:
                        change = last_close - first_close
                        change_pct = (change / first_close * 100) if first_close else 0
                        trend = "📈 上涨" if change > 0 else "📉 下跌" if change < 0 else "➡️ 持平"
                    else:
                        change = 0
                        change_pct = 0
                        trend = "N/A"
                else:
                    change = 0
                    change_pct = 0
                    trend = "N/A"
                
                result = f"""## � 股票K线数据分析

**基本信息**
- 股票代码: {code_str}
- 市场: {region_str}
- 时间周期: {period_str}
- 日期范围: {start_date_str[:4]}-{start_date_str[4:6]}-{start_date_str[6:8]} 至 {end_date_str[:4]}-{end_date_str[4:6]}-{end_date_str[6:8]}
- 数据条数: {total_count}条

**区间表现**
- 期初收盘: {kline_data[0].get('c', 'N/A') if total_count > 0 else 'N/A'}
- 期末收盘: {kline_data[-1].get('c', 'N/A') if total_count > 0 else 'N/A'}
- 区间涨跌: {change:+.2f} ({change_pct:+.2f}%)
- 趋势: {trend}

**K线数据明细** (最新 {len(display_data)} 条)

{table_header}{table_rows}

---
**数据字段说明**:
- O(Open): 开盘价
- H(High): 最高价
- L(Low): 最低价  
- C(Close): 收盘价
- V(Volume): 成交量（股）
- T(Turnover): 成交额（元）

*数据来源: iTick API*
"""
            else:
                result = f"""## � 股票K线数据

**查询信息**
- 股票代码: {code}
- 市场: {region}
- 周期: {period}
- 日期范围: {start_date} ~ {end_date}

⚠️ **未查询到K线数据**

可能的原因:
1. 日期范围内该股票未开市或无交易
2. 股票代码不正确或不存在
3. 该市场不支持此周期的K线数据
4. 起始日期晚于结束日期

建议:
- 检查股票代码是否正确
- 调整日期范围
- 尝试其他时间周期

---
*数据来源: iTick API*
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
                    "text": f"❌ iTick API 错误: [{e.code}] {e.message}\n\n建议检查:\n- API Key是否有效\n- 股票代码和市场代码是否匹配\n- 日期格式是否正确(YYYYMMDD)"
                }],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"❌ 系统错误: {str(e)}\n\n如果问题持续，请检查网络连接或联系技术支持。"
                }],
                "isError": True
            }
