#!/usr/bin/env python3
"""
测试脚本：查询腾讯控股(00700.HK)的K线数据
演示 iTick K线 API 的数据结构
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tools.stock_kline import StockKlineTool


async def test_kline():
    """测试K线查询"""
    
    print("=" * 80)
    print("📊 iTick K线数据结构说明")
    print("=" * 80)
    
    print("\n【K线数据字段说明】")
    print("-" * 80)
    print("字段名 | 类型   | 说明")
    print("-" * 80)
    print("t      | number | 时间戳 (毫秒)")
    print("o      | number | 开盘价 (Open)")
    print("h      | number | 最高价 (High)")
    print("l      | number | 最低价 (Low)")
    print("c      | number | 收盘价 (Close)")
    print("v      | number | 成交量 (Volume)")
    print("tu     | number | 成交额 (Turnover)")
    print("-" * 80)
    print("\n💡 标准的 OHLCV 格式 (Open-High-Low-Close-Volume)\n")
    
    # API Key
    api_key = "d3de0307d463469697ac2faf27f5f5e02cedbde8e2d1400c9476d45adcf6a859"
    
    # 查询参数 - 获取腾讯控股最近10天的日K线
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    arguments = {
        "region": "HK",
        "code": "700",
        "start_date": start_date.strftime("%Y%m%d"),
        "end_date": end_date.strftime("%Y%m%d"),
        "period": "day"  # 日K线
    }
    
    print("=" * 80)
    print("📈 查询腾讯控股(00700.HK)最近30天的日K线")
    print("=" * 80)
    print(f"\n查询参数:")
    print(f"  市场: {arguments['region']}")
    print(f"  代码: {arguments['code']}")
    print(f"  周期: {arguments['period']}")
    print(f"  起始: {arguments['start_date']}")
    print(f"  结束: {arguments['end_date']}")
    print("\n⏳ 正在查询...\n")
    
    # 调用工具
    try:
        result = await StockKlineTool.run(arguments, api_key)
        
        if result.get("isError"):
            print("❌ 查询失败:")
            print(result["content"][0]["text"])
        else:
            print(result["content"][0]["text"])
            
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)


async def test_kline_raw():
    """直接调用 API 查看原始数据结构"""
    
    print("\n" + "=" * 80)
    print("🔍 查看原始 API 响应数据")
    print("=" * 80)
    
    from src.itick_client import ItickClient
    from datetime import datetime, timedelta
    
    api_key = "d3de0307d463469697ac2faf27f5f5e02cedbde8e2d1400c9476d45adcf6a859"
    client = ItickClient(api_key)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)
    
    print(f"\n查询参数: region=HK, code=700, period=day")
    print(f"日期范围: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}")
    print("\n⏳ 正在获取原始数据...\n")
    
    try:
        data = await client.get_stock_kline(
            region="HK",
            code="700",
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            period="day"
        )
        
        print("📦 原始数据结构:")
        print("-" * 80)
        import json
        print(json.dumps(data[:3] if len(data) > 3 else data, indent=2, ensure_ascii=False))
        print("-" * 80)
        print(f"\n✅ 共获取 {len(data)} 条K线数据")
        
        if data:
            print("\n📋 第一条K线数据详解:")
            first = data[0]
            print(f"  时间戳: {first.get('t')} ({datetime.fromtimestamp(first.get('t')/1000).strftime('%Y-%m-%d %H:%M:%S')})") # type: ignore
            print(f"  开盘价: {first.get('o')}")
            print(f"  最高价: {first.get('h')}")
            print(f"  最低价: {first.get('l')}")
            print(f"  收盘价: {first.get('c')}")
            print(f"  成交量: {first.get('v'):,}")
            print(f"  成交额: {first.get('tu'):,.2f}")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()
    
    print("\n" + "=" * 80)


async def test_different_periods():
    """测试不同周期的K线"""
    
    print("\n" + "=" * 80)
    print("⏱️  测试不同周期的K线数据")
    print("=" * 80)
    
    from src.itick_client import ItickClient
    from datetime import datetime, timedelta
    
    api_key = "d3de0307d463469697ac2faf27f5f5e02cedbde8e2d1400c9476d45adcf6a859"
    client = ItickClient(api_key)
    
    periods = [
        ("1min", "1分钟线"),
        ("5min", "5分钟线"),
        ("15min", "15分钟线"),
        ("30min", "30分钟线"),
        ("60min", "60分钟线"),
        ("day", "日线"),
        ("week", "周线"),
        ("month", "月线")
    ]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    
    print(f"\n查询: 腾讯控股(00700.HK)")
    print(f"日期: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}\n")
    
    try:
        for period_code, period_name in periods:
            try:
                data = await client.get_stock_kline(
                    region="HK",
                    code="700",
                    start_date=start_date.strftime("%Y%m%d"),
                    end_date=end_date.strftime("%Y%m%d"),
                    period=period_code
                )
                print(f"✅ {period_name:8s} ({period_code:6s}): {len(data):4d} 条数据")
            except Exception as e:
                print(f"❌ {period_name:8s} ({period_code:6s}): {str(e)}")
        
    finally:
        await client.close()
    
    print("\n" + "=" * 80)


async def main():
    """主函数"""
    await test_kline()
    await test_kline_raw()
    await test_different_periods()


if __name__ == "__main__":
    asyncio.run(main())
