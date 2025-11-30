"""
Stock Tick Tool - 股票Tick数据工具
获取逐笔成交数据，用于高频交易分析
"""
from typing import Dict, Any, Optional
from datetime import datetime
from ..itick_client import get_client, ItickAPIError


class StockTickTool:
    """股票Tick数据工具 - 获取逐笔成交记录"""
    
    name = "itick_stock_tick"
    description = """获取股票实时Tick（逐笔成交）数据，包含最新成交价格、成交量和成交时间。

📊 **数据内容**:
- 最新成交价格 (Latest Price)
- 最新成交量 (Volume)
- 成交时间戳 (Timestamp)

💡 **主要用途**:
- 监控实时成交情况
- 高频交易策略分析
- 观察价格变化频率
- 识别大单成交

⏰ **数据更新**: 实时推送，毫秒级延迟

📍 **使用建议**:
- 适合需要实时监控的场景
- 可用于验证订单执行情况
- 配合盘口深度分析买卖力量

🔔 **注意事项**:
- Tick数据更新频率极高
- 仅显示最新一笔成交
- 需在交易时间内使用最有效

💡 **示例查询**:
- "查看宁德时代(300750.SZ)的最新Tick数据"
- "获取腾讯控股(00700.HK)实时成交记录"
"""
    
    parameters = {
        "type": "object",
        "properties": {
            "region": {
                "type": "string",
                "description": "股票所属市场代码。HK=香港, US=美国, SH=上海, SZ=深圳等",
                "enum": ["HK", "US", "SH", "SZ", "SG", "JP", "TW", "IN", "TH", "DE", "MX", "MY", "TR", "ES", "NL", "GB", "ID", "VN", "KR"]
            },
            "code": {
                "type": "string",
                "description": "股票代码（不含市场后缀）。例如: 300750(宁德时代), 700(腾讯), AAPL(苹果)"
            }
        },
        "required": ["region", "code"]
    }
    
    @staticmethod
    async def run(arguments: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """执行Tick数据查询"""
        try:
            region = arguments.get("region")
            code = arguments.get("code")
            
            if not region or not code:
                return {
                    "content": [{
                        "type": "text",
                        "text": "❌ 缺少必需参数：region（市场代码）和 code（股票代码）"
                    }],
                    "isError": True
                }
            
            region_str = str(region)
            code_str = str(code)
            
            # 调用 iTick API
            client = get_client(api_key)
            data = await client.get_stock_tick(region_str, code_str)
            
            # 解析数据
            stock_code = data.get('s', code_str)
            latest_price = data.get('ld', 'N/A')
            volume = data.get('v', 0)
            timestamp = data.get('t', 0)
            
            # 解析时间
            if timestamp:
                dt = datetime.fromtimestamp(timestamp / 1000)
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 保留毫秒
            else:
                time_str = 'N/A'
            
            # 格式化输出
            result = f"""## 🔄 股票Tick数据（逐笔成交）

**股票信息**
- 📌 代码: {stock_code}
- 🌍 市场: {region_str}

**最新成交**
- 💰 成交价: **{latest_price}**
- 📦 成交量: {volume:,} 股
- ⏰ 成交时间: {time_str}

**说明**
- Tick数据为最新一笔成交记录
- 数据实时更新，延迟毫秒级
- 可用于监控价格实时变化

---
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
                    "text": f"❌ iTick API 错误: [{e.code}] {e.message}\n\n建议检查股票代码和市场代码是否正确。"
                }],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"❌ 系统错误: {str(e)}"
                }],
                "isError": True
            }
