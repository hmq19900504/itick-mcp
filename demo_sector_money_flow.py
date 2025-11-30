"""
板块资金流向分析工具 - 基于ETF
通过分析板块ETF的价格、成交量、涨跌幅等指标，评估板块资金流向
"""
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from src.itick_client import get_client


# A股主要板块ETF代码
A_STOCK_SECTOR_ETFS = {
    "科技板块": [
        {"name": "半导体ETF", "region": "SH", "code": "512480"},
        {"name": "人工智能ETF", "region": "SH", "code": "515070"},
        {"name": "芯片ETF", "region": "SZ", "code": "159995"},
        {"name": "5G ETF", "region": "SH", "code": "515050"},
    ],
    "消费板块": [
        {"name": "白酒ETF", "region": "SH", "code": "512690"},
        {"name": "消费ETF", "region": "SZ", "code": "159928"},
        {"name": "医药ETF", "region": "SH", "code": "512010"},
    ],
    "金融板块": [
        {"name": "证券ETF", "region": "SH", "code": "512880"},
        {"name": "银行ETF", "region": "SH", "code": "512800"},
        {"name": "保险ETF", "region": "SH", "code": "512910"},
    ],
    "新能源板块": [
        {"name": "新能源车ETF", "region": "SH", "code": "515030"},
        {"name": "光伏ETF", "region": "SH", "code": "515790"},
        {"name": "电池ETF", "region": "SZ", "code": "159755"},
    ],
}

# 港股主要板块ETF
HK_SECTOR_ETFS = {
    "科技板块": [
        {"name": "恒生科技ETF", "region": "HK", "code": "3033"},
        {"name": "互联网科技ETF", "region": "HK", "code": "3022"},
    ],
    "医疗板块": [
        {"name": "医疗保健ETF", "region": "HK", "code": "3067"},
    ],
}


async def analyze_etf_money_flow(client, region: str, code: str, name: str, days: int = 5):
    """
    分析单个ETF的资金流向
    
    Args:
        client: iTick客户端
        region: 市场代码
        code: ETF代码
        name: ETF名称
        days: 分析天数
        
    Returns:
        分析结果字典
    """
    try:
        # 获取实时行情
        quote = await client.get_stock_quote(region, code)
        
        if not quote:
            return {"name": name, "error": "获取行情失败"}
        
        # 获取K线数据
        kline = await client.get_stock_kline(region, code, period="day", limit=days + 1)
        
        if not kline or len(kline) < 2:
            return {"name": name, "error": "获取K线失败"}
        
        # 基础数据
        latest_price = quote.get('ld', 0)
        change_pct = quote.get('chp', 0)
        volume = quote.get('v', 0)
        turnover = quote.get('tu', 0)
        
        # 计算量能比（今日 vs 昨日）
        today_volume = kline[-1].get('v', 0)
        yesterday_volume = kline[-2].get('v', 0)
        volume_ratio = (today_volume / yesterday_volume) if yesterday_volume else 1.0
        
        # 计算近N日涨跌
        period_change = 0
        if len(kline) >= days:
            first_close = kline[-days].get('c', 0)
            last_close = kline[-1].get('c', 0)
            period_change = ((last_close - first_close) / first_close * 100) if first_close else 0
        
        # 资金流向评分（0-100）
        # 涨跌幅权重50%，量能比权重30%，近期趋势20%
        score = (
            (change_pct * 10) * 0.5 +  # 涨1%得5分
            ((volume_ratio - 1) * 100) * 0.3 +  # 放量20%得6分
            (period_change * 2) * 0.2  # 近期涨1%得0.4分
        )
        score = max(0, min(100, score + 50))  # 归一化到0-100
        
        # 资金流向判断
        if change_pct > 2 and volume_ratio > 1.2:
            flow_status = "🔥 强势流入"
        elif change_pct > 0.5 and volume_ratio > 1:
            flow_status = "🟢 持续流入"
        elif change_pct > 0:
            flow_status = "✅ 小幅流入"
        elif change_pct > -0.5:
            flow_status = "⚪ 震荡整理"
        elif change_pct > -2:
            flow_status = "🔴 小幅流出"
        else:
            flow_status = "❌ 大幅流出"
        
        # 估算净流入金额（简化算法）
        # 实际应该用逐笔成交的买卖盘数据
        if change_pct > 0 and volume_ratio > 1:
            net_inflow = turnover * (change_pct / 100) * volume_ratio
        else:
            net_inflow = -turnover * abs(change_pct / 100) * 0.5
        
        return {
            "name": name,
            "code": f"{region}.{code}",
            "price": latest_price,
            "change_pct": change_pct,
            "volume": volume,
            "turnover": turnover,
            "volume_ratio": volume_ratio,
            "period_change": period_change,
            "score": score,
            "flow_status": flow_status,
            "net_inflow": net_inflow,
        }
        
    except Exception as e:
        return {"name": name, "error": str(e)}


async def analyze_sector_money_flow(sector_name: str, etf_list: List[Dict], days: int = 5):
    """
    分析整个板块的资金流向
    
    Args:
        sector_name: 板块名称
        etf_list: ETF列表
        days: 分析天数
        
    Returns:
        板块分析结果
    """
    client = get_client()
    
    print(f"\n{'=' * 80}")
    print(f"💰 {sector_name} - 资金流向分析")
    print(f"{'=' * 80}")
    
    results = []
    
    for etf in etf_list:
        result = await analyze_etf_money_flow(
            client, 
            etf['region'], 
            etf['code'], 
            etf['name'],
            days
        )
        results.append(result)
        await asyncio.sleep(1)  # 避免速率限制
    
    # 过滤错误结果
    valid_results = [r for r in results if 'error' not in r]
    
    if not valid_results:
        print("❌ 未能获取任何数据")
        return
    
    # 显示结果
    print(f"\n{'ETF名称':20s} {'代码':12s} {'涨跌幅':>8s} {'量能比':>8s} {'评分':>6s} {'资金流向':15s} {'净流入':>12s}")
    print("-" * 100)
    
    for r in sorted(valid_results, key=lambda x: x['score'], reverse=True):
        net_inflow_yi = r['net_inflow'] / 100000000  # 转换为亿
        print(f"{r['name']:20s} {r['code']:12s} {r['change_pct']:>7.2f}% "
              f"{r['volume_ratio']:>7.2f}x {r['score']:>5.0f} {r['flow_status']:15s} "
              f"{net_inflow_yi:>11.2f}亿")
    
    # 板块整体评估
    avg_change = sum(r['change_pct'] for r in valid_results) / len(valid_results)
    avg_score = sum(r['score'] for r in valid_results) / len(valid_results)
    total_inflow = sum(r['net_inflow'] for r in valid_results) / 100000000
    
    print(f"\n{'=' * 100}")
    print(f"📊 板块整体评估:")
    print(f"   平均涨跌: {avg_change:+.2f}%")
    print(f"   资金评分: {avg_score:.0f}/100")
    print(f"   净流入额: {total_inflow:+.2f}亿元")
    
    if avg_change > 1 and avg_score > 60:
        print(f"   综合判断: 🔥 强势板块，资金大幅流入")
    elif avg_change > 0 and avg_score > 50:
        print(f"   综合判断: 🟢 活跃板块，资金持续流入")
    elif avg_change > -0.5:
        print(f"   综合判断: ⚪ 震荡板块，资金观望")
    else:
        print(f"   综合判断: 🔴 弱势板块，资金流出")
    
    return valid_results


async def compare_all_sectors():
    """对比所有A股板块的资金流向"""
    print("\n" + "🌟" * 40)
    print("A股板块资金流向全景图")
    print("🌟" * 40)
    
    all_sectors_results = {}
    
    for sector_name, etf_list in A_STOCK_SECTOR_ETFS.items():
        results = await analyze_sector_money_flow(sector_name, etf_list, days=5)
        if results:
            all_sectors_results[sector_name] = results
        await asyncio.sleep(2)
    
    # 板块排名
    print(f"\n\n{'=' * 80}")
    print("🏆 板块资金流向排名")
    print(f"{'=' * 80}\n")
    
    sector_scores = []
    for sector_name, results in all_sectors_results.items():
        avg_score = sum(r['score'] for r in results) / len(results)
        avg_change = sum(r['change_pct'] for r in results) / len(results)
        total_inflow = sum(r['net_inflow'] for r in results) / 100000000
        
        sector_scores.append({
            'name': sector_name,
            'score': avg_score,
            'change': avg_change,
            'inflow': total_inflow
        })
    
    # 按评分排序
    sector_scores.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"{'排名':4s} {'板块':12s} {'评分':>8s} {'平均涨跌':>10s} {'净流入':>12s} {'热度':10s}")
    print("-" * 70)
    
    for i, s in enumerate(sector_scores, 1):
        stars = "⭐" * int(s['score'] / 20)
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        
        print(f"{medal}{i:2d}. {s['name']:12s} {s['score']:>7.0f} "
              f"{s['change']:>9.2f}% {s['inflow']:>11.2f}亿 {stars:10s}")


async def demo_hk_sectors():
    """演示港股板块分析"""
    print("\n" + "🇭🇰" * 40)
    print("港股板块资金流向分析")
    print("🇭🇰" * 40)
    
    for sector_name, etf_list in HK_SECTOR_ETFS.items():
        await analyze_sector_money_flow(sector_name, etf_list, days=5)
        await asyncio.sleep(2)


async def main():
    """主函数"""
    print("\n" + "💎" * 40)
    print("板块资金流向分析系统 (基于ETF)")
    print("💎" * 40)
    
    # 选择演示模式
    print("\n请选择分析模式:")
    print("1. A股全部板块对比")
    print("2. 单个板块详细分析")
    print("3. 港股板块分析")
    
    # 这里为了演示，直接运行模式1
    await compare_all_sectors()
    
    # 也可以演示港股
    # await demo_hk_sectors()
    
    print("\n" + "=" * 80)
    print("✅ 分析完成")
    print("=" * 80)
    
    print("""
💡 使用说明:
1. 本工具通过分析板块ETF的价格、成交量、涨跌幅评估资金流向
2. 评分范围0-100，分数越高表示资金流入越强
3. 净流入金额是估算值，实际需要逐笔成交数据
4. 建议结合多日数据综合判断，避免单日波动

📊 评分标准:
90-100分: 🔥 超强流入，板块极度活跃
70-89分:  🟢 强势流入，资金积极布局
50-69分:  ✅ 温和流入，资金谨慎进场
30-49分:  ⚪ 震荡整理，资金观望
10-29分:  🔴 资金流出，板块走弱
0-9分:    ❌ 大幅流出，避险情绪浓厚
    """)


if __name__ == "__main__":
    asyncio.run(main())
