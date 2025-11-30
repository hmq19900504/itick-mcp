#!/usr/bin/env python3
"""
测试 iTick API 的 kType 参数映射关系
"""
import requests
import json

API_KEY = "d3de0307d463469697ac2faf27f5f5e02cedbde8e2d1400c9476d45adcf6a859"
BASE_URL = "https://api.itick.org/stock/kline"

def test_ktype(region, code, ktype, ktype_name):
    """测试特定的 kType 值"""
    params = {
        "region": region,
        "code": code,
        "kType": ktype,
        "limit": 3  # 只获取3条数据
    }
    
    headers = {
        "accept": "application/json",
        "token": API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if data.get("code") == 0:
            klines = data.get("data", [])
            count = len(klines)
            if count > 0:
                first_k = klines[0]
                return True, count, first_k
            else:
                return True, 0, None
        else:
            return False, data.get("msg", "未知错误"), None
            
    except Exception as e:
        return False, str(e), None


def main():
    """测试所有可能的 kType 值"""
    
    print("=" * 100)
    print("🔍 测试 iTick API kType 参数映射")
    print("=" * 100)
    print(f"\n测试股票: 腾讯控股 (00700.HK)")
    print(f"API Key: {API_KEY[:20]}...\n")
    
    # 测试 kType 1-15
    print(f"{'kType':^8} | {'周期猜测':^15} | {'状态':^8} | {'数据条数':^10} | {'时间戳示例':^20}")
    print("-" * 100)
    
    ktype_guesses = {
        1: "1分钟",
        2: "日线",
        3: "周线",
        4: "月线",
        5: "5分钟",
        6: "15分钟",
        7: "30分钟",
        8: "60分钟",
        9: "未知",
        10: "未知",
        11: "未知",
        12: "未知",
        13: "未知",
        14: "未知",
        15: "未知",
    }
    
    results = {}
    
    for ktype in range(1, 16):
        guess = ktype_guesses.get(ktype, "未知")
        success, data_or_error, first_k = test_ktype("HK", "700", ktype, guess)
        
        if success:
            if isinstance(data_or_error, int):
                count = data_or_error
                if count > 0 and first_k:
                    from datetime import datetime
                    ts = first_k.get('t', 0)
                    dt = datetime.fromtimestamp(ts/1000) if ts else None
                    time_str = dt.strftime('%Y-%m-%d %H:%M') if dt else "N/A"
                    status = "✅ 成功"
                    results[ktype] = {"name": guess, "count": count, "sample": first_k}
                else:
                    time_str = "无数据"
                    status = "⚠️ 无数据"
                    
                print(f"{ktype:^8} | {guess:^15} | {status:^10} | {count:^10} | {time_str:^20}")
        else:
            error_msg = str(data_or_error)[:30]
            print(f"{ktype:^8} | {guess:^15} | {'❌ 失败':^10} | {'-':^10} | {error_msg:^20}")
    
    print("-" * 100)
    
    # 详细输出成功的 kType
    print("\n" + "=" * 100)
    print("📊 成功的 kType 详细信息")
    print("=" * 100)
    
    for ktype, info in results.items():
        print(f"\n【kType = {ktype}】 {info['name']}")
        print(f"  数据条数: {info['count']}")
        print(f"  示例数据:")
        print(f"    {json.dumps(info['sample'], indent=4, ensure_ascii=False)}")
    
    print("\n" + "=" * 100)


if __name__ == "__main__":
    main()
