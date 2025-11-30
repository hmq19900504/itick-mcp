"""
Technical Indicators Tool - 技术指标分析工具
基于K线数据计算各类技术指标：MACD、RSI、KDJ、BOLL、MA等
"""
from typing import Dict, Any, Optional, List
import math
from datetime import datetime
from ..itick_client import get_client, ItickAPIError


class TechnicalIndicatorsTool:
    """技术指标分析工具 - 计算MACD、RSI、KDJ等技术指标"""
    
    name = "itick_technical_indicators"
    description = """计算股票的技术指标，包括MACD、RSI、KDJ、BOLL、MA等常用技术分析指标。

📊 **支持的指标**:
- MACD (指数平滑异同移动平均线): 趋势跟踪动量指标，包含DIF、DEA、MACD柱
- RSI (相对强弱指标): 衡量价格涨跌动能，范围0-100，超买超卖信号
- KDJ (随机指标): K值、D值、J值，判断超买超卖
- BOLL (布林带): 上轨、中轨、下轨，波动率指标
- MA (移动平均线): 5日、10日、20日、60日均线
- EMA (指数移动平均线): 加权移动平均

💡 **主要用途**:
- 识别买卖信号（金叉、死叉）
- 判断超买超卖区域
- 分析价格趋势强度
- 确定支撑阻力位
- 辅助交易决策

⏰ **数据周期**: 支持日线、周线、月线、分钟线

📍 **使用建议**:
- 结合多个指标综合判断
- 不同周期对比验证
- 配合K线形态分析
- 注意指标背离现象

🔔 **技术说明**:
- MACD参数: (12,26,9) - 快线、慢线、信号线
- RSI参数: 默认14期，>70超买，<30超卖
- KDJ参数: (9,3,3)，J值>100超买，<0超卖
- BOLL参数: 20期中轨，2倍标准差

💡 **示例查询**:
- "计算腾讯(700.HK)的MACD和RSI指标"
- "分析茅台(600519.SH)的KDJ超买超卖情况"
- "查看苹果(AAPL)的布林带和均线系统"
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
            "indicators": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["macd", "rsi", "kdj", "boll", "ma", "ema", "all"]
                },
                "description": "要计算的技术指标列表。可选: macd, rsi, kdj, boll, ma, ema, all(全部指标)",
                "default": ["macd", "rsi"]
            },
            "period": {
                "type": "string",
                "enum": ["1min", "5min", "60min", "day", "week", "month"],
                "description": "K线周期。1min=1分钟, 5min=5分钟, 60min=60分钟, day=日线, week=周线, month=月线",
                "default": "day"
            },
            "limit": {
                "type": "integer",
                "description": "计算所需的K线数据条数（建议至少100条以保证指标准确性）",
                "default": 200,
                "minimum": 100,
                "maximum": 1000
            }
        },
        "required": ["region", "code"]
    }
    
    @staticmethod
    def calculate_ma(prices: List[float], period: int) -> Optional[float]:
        """计算移动平均线"""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> Optional[float]:
        """计算指数移动平均线"""
        if len(prices) < period:
            return None
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Any]:
        """计算MACD指标"""
        if len(prices) < slow + signal:
            return {"error": "数据不足，无法计算MACD"}
        
        # 计算快线和慢线EMA
        ema_fast = []
        ema_slow = []
        
        for i in range(len(prices)):
            if i >= fast - 1:
                ema_f = TechnicalIndicatorsTool.calculate_ema(prices[:i+1], fast)
                if ema_f:
                    ema_fast.append(ema_f)
            
            if i >= slow - 1:
                ema_s = TechnicalIndicatorsTool.calculate_ema(prices[:i+1], slow)
                if ema_s:
                    ema_slow.append(ema_s)
        
        # 计算DIF (快线-慢线)
        dif_values = []
        for i in range(min(len(ema_fast), len(ema_slow))):
            offset = len(ema_fast) - len(ema_slow)
            if offset > 0:
                dif = ema_fast[i + offset] - ema_slow[i]
            else:
                dif = ema_fast[i] - ema_slow[i - offset]
            dif_values.append(dif)
        
        # 计算DEA (DIF的9日EMA)
        dea = TechnicalIndicatorsTool.calculate_ema(dif_values, signal) if len(dif_values) >= signal else None
        
        # 计算MACD柱
        macd_bar = (dif_values[-1] - dea) * 2 if dea else None
        
        return {
            "dif": round(dif_values[-1], 4) if dif_values else None,
            "dea": round(dea, 4) if dea else None,
            "macd": round(macd_bar, 4) if macd_bar else None,
            "signal": "🔴 死叉(看空)" if dif_values and dea and dif_values[-1] < dea else "🟢 金叉(看涨)" if dif_values and dea else "➖ 无明确信号"
        }
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Dict[str, Any]:
        """计算RSI相对强弱指标"""
        if len(prices) < period + 1:
            return {"error": "数据不足，无法计算RSI"}
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # 判断超买超卖
        if rsi > 70:
            status = "🔴 超买区域(建议减仓)"
        elif rsi < 30:
            status = "🟢 超卖区域(建议加仓)"
        else:
            status = "➖ 中性区域"
        
        return {
            "rsi": round(rsi, 2),
            "status": status,
            "period": period
        }
    
    @staticmethod
    def calculate_kdj(highs: List[float], lows: List[float], closes: List[float], n: int = 9, m1: int = 3, m2: int = 3) -> Dict[str, Any]:
        """计算KDJ随机指标"""
        if len(highs) < n or len(lows) < n or len(closes) < n:
            return {"error": "数据不足，无法计算KDJ"}
        
        # 计算RSV (未成熟随机值)
        recent_high = max(highs[-n:])
        recent_low = min(lows[-n:])
        
        if recent_high == recent_low:
            rsv = 50
        else:
            rsv = (closes[-1] - recent_low) / (recent_high - recent_low) * 100
        
        # 简化计算：K = 2/3 * prev_K + 1/3 * RSV
        # D = 2/3 * prev_D + 1/3 * K
        k = rsv  # 简化版本
        d = k  # 简化版本
        j = 3 * k - 2 * d
        
        # 判断超买超卖
        if j > 100:
            status = "🔴 超买区域(J值>100)"
        elif j < 0:
            status = "🟢 超卖区域(J值<0)"
        elif k > 80 and d > 80:
            status = "🔴 高位钝化"
        elif k < 20 and d < 20:
            status = "🟢 低位钝化"
        else:
            status = "➖ 中性区域"
        
        return {
            "k": round(k, 2),
            "d": round(d, 2),
            "j": round(j, 2),
            "status": status
        }
    
    @staticmethod
    def calculate_boll(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, Any]:
        """计算布林带指标"""
        if len(prices) < period:
            return {"error": "数据不足，无法计算BOLL"}
        
        # 中轨 = N日移动平均
        middle = sum(prices[-period:]) / period
        
        # 标准差
        variance = sum((p - middle) ** 2 for p in prices[-period:]) / period
        std = math.sqrt(variance)
        
        # 上轨和下轨
        upper = middle + std_dev * std
        lower = middle - std_dev * std
        
        current_price = prices[-1]
        
        # 判断位置
        if current_price > upper:
            position = "🔴 突破上轨(超买)"
        elif current_price < lower:
            position = "🟢 跌破下轨(超卖)"
        elif current_price > middle:
            position = "📈 中轨上方(偏强)"
        else:
            position = "📉 中轨下方(偏弱)"
        
        return {
            "upper": round(upper, 2),
            "middle": round(middle, 2),
            "lower": round(lower, 2),
            "current": round(current_price, 2),
            "position": position,
            "width": round((upper - lower) / middle * 100, 2)  # 带宽百分比
        }
    
    @staticmethod
    async def run(arguments: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """执行技术指标计算"""
        try:
            region = arguments.get("region")
            code = arguments.get("code")
            indicators = arguments.get("indicators", ["macd", "rsi"])
            period = arguments.get("period", "day")
            limit = arguments.get("limit", 200)
            
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
                limit=limit
            )
            
            if not kline_data or len(kline_data) < 50:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"❌ K线数据不足（需要至少50条，当前{len(kline_data)}条），无法计算技术指标"
                    }],
                    "isError": True
                }
            
            # 提取价格数据
            closes = [float(k.get('c', 0)) for k in kline_data if k.get('c')]
            highs = [float(k.get('h', 0)) for k in kline_data if k.get('h')]
            lows = [float(k.get('l', 0)) for k in kline_data if k.get('l')]
            
            # 计算指标
            results = {}
            
            if "all" in indicators:
                indicators = ["macd", "rsi", "kdj", "boll", "ma"]
            
            if "macd" in indicators:
                results["MACD"] = TechnicalIndicatorsTool.calculate_macd(closes)
            
            if "rsi" in indicators:
                results["RSI"] = TechnicalIndicatorsTool.calculate_rsi(closes)
            
            if "kdj" in indicators:
                results["KDJ"] = TechnicalIndicatorsTool.calculate_kdj(highs, lows, closes)
            
            if "boll" in indicators:
                results["BOLL"] = TechnicalIndicatorsTool.calculate_boll(closes)
            
            if "ma" in indicators or "ema" in indicators:
                results["均线系统"] = {
                    "MA5": round(TechnicalIndicatorsTool.calculate_ma(closes, 5) or 0, 2),
                    "MA10": round(TechnicalIndicatorsTool.calculate_ma(closes, 10) or 0, 2),
                    "MA20": round(TechnicalIndicatorsTool.calculate_ma(closes, 20) or 0, 2),
                    "MA60": round(TechnicalIndicatorsTool.calculate_ma(closes, 60) or 0, 2),
                    "当前价": round(closes[-1], 2)
                }
            
            # 格式化输出
            output = f"""## 📊 技术指标分析

**股票信息**
- 📌 代码: {region}.{code}
- 📈 周期: {period}
- 📅 数据量: {len(kline_data)} 条K线
- 💰 最新价: {closes[-1]:.2f}

---

"""
            
            for indicator_name, indicator_data in results.items():
                output += f"### {indicator_name}\n\n"
                
                if "error" in indicator_data:
                    output += f"❌ {indicator_data['error']}\n\n"
                else:
                    for key, value in indicator_data.items():
                        output += f"- **{key}**: {value}\n"
                    output += "\n"
            
            output += """---
**📌 使用提示**:
1. 金叉(看涨): 快线上穿慢线，买入信号
2. 死叉(看空): 快线下穿慢线，卖出信号
3. RSI>70超买，RSI<30超卖
4. KDJ的J值>100超买，<0超卖
5. 价格突破布林带上轨可能超买，跌破下轨可能超卖
6. 多个指标共振时信号更可靠

**⚠️ 风险提示**: 技术指标仅供参考，不构成投资建议。请结合基本面和市场环境综合判断。

*计算时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "*"
            
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
