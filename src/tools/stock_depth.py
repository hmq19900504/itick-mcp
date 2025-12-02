"""
Stock Depth Tool - 股票盘口深度工具
获取买卖盘口的五档/十档深度数据
"""
from typing import Dict, Any, Optional
from ..itick_client import get_client, ItickAPIError


class StockDepthTool:
    """股票盘口深度工具 - 获取买卖盘五档/十档数据"""
    
    name = "itick_stock_depth"
    description = """获取【个股】盘口深度数据，显示买卖五档或十档的挂单价格、数量和订单数。

⚠️ **重要提示 - 工具适用范围**:
- ✅ 适用于: 个股（如腾讯、阿里巴巴、茅台、比亚迪等具体公司股票）
- ❌ 不适用于: 大盘指数（如恒生指数、上证指数等）→ 请使用 itick_index_analysis
- ❌ 不适用于: 板块（如科技板块、医药板块等）→ 请使用 itick_sector_analysis

📊 **数据内容**:
- 卖盘数据(Ask): 10档卖单价格、挂单量、订单数
- 买盘数据(Bid): 10档买单价格、挂单量、订单数
- 实时更新，毫秒级延迟

💡 **主要用途**:
- 分析市场买卖力量对比
- 识别关键支撑位和阻力位
- 判断大单压盘或托盘情况
- 预判短期价格走向

📍 **使用建议**:
- 买盘力量强于卖盘，价格可能上涨
- 卖盘力量强于买盘，价格可能下跌
- 关注大单挂单情况
- 配合实时报价综合判断

⏰ **数据更新**: 实时刷新，延迟毫秒级

💡 **示例查询**:
- "查看阿里巴巴(09988.HK)的盘口深度"
- "分析比亚迪(002594.SZ)的买卖盘情况"
"""
    
    parameters = {
        "type": "object",
        "properties": {
            "region": {
                "type": "string",
                "description": "市场代码",
                "enum": ["HK", "US", "SH", "SZ", "SG", "JP", "TW", "IN", "TH", "DE", "MX", "MY", "TR", "ES", "NL", "GB", "ID", "VN", "KR"]
            },
            "code": {
                "type": "string",
                "description": "股票代码"
            }
        },
        "required": ["region", "code"]
    }
    
    @staticmethod
    async def run(arguments: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """执行工具逻辑"""
        try:
            region = arguments.get("region")
            code = arguments.get("code")
            
            if not region or not code:
                return {
                    "content": [{
                        "type": "text",
                        "text": "❌ 缺少必需参数：region 和 code"
                    }],
                    "isError": True
                }
            
            # 调用 iTick API
            client = get_client(api_key)
            data = await client.get_stock_depth(region, code)
            
            # 格式化输出
            result = f"""## 📊 股票盘口深度

**股票信息**
- 股票代码: {data.get('s', code)}
- 市场: {region}

**盘口数据**
{data}

---
*数据来源: iTick API*
*说明: 盘口深度反映当前买卖挂单情况，可用于判断支撑阻力位*
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
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"❌ 发生错误: {str(e)}"
                }],
                "isError": True
            }
