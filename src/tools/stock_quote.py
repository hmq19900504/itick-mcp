"""
Stock Quote Tool - 股票实时报价工具
获取股票的实时行情数据，包括最新价、涨跌幅、成交量等
"""
from typing import Dict, Any, Optional
from datetime import datetime
from ..itick_client import get_client, ItickAPIError


class StockQuoteTool:
    """股票实时报价工具 - 获取最新市场行情"""
    
    name = "itick_stock_quote"
    description = """获取【个股】的实时报价数据，包含最新价格、开高低收、成交量额等实时行情信息。

⚠️ **重要提示 - 工具适用范围**:
- ✅ 适用于: 个股（如腾讯、阿里巴巴、茅台、比亚迪等具体公司股票）
- ❌ 不适用于: 大盘指数（如恒生指数、上证指数、纳斯达克等）→ 请使用 itick_index_analysis
- ❌ 不适用于: 板块指数（如科技板块、医药板块等）→ 请使用 itick_sector_analysis

� **如何识别个股 vs 指数**:
- 个股示例: "腾讯跳水"、"茅台大涨"、"比亚迪暴跌" → 使用本工具
- 指数示例: "恒科跳水"、"上证大跌"、"纳指暴涨" → 使用 itick_index_analysis
- 板块示例: "科技板块领跌"、"医药板块大涨" → 使用 itick_sector_analysis

�📊 **数据内容**:
- 价格信息: 最新价、开盘价、最高价、最低价
- 成交信息: 成交量（股数）、成交额（金额）
- 时间信息: 最新成交时间戳
- 状态信息: 交易状态码

💡 **主要用途**:
- 查看个股当前价格
- 监控实时价格变化
- 分析当日交易情况
- 获取市场最新动态

⏰ **数据更新**: 实时更新，延迟极低（毫秒级）

📍 **使用建议**:
- 适用于需要最新价格的场景
- 可配合K线数据进行综合分析
- 支持全球主要市场（A股、港股、美股等）

🔔 **注意事项**:
- 交易时间内数据实时更新
- 非交易时间显示最后交易日收盘数据
- ts=0 表示正常交易状态

💡 **示例查询**:
- "查询腾讯控股(00700.HK)的最新股价"
- "获取苹果公司(AAPL)实时报价"
- "查看茅台(600519.SH)当前价格"
"""
    
    parameters = {
        "type": "object",
        "properties": {
            "region": {
                "type": "string",
                "description": "股票所属市场代码。HK=香港, US=美国, SH=上海, SZ=深圳, SG=新加坡, JP=日本, TW=台湾, IN=印度, TH=泰国, DE=德国等",
                "enum": ["HK", "US", "SH", "SZ", "SG", "JP", "TW", "IN", "TH", "DE", "MX", "MY", "TR", "ES", "NL", "GB", "ID", "VN", "KR"]
            },
            "code": {
                "type": "string",
                "description": "股票代码（不含市场后缀和前导零）。例如: 700(腾讯), AAPL(苹果), 600519(茅台), 1(长和), 000001(平安银行)"
            }
        },
        "required": ["region", "code"]
    }
    
    @staticmethod
    async def run(arguments: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """执行实时报价查询"""
        try:
            region = arguments.get("region")
            code = arguments.get("code")
            
            if not region or not code:
                return {
                    "content": [{
                        "type": "text",
                        "text": "❌ 缺少必需参数：region（市场代码）和 code（股票代码）\n\n示例: region='HK', code='700'"
                    }],
                    "isError": True
                }
            
            region_str = str(region)
            code_str = str(code)
            
            # 调用 iTick API
            client = get_client(api_key)
            data = await client.get_stock_quote(region_str, code_str)
            
            # 解析时间戳
            timestamp = data.get('t', 0)
            if timestamp:
                dt = datetime.fromtimestamp(timestamp / 1000)
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                time_str = 'N/A'
            
            # 格式化数字
            latest_price = data.get('ld', 'N/A')
            open_price = data.get('o', 'N/A')
            high_price = data.get('h', 'N/A')
            low_price = data.get('l', 'N/A')
            volume = data.get('v', 0)
            turnover = data.get('tu', 0)
            
            # 计算涨跌
            if isinstance(latest_price, (int, float)) and isinstance(open_price, (int, float)) and open_price:
                change = latest_price - open_price
                change_pct = (change / open_price * 100)
                if change > 0:
                    change_str = f"📈 +{change:.2f} (+{change_pct:.2f}%)"
                elif change < 0:
                    change_str = f"📉 {change:.2f} ({change_pct:.2f}%)"
                else:
                    change_str = f"➡️ 0.00 (0.00%)"
            else:
                change_str = "N/A"
            
            # 交易状态
            ts_code = data.get('ts', -1)
            if ts_code == 0:
                status = "✅ 正常交易"
            else:
                status = f"⚠️ 状态码: {ts_code}"
            
            # 格式化输出
            result = f"""## 📊 股票实时报价

**股票信息**
- 📌 代码: {data.get('s', code_str)}
- 🌍 市场: {region_str}
- ⏰ 更新时间: {time_str}
- 🚦 交易状态: {status}

**价格信息**
- 💰 最新价: **{latest_price}**
- 📊 涨跌: {change_str}
- 🔼 今开: {open_price}
- ⬆️  今高: {high_price}
- ⬇️  今低: {low_price}

**成交信息**
- 📦 成交量: {volume:,} 股
- 💵 成交额: ¥{turnover:,.2f}

---
**提示**: 
- 数据实时更新，延迟极低
- 交易时间外显示最后收盘价
- 可配合K线和盘口数据进行深入分析

*数据来源: iTick API*
*查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
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
                    "text": f"❌ iTick API 错误: [{e.code}] {e.message}\n\n可能的原因:\n- 股票代码不存在或格式错误\n- 市场代码与股票不匹配\n- API Key无效或已过期\n\n建议:\n- 检查股票代码是否正确（去掉市场后缀）\n- 确认市场代码准确（如港股用HK，A股用SH/SZ）"
                }],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"❌ 系统错误: {str(e)}\n\n请检查网络连接或稍后重试。"
                }],
                "isError": True
            }
