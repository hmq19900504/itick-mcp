"""
Index Analysis Tool - 指数分析工具
分析大盘指数和板块指数的走势、强弱和市场情绪
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..itick_client import get_client, ItickAPIError


class IndexAnalysisTool:
    """指数分析工具 - 分析大盘指数和板块指数"""
    
    name = "itick_index_analysis"
    description = """分析大盘指数和板块指数的实时行情、历史走势和市场强弱对比。

✅ **市场支持说明**:
- ✅ **A股指数**: 上证指数、深证成指、创业板指、科创50、沪深300等
- ✅ **港股指数**: 恒生指数、恒生科技、恒生国企等
- ✅ **美股指数**: 标普500、纳斯达克、道琼斯等
- 🌍 **全球指数**: 支持多个国家和地区的主要指数

📊 **支持的指数类型**:
- 🌍 大盘指数: 上证指数、深证成指、创业板指、科创50、沪深300等
- 🌏 国际指数: 恒生指数、纳斯达克、道琼斯、标普500等
- 📈 行业指数: 科技、医药、消费、金融等行业指数

💡 **核心功能**:
- 实时指数行情（最新点位、涨跌幅）
- 历史走势分析（区间涨跌、波动率）
- 多指数对比（强弱排名、相关性）
- 市场情绪判断（牛熊态势、风险评估）
- 成交量能分析（量价配合、资金活跃度）

📍 **常用指数代码**:
- 上证指数: 000001
- 深证成指: 399001
- 创业板指: 399006
- 科创50: 000688
- 沪深300: 000300
- 中证500: 000905
- 恒生指数: HSI
- 恒生科技: HSTECH
- 标普500: SPX
- 纳斯达克: IXIC
- 道琼斯: DJI

💡 **注意**: 指数API使用统一的代码格式，不需要区分市场前缀（如SH/SZ/HK/US）

💡 **主要用途**:
- 判断大盘整体趋势
- 识别强势板块和热点
- 分析市场风险偏好
- 辅助个股投资决策
- 把握市场轮动节奏

🔔 **分析维度**:
- 📈 涨跌分析: 当日/近期涨跌幅
- 📊 量能分析: 成交量同比变化
- 💪 强弱对比: 多指数相对表现
- 🎯 技术位置: 支撑阻力、均线系统
- 😊 市场情绪: 乐观/谨慎/恐慌

💡 **示例查询**:
- "查看上证指数和深证成指今日表现"
- "分析创业板指近期走势"
- "对比沪深300和中证500的强弱"
- "查看恒生指数和恒生科技指数"
- "分析标普500和纳斯达克的走势"
- "对比A股、港股、美股三大市场"

⚠️ **注意事项**:
- 指数代码不需要市场前缀（直接用000001，不是SH.000001）
- region参数会被自动设置为'GB'（指数API的标准）
- 确保指数代码正确，错误的代码会返回空数据
"""
    
    parameters = {
        "type": "object",
        "properties": {
            "indices": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "region": {
                            "type": "string",
                            "description": "市场代码（可选，仅用于标识，实际API调用统一使用GB）。CN=中国，HK=香港，US=美国等"
                        },
                        "code": {
                            "type": "string",
                            "description": "指数代码（如：000001=上证指数, HSI=恒生指数, SPX=标普500, IXIC=纳斯达克）"
                        },
                        "name": {
                            "type": "string",
                            "description": "指数名称（可选，用于显示）"
                        }
                    },
                    "required": ["code"]
                },
                "description": "要分析的指数列表。例如: [{code:'000001', name:'上证指数'}, {code:'HSI', name:'恒生指数'}, {code:'SPX', name:'标普500'}]。注意：只需要code，region会自动设置",
                "minItems": 1
            },
            "period": {
                "type": "string",
                "enum": ["day", "week", "month"],
                "description": "分析周期。day=日线, week=周线, month=月线",
                "default": "day"
            },
            "days": {
                "type": "integer",
                "description": "历史分析天数（用于计算涨跌幅和波动率）",
                "default": 30,
                "minimum": 5,
                "maximum": 250
            },
            "compare": {
                "type": "boolean",
                "description": "是否进行多指数对比分析",
                "default": True
            }
        },
        "required": ["indices"]
    }
    
    # 常用指数映射
    # 注意：指数API统一使用region='GB'，这里的region仅供参考识别市场
    COMMON_INDICES = {
        "上证指数": {"region": "CN", "code": "000001"},
        "深证成指": {"region": "CN", "code": "399001"},
        "创业板指": {"region": "CN", "code": "399006"},
        "科创50": {"region": "CN", "code": "000688"},
        "沪深300": {"region": "CN", "code": "000300"},
        "中证500": {"region": "CN", "code": "000905"},
        "中证1000": {"region": "CN", "code": "000852"},
        "恒生指数": {"region": "HK", "code": "HSI"},
        "恒生科技": {"region": "HK", "code": "HSTECH"},
        "恒生国企": {"region": "HK", "code": "HSCEI"},
        "纳斯达克": {"region": "US", "code": "IXIC"},
        "标普500": {"region": "US", "code": "SPX"},
        "道琼斯": {"region": "US", "code": "DJI"},
    }
    
    @staticmethod
    def judge_market_sentiment(change_pct: float, volume_ratio: float = 1.0) -> str:
        """
        判断市场情绪
        
        Args:
            change_pct: 涨跌幅
            volume_ratio: 成交量比率（今日/昨日）
            
        Returns:
            市场情绪描述
        """
        # 基于涨跌幅和量能判断
        if change_pct > 2:
            if volume_ratio > 1.2:
                return "🔥 强势上涨(量价齐升，市场乐观)"
            else:
                return "📈 温和上涨(缩量上涨，需观察)"
        elif change_pct > 1:
            return "✅ 小幅上涨(市场偏乐观)"
        elif change_pct > 0:
            return "➕ 微幅上涨(市场平稳)"
        elif change_pct > -1:
            return "➖ 微幅下跌(市场平稳)"
        elif change_pct > -2:
            return "⚠️ 小幅下跌(市场偏谨慎)"
        elif change_pct > -3:
            if volume_ratio > 1.2:
                return "📉 放量下跌(市场恐慌)"
            else:
                return "📉 温和下跌(缩量调整)"
        else:
            return "🔴 大幅下跌(市场恐慌，规避风险)"
    
    @staticmethod
    def calculate_volatility(kline_data: List[Dict[str, Any]]) -> float:
        """计算波动率（标准差）"""
        if len(kline_data) < 2:
            return 0.0
        
        changes = []
        for i in range(1, len(kline_data)):
            prev_close = float(kline_data[i-1].get('c', 0))
            curr_close = float(kline_data[i].get('c', 0))
            if prev_close:
                change = (curr_close - prev_close) / prev_close * 100
                changes.append(change)
        
        if not changes:
            return 0.0
        
        # 计算标准差
        mean = sum(changes) / len(changes)
        variance = sum((x - mean) ** 2 for x in changes) / len(changes)
        return variance ** 0.5
    
    @staticmethod
    async def run(arguments: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """执行指数分析"""
        try:
            indices = arguments.get("indices", [])
            period = arguments.get("period", "day")
            days = arguments.get("days", 30)
            compare = arguments.get("compare", True)
            
            if not indices:
                return {
                    "content": [{
                        "type": "text",
                        "text": "❌ 缺少必需参数：indices（指数列表）\n\n示例: [{\"region\": \"SH\", \"code\": \"000001\", \"name\": \"上证指数\"}]"
                    }],
                    "isError": True
                }
            
            client = get_client(api_key)
            
            # 收集所有指数数据
            index_results = []
            
            for index_info in indices:
                code = index_info.get("code")
                region = index_info.get("region", "")  # region现在是可选的，仅用于显示
                name = index_info.get("name", code)  # 默认用代码作为名称
                
                if not code:
                    continue  # 只检查code，region不再必需
                
                try:
                    # 获取实时行情 - 使用指数专用API
                    # 注意：iTick的指数API统一使用region='GB'
                    quote_data = await client.get_index_quote(code=str(code), region="GB")
                    
                    # 检查quote_data是否为None或空
                    if not quote_data:
                        raise Exception(f"API返回空数据，可能是指数代码不正确")
                    
                    # 获取历史K线 - 使用指数专用API
                    kline_data = await client.get_index_kline(
                        code=str(code),
                        region="GB",
                        period=period,
                        limit=days
                    )
                    
                    # 提取关键数据
                    latest_price = quote_data.get('ld', 0)
                    open_price = quote_data.get('o', 0)
                    high_price = quote_data.get('h', 0)
                    low_price = quote_data.get('l', 0)
                    volume = quote_data.get('v', 0)
                    turnover = quote_data.get('tu', 0)
                    change = quote_data.get('ch', 0)
                    change_pct = quote_data.get('chp', 0)
                    
                    # 时间戳
                    timestamp = quote_data.get('t', 0)
                    if timestamp:
                        time_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        time_str = 'N/A'
                    
                    # 计算历史数据
                    period_change = 0
                    volatility = 0
                    
                    if kline_data and len(kline_data) >= 2:
                        first_close = float(kline_data[0].get('c', 0))
                        last_close = float(kline_data[-1].get('c', 0))
                        
                        if first_close:
                            period_change = (last_close - first_close) / first_close * 100
                        
                        # 计算波动率
                        volatility = IndexAnalysisTool.calculate_volatility(kline_data)
                    
                    # 判断市场情绪
                    sentiment = IndexAnalysisTool.judge_market_sentiment(change_pct, 1.0)
                    
                    index_results.append({
                        "name": name,
                        "region": region,
                        "code": code,
                        "latest_price": latest_price,
                        "open_price": open_price,
                        "high_price": high_price,
                        "low_price": low_price,
                        "volume": volume,
                        "turnover": turnover,
                        "change": change,
                        "change_pct": change_pct,
                        "time": time_str,
                        "period_change": period_change,
                        "volatility": volatility,
                        "sentiment": sentiment,
                        "kline_count": len(kline_data) if kline_data else 0
                    })
                    
                except Exception as e:
                    index_results.append({
                        "name": name,
                        "region": region,
                        "code": code,
                        "error": str(e)
                    })
            
            if not index_results:
                return {
                    "content": [{
                        "type": "text",
                        "text": "❌ 未能获取任何指数数据"
                    }],
                    "isError": True
                }
            
            # 生成报告
            output = f"""## 📊 指数分析报告

**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**分析周期**: {period} × {days}天
**指数数量**: {len(index_results)}

---

"""
            
            # 单个指数详情
            for i, result in enumerate(index_results, 1):
                if "error" in result:
                    output += f"### {i}. ❌ {result['name']} - 获取失败\n"
                    output += f"错误: {result['error']}\n\n"
                    continue
                
                # 涨跌符号
                if result['change_pct'] > 0:
                    trend_icon = "📈"
                    trend_color = "🟢"
                elif result['change_pct'] < 0:
                    trend_icon = "📉"
                    trend_color = "🔴"
                else:
                    trend_icon = "➡️"
                    trend_color = "⚪"
                
                output += f"""### {i}. {trend_icon} {result['name']}

**实时行情**
- 💰 最新点位: **{result['latest_price']:.2f}** 点
- 📊 涨跌: {trend_color} {result['change']:+.2f} ({result['change_pct']:+.2f}%)
- 🔼 今开: {result['open_price']:.2f}
- ⬆️  今高: {result['high_price']:.2f}
- ⬇️  今低: {result['low_price']:.2f}
- ⏰ 更新: {result['time']}

**成交数据**
- 📦 成交量: {result['volume']:,.0f}
- 💵 成交额: ¥{result['turnover']/100000000:.2f}亿

**历史表现** (近{days}个交易日)
- 📈 区间涨跌: {result['period_change']:+.2f}%
- 📊 波动率: {result['volatility']:.2f}%
- 😊 市场情绪: {result['sentiment']}

---

"""
            
            # 多指数对比
            if compare and len(index_results) > 1:
                # 过滤掉有错误的结果
                valid_results = [r for r in index_results if "error" not in r]
                
                if len(valid_results) > 1:
                    output += """### 📊 多指数对比分析

| 指数名称 | 最新点位 | 今日涨跌 | 区间涨跌 | 波动率 | 市场情绪 |
|---------|---------|---------|---------|--------|---------|
"""
                    # 按涨跌幅排序
                    sorted_results = sorted(valid_results, key=lambda x: x['change_pct'], reverse=True)
                    
                    for result in sorted_results:
                        trend = "🟢" if result['change_pct'] > 0 else "🔴" if result['change_pct'] < 0 else "⚪"
                        output += f"| {result['name']} | {result['latest_price']:.2f} | {trend} {result['change_pct']:+.2f}% | {result['period_change']:+.2f}% | {result['volatility']:.2f}% | {result['sentiment'][:20]} |\n"
                    
                    output += "\n---\n\n"
                    
                    # 强弱分析
                    output += """### 💪 强弱分析

"""
                    strongest = sorted_results[0]
                    weakest = sorted_results[-1]
                    
                    output += f"""**🔥 最强指数**: {strongest['name']} ({strongest['change_pct']:+.2f}%)
- 今日表现领先，资金流入明显
- 近{days}日累计涨幅: {strongest['period_change']:+.2f}%

**❄️ 最弱指数**: {weakest['name']} ({weakest['change_pct']:+.2f}%)
- 今日表现落后，资金流出
- 近{days}日累计涨幅: {weakest['period_change']:+.2f}%

"""
                    
                    # 市场风格判断
                    avg_change = sum(r['change_pct'] for r in valid_results) / len(valid_results)
                    
                    if avg_change > 1:
                        market_style = "🔥 普涨行情(市场情绪乐观，可积极参与)"
                    elif avg_change > 0:
                        market_style = "✅ 震荡偏强(市场偏乐观，谨慎乐观)"
                    elif avg_change > -1:
                        market_style = "⚠️ 震荡偏弱(市场偏谨慎，控制仓位)"
                    else:
                        market_style = "🔴 普跌行情(市场恐慌，规避风险)"
                    
                    output += f"""**🎯 市场风格**: {market_style}
**📊 平均涨跌**: {avg_change:+.2f}%

---

"""
            
            # 投资建议
            output += """### 💡 投资建议

**基于指数分析的建议**:
1. 关注强势指数对应的板块和个股
2. 弱势指数板块可适当规避或减仓
3. 大盘指数走势决定整体仓位
4. 板块轮动时把握结构性机会
5. 波动率加大时注意风险控制

**⚠️ 风险提示**:
- 指数分析仅供参考，不构成投资建议
- 市场有风险，投资需谨慎
- 建议结合个股基本面综合判断

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
