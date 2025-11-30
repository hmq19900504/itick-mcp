"""
测试港股和美股指数的正确代码格式
"""
import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from src.itick_client import get_client


async def test_index_codes():
    """测试不同指数代码格式"""
    
    # 要测试的指数列表
    test_indices = [
        # 美股指数 - 尝试不同格式
        {"name": "纳斯达克", "region": "US", "codes": ["IXIC", ".IXIC", "^IXIC", "COMP"]},
        {"name": "标普500", "region": "US", "codes": ["SPX", ".SPX", "^GSPC", "SPY"]},
        {"name": "道琼斯", "region": "US", "codes": ["DJI", ".DJI", "^DJI", "DJIA"]},
        
        # 港股指数 - 尝试不同格式
        {"name": "恒生指数", "region": "HK", "codes": ["HSI", "^HSI", "0HSI", "800000"]},
        {"name": "恒生科技", "region": "HK", "codes": ["HSTECH", "^HSTECH", "HSTEC"]},
        
        # A股指数（作为对照）
        {"name": "上证指数", "region": "SH", "codes": ["000001"]},
        {"name": "深证成指", "region": "SZ", "codes": ["399001"]},
    ]
    
    client = get_client()
    
    print("=" * 80)
    print("🧪 测试不同市场指数代码格式")
    print("=" * 80)
    
    for index_info in test_indices:
        print(f"\n📊 {index_info['name']} ({index_info['region']})")
        print("-" * 80)
        
        found = False
        for code in index_info['codes']:
            try:
                print(f"   尝试代码: {code} ... ", end="")
                
                # 尝试获取实时行情
                quote_data = await client.get_stock_quote(index_info['region'], code)
                
                if quote_data and isinstance(quote_data, dict):
                    latest_price = quote_data.get('ld', 0)
                    change_pct = quote_data.get('chp', 0)
                    
                    print(f"✅ 成功!")
                    print(f"      最新点位: {latest_price}")
                    print(f"      涨跌幅: {change_pct:+.2f}%")
                    print(f"      ✨ 正确代码: region='{index_info['region']}', code='{code}'")
                    found = True
                    break
                else:
                    print("❌ 返回空数据")
                    
            except Exception as e:
                print(f"❌ {str(e)[:50]}")
        
        if not found:
            print(f"   ⚠️  未找到有效代码格式")


async def test_kline_data():
    """测试K线数据获取"""
    print("\n" + "=" * 80)
    print("🧪 测试K线数据获取")
    print("=" * 80)
    
    # 基于上面测试成功的代码
    test_cases = [
        {"name": "上证指数", "region": "SH", "code": "000001"},
        {"name": "恒生指数", "region": "HK", "code": "HSI"},
        {"name": "纳斯达克", "region": "US", "code": "IXIC"},
    ]
    
    client = get_client()
    
    for test in test_cases:
        print(f"\n📈 {test['name']}")
        print("-" * 80)
        
        try:
            kline_data = await client.get_stock_kline(
                region=test['region'],
                code=test['code'],
                period='day',
                limit=5
            )
            
            if kline_data and isinstance(kline_data, list):
                print(f"✅ 成功获取 {len(kline_data)} 条K线数据")
                if len(kline_data) > 0:
                    latest = kline_data[-1]
                    print(f"   最新K线: 收盘={latest.get('c')}, 成交量={latest.get('v')}")
            else:
                print(f"❌ K线数据为空或格式错误: {type(kline_data)}")
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


async def main():
    """主函数"""
    await test_index_codes()
    await test_kline_data()
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
