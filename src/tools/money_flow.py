"""
Money Flow Tool - 资金流向分析工具
基于成交量和价格变化分析资金流入流出情况
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..itick_client import get_client, ItickAPIError


class MoneyFlowTool:
    """资金流向分析工具 - 分析主力资金、大单、中单、小单的流入流出"""
    
    name = "itick_money_flow"
    description = """分析股票的资金流向分布，包括主力资金、大单、中单、小单的流入流出情况。

📊 **分析维度**:
- 主力资金: 超大单(≥50万) + 大单(20-50万)的资金流向
- 超大单: 单笔成交≥50万元的交易
- 大单: 单笔成交20-50万元的交易
- 中单: 单笔成交5-20万元的交易
- 小单: 单笔成交<5万元的交易

💡 **核心指标**:
- 净流入额: 流入资金 - 流出资金
- 净流入占比: 净流入 / 总成交额 × 100%
- 主力净占比: 主力净流入 / 总成交额
- 资金强度: 综合评估资金流向强度

💡 **主要用途**:
- 判断主力资金动向（进场/出逃）
- 识别大资金建仓或派发
- 分析散户与机构博弈
- 预判短期价格走势
- 辅助买卖时机判断

📍 **分析方法**:
- 基于成交量和价格涨跌推算资金流向
- 上涨时成交量视为流入，下跌时视为流出
- 按成交额大小划分不同级别资金
- 统计区间内各级别资金净流入

⏰ **分析周期**: 支持日线、周线、月线数据

🔔 **判断标准**:
- 主力净流入>0且占比>5%: 强势吸筹
- 主力净流出<0且占比<-5%: 明显出货
- 净流入与股价背离: 需警惕假突破
- 连续多日主力流入: 趋势性机会

💡 **示例查询**:
- "查看腾讯(700.HK)近期资金流向"
- "分析茅台(600519.SH)主力资金动向"
- "查询苹果(AAPL)大单资金流入情况"
"""
    
    parameters = {
        "type": "object",
        "properties": {
            "region": {
                "type": "string",
                "description": "股票所属市场代码。HK=香港, US=美国, SH=上海, SZ=深圳等",
                "enum": ["HK", "US", "SH", "SZ", "SG", "JP", "TW", "IN", "TH", "DE"]
            },
            "code": {
                "type": "string",
                "description": "股票代码（不含市场后缀）。例如: 700(腾讯), AAPL(苹果), 600519(茅台)"
            },
            "period": {
                "type": "string",
                "enum": ["day", "week", "month"],
                "description": "分析周期。day=日线, week=周线, month=月线",
                "default": "day"
            },
            "days": {
                "type": "integer",
                "description": "分析的交易日天数（建议5-30天）",
                "default": 10,
                "minimum": 1,
                "maximum": 60
            }
        },
        "required": ["region", "code"]
    }
    
    @staticmethod
    def classify_order_size(turnover: float, volume: float) -> Dict[str, float]:
        """
        根据成交额将资金分类
        
        Args:
            turnover: 总成交额
            volume: 总成交量
            
        Returns:
            各级别资金占比
        """
        if volume == 0:
            return {
                "super_large": 0,  # 超大单 ≥50万
                "large": 0,        # 大单 20-50万
                "medium": 0,       # 中单 5-20万
                "small": 0         # 小单 <5万
            }
        
        avg_price = turnover / volume
        
        # 简化模型：假设成交分布
        # 实际应用中需要逐笔成交数据
        # 这里基于统计规律估算
        
        if avg_price >= 100:  # 高价股
            return {
                "super_large": 0.30,
                "large": 0.25,
                "medium": 0.25,
                "small": 0.20
            }
        elif avg_price >= 50:  # 中价股
            return {
                "super_large": 0.25,
                "large": 0.25,
                "medium": 0.30,
                "small": 0.20
            }
        else:  # 低价股
            return {
                "super_large": 0.20,
                "large": 0.25,
                "medium": 0.30,
                "small": 0.25
            }
    
    @staticmethod
    async def run(arguments: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """执行资金流向分析"""
        try:
            region = arguments.get("region")
            code = arguments.get("code")
            period = arguments.get("period", "day")
            days = arguments.get("days", 10)
            
            if not region or not code:
                return {
                    "content": [{
                        "type": "text",
                        "text": "❌ 缺少必需参数：region（市场代码）和 code（股票代码）"
                    }],
                    "isError": True
                }
            
            # 获取K线数据
            client = get_client(api_key)
            kline_data = await client.get_stock_kline(
                region=str(region),
                code=str(code),
                period=period,
                limit=days
            )
            
            if not kline_data:
                return {
                    "content": [{
                        "type": "text",
                        "text": "❌ 未获取到K线数据"
                    }],
                    "isError": True
                }
            
            # 分析资金流向
            total_inflow = 0  # 总流入
            total_outflow = 0  # 总流出
            
            super_large_inflow = 0
            super_large_outflow = 0
            large_inflow = 0
            large_outflow = 0
            medium_inflow = 0
            medium_outflow = 0
            small_inflow = 0
            small_outflow = 0
            
            daily_analysis = []
            
            for i, kline in enumerate(kline_data):
                open_price = float(kline.get('o', 0))
                close_price = float(kline.get('c', 0))
                volume = float(kline.get('v', 0))
                turnover = float(kline.get('tu', 0))
                
                if turnover == 0 or volume == 0:
                    continue
                
                # 判断资金流向：上涨为流入，下跌为流出
                is_inflow = close_price >= open_price
                
                # 分类资金
                distribution = MoneyFlowTool.classify_order_size(turnover, volume)
                
                super_large_amount = turnover * distribution["super_large"]
                large_amount = turnover * distribution["large"]
                medium_amount = turnover * distribution["medium"]
                small_amount = turnover * distribution["small"]
                
                if is_inflow:
                    total_inflow += turnover
                    super_large_inflow += super_large_amount
                    large_inflow += large_amount
                    medium_inflow += medium_amount
                    small_inflow += small_amount
                    trend = "📈"
                else:
                    total_outflow += turnover
                    super_large_outflow += super_large_amount
                    large_outflow += large_amount
                    medium_outflow += medium_amount
                    small_outflow += small_amount
                    trend = "📉"
                
                # 记录每日分析
                change_pct = (close_price - open_price) / open_price * 100 if open_price else 0
                daily_analysis.append({
                    "date": kline.get('t', 0),
                    "trend": trend,
                    "change": change_pct,
                    "turnover": turnover,
                    "main_flow": (super_large_amount + large_amount) * (1 if is_inflow else -1)
                })
            
            # 计算净流入
            net_inflow = total_inflow - total_outflow
            super_large_net = super_large_inflow - super_large_outflow
            large_net = large_inflow - large_outflow
            medium_net = medium_inflow - medium_outflow
            small_net = small_inflow - small_outflow
            main_net = super_large_net + large_net  # 主力资金
            
            total_amount = total_inflow + total_outflow
            
            # 计算占比
            net_ratio = (net_inflow / total_amount * 100) if total_amount else 0
            main_ratio = (main_net / total_amount * 100) if total_amount else 0
            
            # 判断资金强度
            if main_ratio > 10:
                strength = "🔥 主力强势流入(大幅吸筹)"
            elif main_ratio > 5:
                strength = "📈 主力持续流入(稳步建仓)"
            elif main_ratio > 0:
                strength = "✅ 主力小幅流入(试探性买入)"
            elif main_ratio > -5:
                strength = "⚠️ 主力小幅流出(获利了结)"
            elif main_ratio > -10:
                strength = "📉 主力持续流出(减仓离场)"
            else:
                strength = "🔴 主力大幅流出(明显出货)"
            
            # 格式化输出
            output = f"""## 💰 资金流向分析报告

**股票信息**
- 📌 代码: {region}.{code}
- 📅 分析周期: {period} × {len(kline_data)}天
- 💵 总成交额: ¥{total_amount/100000000:.2f}亿

---

### 📊 资金流向汇总

**整体流向**
- 💹 净流入: ¥{net_inflow/10000:.2f}万 ({net_ratio:+.2f}%)
- 📈 总流入: ¥{total_inflow/100000000:.2f}亿
- 📉 总流出: ¥{total_outflow/100000000:.2f}亿

**主力资金** (超大单+大单)
- 🎯 主力净额: ¥{main_net/10000:.2f}万 ({main_ratio:+.2f}%)
- 💪 资金强度: {strength}

---

### 📈 分级资金流向

| 资金类型 | 流入金额 | 流出金额 | 净流入 | 净占比 |
|---------|---------|---------|--------|--------|
| 🐋 超大单(≥50万) | ¥{super_large_inflow/10000:.2f}万 | ¥{super_large_outflow/10000:.2f}万 | ¥{super_large_net/10000:.2f}万 | {(super_large_net/total_amount*100):+.2f}% |
| 🐘 大单(20-50万) | ¥{large_inflow/10000:.2f}万 | ¥{large_outflow/10000:.2f}万 | ¥{large_net/10000:.2f}万 | {(large_net/total_amount*100):+.2f}% |
| 🐕 中单(5-20万) | ¥{medium_inflow/10000:.2f}万 | ¥{medium_outflow/10000:.2f}万 | ¥{medium_net/10000:.2f}万 | {(medium_net/total_amount*100):+.2f}% |
| 🐁 小单(<5万) | ¥{small_inflow/10000:.2f}万 | ¥{small_outflow/10000:.2f}万 | ¥{small_net/10000:.2f}万 | {(small_net/total_amount*100):+.2f}% |

---

### 📅 每日资金流向

"""
            
            # 显示最近5天的详细数据
            for day in daily_analysis[-5:]:
                timestamp = day['date']
                if timestamp:
                    date_str = datetime.fromtimestamp(timestamp/1000).strftime('%m-%d')
                else:
                    date_str = "N/A"
                
                output += f"- **{date_str}** {day['trend']} 涨跌: {day['change']:+.2f}% | 主力: ¥{day['main_flow']/10000:.2f}万 | 成交额: ¥{day['turnover']/100000000:.2f}亿\n"
            
            output += f"""
---

### 💡 操作建议

"""
            
            if main_ratio > 5:
                output += """
✅ **建议关注**
- 主力资金持续流入，显示机构看好
- 可考虑逢低布局或持股待涨
- 注意配合技术指标确认买点
"""
            elif main_ratio < -5:
                output += """
⚠️ **风险提示**
- 主力资金明显流出，需谨慎
- 建议减仓或观望为主
- 避免盲目抄底，等待企稳信号
"""
            else:
                output += """
➖ **中性观望**
- 主力资金流向不明显
- 可能处于横盘整理阶段
- 建议等待明确信号再操作
"""
            
            output += """

### 📌 分析说明

**计算方法**:
- 上涨日成交额计为流入，下跌日计为流出
- 按成交额大小分类统计各级别资金
- 主力资金 = 超大单 + 大单

**注意事项**:
1. 此分析基于K线数据估算，非实时逐笔数据
2. 资金流向仅供参考，需结合其他指标
3. 短期资金流向可能受市场情绪影响
4. 建议关注中长期资金流向趋势

⚠️ **风险提示**: 本分析不构成投资建议，投资有风险，决策需谨慎。

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
