"""
Sector Analysis Tool - 板块分析工具
分析行业板块和概念板块的强弱、资金流向和投资机会
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..itick_client import get_client, ItickAPIError


class SectorAnalysisTool:
    """板块分析工具 - 分析行业板块和概念板块"""
    
    name = "itick_sector_analysis"
    description = """分析【行业板块和概念板块】的强弱、资金流向和投资机会，识别市场热点。

⚠️ **重要提示 - 工具适用范围**:
- ✅ 适用于: 行业板块、概念板块（如科技板块、医药板块、新能源板块、半导体板块等）
- ❌ 不适用于: 大盘指数（如恒生指数、上证指数等）→ 请使用 itick_index_analysis
- ❌ 不适用于: 个股（如腾讯、阿里巴巴等具体公司）→ 请使用 itick_stock_quote 等个股工具

🔍 **板块关键词识别**:
当用户提到以下词汇时，应该使用本工具：
- "科技板块"、"医药板块"、"消费板块"、"金融板块"
- "半导体板块"、"新能源板块"、"芯片板块"
- "人工智能板块"、"ChatGPT概念"、"元宇宙概念"

📊 **分析对象**:
- 🏭 行业板块: 科技、医药、消费、金融、地产、能源、军工等
- 💡 概念板块: 人工智能、半导体、新能源车、元宇宙、ChatGPT等
- 🌍 地域板块: 京津冀、长三角、粤港澳、成渝等
- 📈 主题板块: 国企改革、一带一路、自贸区等

💡 **核心功能**:
- 板块实时涨跌排名
- 板块内个股表现分析
- 板块资金流向统计
- 板块轮动趋势识别
- 强势板块龙头股推荐

📍 **常见板块**:
- 科技板块: 半导体、软件、云计算、5G、人工智能
- 医药板块: 创新药、医疗器械、疫苗、中药
- 消费板块: 白酒、家电、食品饮料、汽车
- 金融板块: 银行、保险、券商、信托
- 周期板块: 煤炭、有色、钢铁、化工
- 新能源: 光伏、风电、储能、新能源车

💡 **主要用途**:
- 识别市场热点板块
- 把握板块轮动机会
- 筛选强势板块龙头
- 规避弱势板块风险
- 跟踪资金流向方向

🔔 **分析维度**:
- 📈 涨跌排名: 板块当日/近期涨跌幅
- 💰 资金流向: 板块资金净流入/流出
- 🔥 活跃度: 板块成交额占比
- 👑 龙头股: 板块内领涨股票
- 📊 估值水平: 板块整体PE/PB

💡 **示例查询**:
- "分析今日涨幅前10的板块"
- "查看新能源板块的资金流向"
- "对比医药和科技板块的强弱"
- "找出人工智能板块的龙头股"
"""
    
    parameters = {
        "type": "object",
        "properties": {
            "stocks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "region": {
                            "type": "string",
                            "description": "市场代码"
                        },
                        "code": {
                            "type": "string",
                            "description": "股票代码"
                        },
                        "name": {
                            "type": "string",
                            "description": "股票名称"
                        },
                        "sector": {
                            "type": "string",
                            "description": "所属板块"
                        }
                    },
                    "required": ["region", "code", "sector"]
                },
                "description": "板块内的股票列表。例如: [{region:'SH', code:'600519', name:'茅台', sector:'白酒'}]",
                "minItems": 2
            },
            "period": {
                "type": "string",
                "enum": ["day", "week", "month"],
                "description": "分析周期",
                "default": "day"
            },
            "days": {
                "type": "integer",
                "description": "历史分析天数",
                "default": 10,
                "minimum": 5,
                "maximum": 60
            }
        },
        "required": ["stocks"]
    }
    
    @staticmethod
    async def run(arguments: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """执行板块分析"""
        try:
            stocks = arguments.get("stocks", [])
            period = arguments.get("period", "day")
            days = arguments.get("days", 10)
            
            if not stocks or len(stocks) < 2:
                return {
                    "content": [{
                        "type": "text",
                        "text": "❌ 至少需要2只股票才能进行板块分析\n\n示例: [{\"region\": \"SH\", \"code\": \"600519\", \"name\": \"茅台\", \"sector\": \"白酒\"}]"
                    }],
                    "isError": True
                }
            
            client = get_client(api_key)
            
            # 收集股票数据
            stock_results = []
            sector_groups = {}  # 按板块分组
            
            for stock_info in stocks:
                region = stock_info.get("region")
                code = stock_info.get("code")
                name = stock_info.get("name", code)
                sector = stock_info.get("sector", "未分类")
                
                if not region or not code:
                    continue
                
                try:
                    # 获取实时行情
                    quote_data = await client.get_stock_quote(str(region), str(code))
                    
                    # 获取K线数据（计算资金流向）
                    kline_data = await client.get_stock_kline(
                        region=str(region),
                        code=str(code),
                        period=period,
                        limit=days
                    )
                    
                    latest_price = quote_data.get('ld', 0)
                    change_pct = quote_data.get('chp', 0)
                    volume = quote_data.get('v', 0)
                    turnover = quote_data.get('tu', 0)
                    
                    # 计算资金流向（简化版）
                    money_flow = 0
                    if kline_data:
                        for kline in kline_data:
                            open_p = float(kline.get('o', 0))
                            close_p = float(kline.get('c', 0))
                            tu = float(kline.get('tu', 0))
                            
                            if close_p >= open_p:
                                money_flow += tu
                            else:
                                money_flow -= tu
                    
                    stock_data = {
                        "name": name,
                        "region": region,
                        "code": code,
                        "sector": sector,
                        "latest_price": latest_price,
                        "change_pct": change_pct,
                        "volume": volume,
                        "turnover": turnover,
                        "money_flow": money_flow
                    }
                    
                    stock_results.append(stock_data)
                    
                    # 按板块分组
                    if sector not in sector_groups:
                        sector_groups[sector] = []
                    sector_groups[sector].append(stock_data)
                    
                except Exception as e:
                    continue
            
            if not stock_results:
                return {
                    "content": [{
                        "type": "text",
                        "text": "❌ 未能获取任何股票数据"
                    }],
                    "isError": True
                }
            
            # 生成报告
            output = f"""## 📊 板块分析报告

**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**分析周期**: {period} × {days}天
**分析股票**: {len(stock_results)}只
**涉及板块**: {len(sector_groups)}个

---

"""
            
            # 板块汇总
            sector_summary = []
            
            for sector_name, sector_stocks in sector_groups.items():
                avg_change = sum(s['change_pct'] for s in sector_stocks) / len(sector_stocks)
                total_turnover = sum(s['turnover'] for s in sector_stocks)
                total_money_flow = sum(s['money_flow'] for s in sector_stocks)
                
                # 找龙头股（涨幅最大）
                leader = max(sector_stocks, key=lambda x: x['change_pct'])
                
                sector_summary.append({
                    "name": sector_name,
                    "stock_count": len(sector_stocks),
                    "avg_change": avg_change,
                    "total_turnover": total_turnover,
                    "total_money_flow": total_money_flow,
                    "leader": leader,
                    "stocks": sector_stocks
                })
            
            # 按平均涨跌幅排序
            sector_summary.sort(key=lambda x: x['avg_change'], reverse=True)
            
            output += """### 📈 板块排名

| 排名 | 板块名称 | 平均涨跌 | 成交额 | 资金流向 | 龙头股 |
|------|---------|---------|--------|---------|--------|
"""
            
            for i, sector in enumerate(sector_summary, 1):
                trend = "🟢" if sector['avg_change'] > 0 else "🔴" if sector['avg_change'] < 0 else "⚪"
                flow_trend = "💰流入" if sector['total_money_flow'] > 0 else "💸流出"
                
                output += f"| {i} | {sector['name']} ({sector['stock_count']}只) | {trend} {sector['avg_change']:+.2f}% | ¥{sector['total_turnover']/100000000:.2f}亿 | {flow_trend} | {sector['leader']['name']} ({sector['leader']['change_pct']:+.2f}%) |\n"
            
            output += "\n---\n\n"
            
            # 详细板块分析
            for i, sector in enumerate(sector_summary, 1):
                trend_icon = "🔥" if sector['avg_change'] > 2 else "📈" if sector['avg_change'] > 0 else "📉" if sector['avg_change'] > -2 else "❄️"
                
                output += f"""### {i}. {trend_icon} {sector['name']}板块

**整体表现**
- 📊 平均涨跌: {sector['avg_change']:+.2f}%
- 💵 总成交额: ¥{sector['total_turnover']/100000000:.2f}亿
- 💰 资金流向: {"流入" if sector['total_money_flow'] > 0 else "流出"} ¥{abs(sector['total_money_flow'])/100000000:.2f}亿
- 📈 股票数量: {sector['stock_count']}只

**板块个股表现**

| 股票名称 | 最新价 | 涨跌幅 | 成交额 |
|---------|--------|--------|--------|
"""
                
                # 按涨跌幅排序板块内个股
                sorted_stocks = sorted(sector['stocks'], key=lambda x: x['change_pct'], reverse=True)
                
                for stock in sorted_stocks[:10]:  # 最多显示10只
                    trend = "🟢" if stock['change_pct'] > 0 else "🔴" if stock['change_pct'] < 0 else "⚪"
                    output += f"| {stock['name']} | {stock['latest_price']:.2f} | {trend} {stock['change_pct']:+.2f}% | ¥{stock['turnover']/100000000:.2f}亿 |\n"
                
                # 龙头股推荐
                if sector['avg_change'] > 0:
                    output += f"\n**👑 板块龙头**: {sector['leader']['name']} - 涨幅{sector['leader']['change_pct']:+.2f}%，领涨板块\n"
                
                output += "\n---\n\n"
            
            # 投资建议
            strongest_sector = sector_summary[0]
            weakest_sector = sector_summary[-1]
            
            output += f"""### 💡 投资建议

**🔥 强势板块**: {strongest_sector['name']}
- 平均涨幅: {strongest_sector['avg_change']:+.2f}%
- 资金态度: {"持续流入，市场看好" if strongest_sector['total_money_flow'] > 0 else "资金流出，谨慎参与"}
- 操作建议: {"可关注龙头股和补涨股机会" if strongest_sector['avg_change'] > 1 else "谨慎追高，等待回调"}

**❄️ 弱势板块**: {weakest_sector['name']}
- 平均跌幅: {weakest_sector['avg_change']:+.2f}%
- 资金态度: {"资金流出，市场回避" if weakest_sector['total_money_flow'] < 0 else "资金流入，可能触底"}
- 操作建议: {"建议回避或减仓" if weakest_sector['avg_change'] < -1 else "可观察是否有止跌迹象"}

**🎯 板块轮动建议**:
1. 强势板块可积极参与，关注龙头股
2. 弱势板块谨慎参与，避免抄底
3. 板块轮动时注意及时换仓
4. 关注资金流向，跟随主力步伐

**⚠️ 风险提示**:
- 板块分析基于历史数据，不保证未来表现
- 板块内个股差异较大，需精选个股
- 市场风格切换时注意板块轮动
- 投资有风险，决策需谨慎

---

*数据来源: iTick API*
*分析时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "*"
            
            return {
                "content": [{
                    "type": "text",
                    "text": output
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
                    "text": f"❌ 系统错误: {str(e)}"
                }],
                "isError": True
            }
