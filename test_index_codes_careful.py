"""
谨慎测试指数代码 - 避免触发API速率限制
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from src.itick_client import get_client


async def test_single_index(client, name, region, code):
    """测试单个指数"""
    print(f"\n📊 测试 {name}")
    print(f"   代码: region='{region}', code='{code}'")
    
    try:
        # 先测试实时行情
        quote_data = await client.get_stock_quote(region, code)
        
        if quote_data and isinstance(quote_data, dict):
            latest_price = quote_data.get('ld', 0)
            change_pct = quote_data.get('chp', 0)
            name_cn = quote_data.get('n', '')
            
            print(f"   ✅ Quote成功: {name_cn}")
            print(f"      最新点位: {latest_price}")
            print(f"      涨跌幅: {change_pct:+.2f}%")
            
            # 延迟后再测试K线
            await asyncio.sleep(2)
            
            kline_data = await client.get_stock_kline(
                region=region,
                code=code,
                period='day',
                limit=5
            )
            
            if kline_data and isinstance(kline_data, list) and len(kline_data) > 0:
                print(f"   ✅ K线成功: 获取到 {len(kline_data)} 条数据")
                print(f"      最新K线收盘: {kline_data[-1].get('c')}")
                return True
            else:
                print(f"   ⚠️  K线为空")
                return False
        else:
            print(f"   ❌ Quote返回空数据")
            return False
            
    except Exception as e:
        print(f"   ❌ 错误: {str(e)[:80]}")
        return False


async def main():
    """主函数 - 谨慎测试，每次之间有延迟"""
    
    # 根据iTick可能支持的格式测试
    test_indices = [
        # A股指数（已知可用）
        ("上证指数", "SH", "000001"),
        ("深证成指", "SZ", "399001"),
        ("创业板指", "SZ", "399006"),
        
        # 港股指数 - 尝试几种可能的代码格式
        ("恒生指数-HSI", "HK", "HSI"),
        ("恒生指数-800000", "HK", "800000"),
        ("恒生科技-HSTECH", "HK", "HSTECH"),
        
        # 美股指数 - 尝试不同格式
        ("纳斯达克-IXIC", "US", "IXIC"),
        ("纳斯达克-NDX", "US", "NDX"),
        ("标普500-SPX", "US", "SPX"),
        ("标普500-.SPX", "US", ".SPX"),
        ("道琼斯-DJI", "US", "DJI"),
        ("道琼斯-.DJI", "US", ".DJI"),
    ]
    
    client = get_client()
    
    print("=" * 80)
    print("🧪 谨慎测试指数代码（有延迟以避免速率限制）")
    print("=" * 80)
    
    success_count = 0
    
    for name, region, code in test_indices:
        result = await test_single_index(client, name, region, code)
        if result:
            success_count += 1
        
        # 每个测试之间延迟，避免触发速率限制
        await asyncio.sleep(3)
    
    print("\n" + "=" * 80)
    print(f"✅ 测试完成，成功: {success_count}/{len(test_indices)}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
