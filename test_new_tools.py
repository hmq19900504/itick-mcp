"""
测试新增工具：技术指标和资金流向
"""
import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置环境变量
os.environ['ITICK_API_KEY'] = os.getenv('ITICK_API_KEY', 'd3de0307d463469697ac2faf27f5f5e02cedbde8e2d1400c9476d45adcf6a859')

from src.tools.technical_indicators import TechnicalIndicatorsTool
from src.tools.money_flow import MoneyFlowTool


async def test_technical_indicators():
    """测试技术指标工具"""
    print("\n" + "=" * 60)
    print("🧪 测试技术指标工具")
    print("=" * 60)
    
    # 测试案例
    test_cases = [
        {
            "name": "腾讯控股 - MACD+RSI",
            "args": {
                "region": "HK",
                "code": "700",
                "indicators": ["macd", "rsi"],
                "period": "day",
                "limit": 200
            }
        },
        {
            "name": "贵州茅台 - 全部指标",
            "args": {
                "region": "SH",
                "code": "600519",
                "indicators": ["all"],
                "period": "day",
                "limit": 200
            }
        },
        {
            "name": "苹果 - KDJ+BOLL",
            "args": {
                "region": "US",
                "code": "AAPL",
                "indicators": ["kdj", "boll", "ma"],
                "period": "day",
                "limit": 150
            }
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📊 测试 {i}: {test['name']}")
        print("-" * 60)
        
        try:
            result = await TechnicalIndicatorsTool.run(test['args'])
            
            if result.get('isError'):
                print(f"❌ 测试失败:")
                print(result['content'][0]['text'])
            else:
                print(f"✅ 测试成功:")
                # 只显示前500字符
                text = result['content'][0]['text']
                if len(text) > 500:
                    print(text[:500] + "\n...(省略剩余内容)")
                else:
                    print(text)
                    
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
        
        print()


async def test_money_flow():
    """测试资金流向工具"""
    print("\n" + "=" * 60)
    print("💰 测试资金流向工具")
    print("=" * 60)
    
    # 测试案例
    test_cases = [
        {
            "name": "腾讯控股 - 近10日资金流向",
            "args": {
                "region": "HK",
                "code": "700",
                "period": "day",
                "days": 10
            }
        },
        {
            "name": "贵州茅台 - 近20日资金流向",
            "args": {
                "region": "SH",
                "code": "600519",
                "period": "day",
                "days": 20
            }
        },
        {
            "name": "苹果 - 近5日资金流向",
            "args": {
                "region": "US",
                "code": "AAPL",
                "period": "day",
                "days": 5
            }
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n💵 测试 {i}: {test['name']}")
        print("-" * 60)
        
        try:
            result = await MoneyFlowTool.run(test['args'])
            
            if result.get('isError'):
                print(f"❌ 测试失败:")
                print(result['content'][0]['text'])
            else:
                print(f"✅ 测试成功:")
                # 只显示前500字符
                text = result['content'][0]['text']
                if len(text) > 500:
                    print(text[:500] + "\n...(省略剩余内容)")
                else:
                    print(text)
                    
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
        
        print()


async def main():
    """主测试函数"""
    print("\n🚀 开始测试新增工具...")
    
    # 测试技术指标
    await test_technical_indicators()
    
    # 等待一下
    await asyncio.sleep(1)
    
    # 测试资金流向
    await test_money_flow()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
