"""
基于发现，测试更多指数的可能配置
已知：标普500 = region:'GB', code:'SPX'
"""
import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('ITICK_API_KEY')
BASE_URL = "https://api.itick.org"


async def quick_test_index(region: str, code: str, name: str):
    """快速测试一个指数配置"""
    url = f"{BASE_URL}/indices/quote"
    headers = {"accept": "application/json", "token": API_KEY}
    params = {"region": region, "code": code}
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0 and data.get('data'):
                    result = data['data']
                    print(f"✅ {name:20s} region='{region:3s}' code='{code:10s}' 价格={result.get('ld')}")
                    return True
    except:
        pass
    
    return False


async def main():
    """测试各种可能的组合"""
    print("=" * 80)
    print("🔍 快速扫描指数配置")
    print("=" * 80)
    
    # 基于标普500成功案例，尝试其他指数
    # 猜测：可能所有美股指数都用 GB？或者有其他规律？
    
    test_configs = [
        # 美股指数 - 尝试不同region
        ("GB", "SPX", "标普500"),
        ("GB", "DJI", "道琼斯(GB)"),
        ("GB", "IXIC", "纳斯达克(GB)"),
        ("GB", "NDX", "纳斯达克100(GB)"),
        
        ("US", "DJI", "道琼斯(US)"),
        ("US", "NDX", "纳斯达克100(US)"),
        
        # 港股指数 - 尝试不同region
        ("HK", "HSI", "恒生指数(HK)"),
        ("HK", "HSCEI", "恒生国企(HK)"),
        ("HK", "HSTECH", "恒生科技(HK)"),
        
        ("GB", "HSI", "恒生指数(GB)"),
        ("GB", "HSCEI", "恒生国企(GB)"),
        ("GB", "HSTECH", "恒生科技(GB)"),
        
        # A股指数 - 尝试不同region
        ("CN", "000001", "上证指数(CN)"),
        ("CN", "399006", "创业板指(CN)"),
        ("SH", "000001", "上证指数(SH)"),
        ("SZ", "399006", "创业板指(SZ)"),
        
        ("GB", "000001", "上证指数(GB)"),
        ("GB", "399006", "创业板指(GB)"),
        
        # 可能的其他代码格式
        ("GB", "SSEC", "上证指数(SSEC)"),
        ("GB", "SZSC", "深证成指(SZSC)"),
        ("GB", "CSI300", "沪深300"),
        ("GB", "CSI500", "中证500"),
    ]
    
    success_count = 0
    
    for region, code, name in test_configs:
        result = await quick_test_index(region, code, name)
        if result:
            success_count += 1
        await asyncio.sleep(1)  # 避免速率限制
    
    print("\n" + "=" * 80)
    print(f"✅ 找到 {success_count} 个有效配置")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
