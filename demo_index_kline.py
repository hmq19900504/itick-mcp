"""
演示：获取指数K线数据和走势分析
"""
import asyncio
from dotenv import load_dotenv

load_dotenv()

from src.itick_client import get_client
from datetime import datetime, timedelta


async def demo_index_kline():
    """演示指数K线获取"""
    print("=" * 80)
    print("📈 指数K线数据获取演示")
    print("=" * 80)
    
    client = get_client()
    
    # 计算日期范围（最近30天）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    
    indices = [
        {"code": "000001", "name": "上证指数"},
        {"code": "HSI", "name": "恒生指数"},
        {"code": "SPX", "name": "标普500"},
    ]
    
    for index in indices:
        print(f"\n{'=' * 80}")
        print(f"📊 {index['name']} ({index['code']})")
        print(f"{'=' * 80}")
        
        try:
            # 方式1：使用日期范围
            kline_data = await client.get_index_kline(
                code=index['code'],
                region='GB',
                start_date=start_str,
                end_date=end_str,
                period='day'
            )
            
            # 或者方式2：使用limit参数（更简单）
            # kline_data = await client.get_index_kline(
            #     code=index['code'],
            #     region='GB',
            #     period='day',
            #     limit=30
            # )
            
            if kline_data and len(kline_data) > 0:
                print(f"✅ 成功获取 {len(kline_data)} 条K线数据")
                print(f"\n最近5天走势：")
                print(f"{'日期':12s} {'开盘':>8s} {'最高':>8s} {'最低':>8s} {'收盘':>8s} {'涨跌幅':>8s} {'成交量':>12s}")
                print("-" * 80)
                
                # 显示最近5条
                recent = kline_data[-5:] if len(kline_data) >= 5 else kline_data
                
                for i, bar in enumerate(recent):
                    timestamp = bar.get('t', 0)
                    date_str = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d') if timestamp else 'N/A'
                    
                    open_p = float(bar.get('o', 0))
                    high = float(bar.get('h', 0))
                    low = float(bar.get('l', 0))
                    close = float(bar.get('c', 0))
                    volume = float(bar.get('v', 0))
                    
                    # 计算涨跌幅
                    if i > 0 and recent[i-1].get('c'):
                        prev_close = float(recent[i-1].get('c', 0))
                        change_pct = ((close - prev_close) / prev_close * 100) if prev_close else 0
                    else:
                        change_pct = 0
                    
                    trend = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
                    
                    print(f"{date_str:12s} {open_p:8.2f} {high:8.2f} {low:8.2f} {close:8.2f} {trend}{change_pct:6.2f}% {volume:12,.0f}")
                
                # 计算技术指标
                if len(kline_data) >= 5:
                    print(f"\n📊 技术分析：")
                    
                    # 计算MA5
                    ma5 = sum(float(k.get('c', 0)) for k in kline_data[-5:]) / 5
                    print(f"   MA5 (5日均线): {ma5:.2f}")
                    
                    # 计算区间涨跌
                    if len(kline_data) >= 2:
                        first_close = float(kline_data[0].get('c', 0))
                        last_close = float(kline_data[-1].get('c', 0))
                        period_change = ((last_close - first_close) / first_close * 100) if first_close else 0
                        print(f"   区间涨跌: {period_change:+.2f}%")
                        
                        # 最高和最低点
                        all_highs = [float(k.get('h', 0)) for k in kline_data]
                        all_lows = [float(k.get('l', 0)) for k in kline_data]
                        print(f"   区间最高: {max(all_highs):.2f}")
                        print(f"   区间最低: {min(all_lows):.2f}")
                        print(f"   振幅: {((max(all_highs) - min(all_lows)) / min(all_lows) * 100):.2f}%")
            else:
                print(f"❌ 未获取到K线数据")
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
        
        await asyncio.sleep(2)  # 避免速率限制


async def demo_different_periods():
    """演示不同周期的K线"""
    print("\n" + "=" * 80)
    print("⏰ 不同周期K线对比")
    print("=" * 80)
    
    client = get_client()
    code = "000001"
    
    periods = [
        ("day", "日线", 20),
        ("week", "周线", 12),
        ("month", "月线", 6),
    ]
    
    for period, name, limit in periods:
        print(f"\n📊 上证指数 - {name}")
        print("-" * 80)
        
        try:
            kline_data = await client.get_index_kline(
                code=code,
                period=period,
                limit=limit
            )
            
            if kline_data:
                print(f"✅ 获取 {len(kline_data)} 条{name}数据")
                
                # 显示最近3条
                recent = kline_data[-3:]
                for bar in recent:
                    timestamp = bar.get('t', 0)
                    date_str = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d') if timestamp else 'N/A'
                    close = float(bar.get('c', 0))
                    print(f"   {date_str}: {close:.2f}")
            
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
        
        await asyncio.sleep(1)


async def main():
    """主函数"""
    print("\n" + "🎯" * 40)
    print("指数K线数据获取和分析演示")
    print("🎯" * 40 + "\n")
    
    # 演示1: 基础K线获取
    await demo_index_kline()
    
    # 演示2: 不同周期
    await demo_different_periods()
    
    print("\n" + "=" * 80)
    print("✅ 演示完成")
    print("=" * 80)
    print("""
💡 使用提示：
1. 使用 get_index_kline() 获取指数K线
2. 支持的周期: 1min, 5min, 60min, day, week, month
3. 可以用 start_date/end_date 或 limit 参数
4. 返回的数据包含: 开盘、最高、最低、收盘、成交量
5. 可以基于K线数据计算各种技术指标
    """)


if __name__ == "__main__":
    asyncio.run(main())
