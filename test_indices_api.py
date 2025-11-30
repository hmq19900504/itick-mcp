"""
测试使用正确的 Indices API 获取指数数据
根据官方文档：https://docs.itick.org/rest-api/indices/indices-quote
"""
import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('ITICK_API_KEY')
BASE_URL = "https://api.itick.org"


async def test_indices_quote(region: str, code: str, name: str):
    """测试指数实时行情 API"""
    url = f"{BASE_URL}/indices/quote"
    
    headers = {
        "accept": "application/json",
        "token": API_KEY
    }
    
    params = {
        "region": region,
        "code": code
    }
    
    print(f"\n📊 测试: {name}")
    print(f"   URL: {url}")
    print(f"   参数: region={region}, code={code}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   响应代码: {data.get('code')}")
                print(f"   响应消息: {data.get('msg')}")
                
                if data.get('code') == 0 and data.get('data'):
                    result = data['data']
                    print(f"   ✅ 成功!")
                    print(f"      代码: {result.get('s')}")
                    print(f"      最新价: {result.get('ld')}")
                    print(f"      开盘价: {result.get('o')}")
                    print(f"      最高价: {result.get('h')}")
                    print(f"      最低价: {result.get('l')}")
                    print(f"      成交量: {result.get('v')}")
                    return True
                else:
                    print(f"   ❌ API返回错误或空数据")
                    print(f"   完整响应: {data}")
                    return False
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"   ❌ 异常: {str(e)}")
        return False


async def test_indices_kline(region: str, code: str, name: str):
    """测试指数K线 API"""
    url = f"{BASE_URL}/indices/kline"
    
    headers = {
        "accept": "application/json",
        "token": API_KEY
    }
    
    params = {
        "region": region,
        "code": code,
        "kType": 2,  # 日K
        "limit": 5
    }
    
    print(f"\n📈 测试K线: {name}")
    print(f"   URL: {url}")
    print(f"   参数: region={region}, code={code}, kType=2, limit=5")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   响应代码: {data.get('code')}")
                
                if data.get('code') == 0:
                    kline_data = data.get('data', [])
                    print(f"   ✅ 成功! 获取到 {len(kline_data)} 条K线数据")
                    if kline_data:
                        latest = kline_data[-1]
                        print(f"      最新K线: 收盘={latest.get('c')}, 成交量={latest.get('v')}")
                    return True
                else:
                    print(f"   ❌ API返回错误")
                    print(f"   完整响应: {data}")
                    return False
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ 异常: {str(e)}")
        return False


async def main():
    """主测试函数"""
    print("=" * 80)
    print("🧪 测试 Indices API（指数专用API）")
    print("=" * 80)
    if API_KEY:
        print(f"API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
    else:
        print("⚠️  API Key 未设置")
    
    # 根据文档示例和常见指数代码测试
    test_cases = [
        # 文档示例：标普500 使用 GB 区域
        {"region": "GB", "code": "SPX", "name": "标普500 (文档示例)"},
        
        # 尝试其他可能的指数代码
        {"region": "US", "code": "SPX", "name": "标普500 (US区域)"},
        {"region": "US", "code": ".SPX", "name": "标普500 (.SPX)"},
        {"region": "US", "code": "IXIC", "name": "纳斯达克 (IXIC)"},
        {"region": "US", "code": ".IXIC", "name": "纳斯达克 (.IXIC)"},
        {"region": "US", "code": "DJI", "name": "道琼斯 (DJI)"},
        {"region": "US", "code": ".DJI", "name": "道琼斯 (.DJI)"},
        
        # 港股指数
        {"region": "HK", "code": "HSI", "name": "恒生指数 (HSI)"},
        {"region": "HK", "code": ".HSI", "name": "恒生指数 (.HSI)"},
        {"region": "HK", "code": "HSTECH", "name": "恒生科技 (HSTECH)"},
        
        # A股指数（对比）
        {"region": "SH", "code": "000001", "name": "上证指数"},
        {"region": "SZ", "code": "399006", "name": "创业板指"},
    ]
    
    print("\n" + "=" * 80)
    print("第一阶段：测试实时行情 (Quote)")
    print("=" * 80)
    
    success_cases = []
    
    for test in test_cases:
        result = await test_indices_quote(test['region'], test['code'], test['name'])
        if result:
            success_cases.append(test)
        await asyncio.sleep(2)  # 避免速率限制
    
    print("\n" + "=" * 80)
    print("第二阶段：测试成功案例的K线数据")
    print("=" * 80)
    
    if success_cases:
        for test in success_cases[:3]:  # 只测试前3个成功的
            await test_indices_kline(test['region'], test['code'], test['name'])
            await asyncio.sleep(2)
    else:
        print("⚠️  没有成功的案例，跳过K线测试")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)
    
    if success_cases:
        print(f"\n✨ 成功的指数配置 ({len(success_cases)} 个):")
        for test in success_cases:
            print(f"   - {test['name']}: region='{test['region']}', code='{test['code']}'")
    else:
        print("\n⚠️  没有找到成功的配置")


if __name__ == "__main__":
    asyncio.run(main())
