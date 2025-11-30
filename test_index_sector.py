"""
测试指数和板块分析工具
"""
import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
os.environ['ITICK_API_KEY'] = os.getenv('ITICK_API_KEY', 'd3de0307d463469697ac2faf27f5f5e02cedbde8e2d1400c9476d45adcf6a859')

from src.tools.index_analysis import IndexAnalysisTool
from src.tools.sector_analysis import SectorAnalysisTool


async def test_index_analysis():
    """测试指数分析工具"""
    print("\n" + "=" * 60)
    print("🧪 测试指数分析工具")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "A股三大指数对比",
            "args": {
                "indices": [
                    {"region": "SH", "code": "000001", "name": "上证指数"},
                    {"region": "SZ", "code": "399001", "name": "深证成指"},
                    {"region": "SZ", "code": "399006", "name": "创业板指"}
                ],
                "period": "day",
                "days": 30,
                "compare": True
            }
        },
        {
            "name": "沪深300 vs 中证500",
            "args": {
                "indices": [
                    {"region": "SH", "code": "000300", "name": "沪深300"},
                    {"region": "SH", "code": "000905", "name": "中证500"}
                ],
                "period": "day",
                "days": 20,
                "compare": True
            }
        },
        {
            "name": "恒生指数单独分析",
            "args": {
                "indices": [
                    {"region": "HK", "code": "HSI", "name": "恒生指数"}
                ],
                "period": "day",
                "days": 30,
                "compare": False
            }
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📊 测试 {i}: {test['name']}")
        print("-" * 60)
        
        try:
            result = await IndexAnalysisTool.run(test['args'])
            
            if result.get('isError'):
                print(f"❌ 测试失败:")
                print(result['content'][0]['text'])
            else:
                print(f"✅ 测试成功:")
                text = result['content'][0]['text']
                # 只显示前800字符
                if len(text) > 800:
                    print(text[:800] + "\n...(省略剩余内容)")
                else:
                    print(text)
                    
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
        
        print()


async def test_sector_analysis():
    """测试板块分析工具"""
    print("\n" + "=" * 60)
    print("🧪 测试板块分析工具")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "白酒板块分析",
            "args": {
                "stocks": [
                    {"region": "SH", "code": "600519", "name": "贵州茅台", "sector": "白酒"},
                    {"region": "SZ", "code": "000858", "name": "五粮液", "sector": "白酒"},
                    {"region": "SZ", "code": "000568", "name": "泸州老窖", "sector": "白酒"},
                    {"region": "SH", "code": "603589", "name": "口子窖", "sector": "白酒"}
                ],
                "period": "day",
                "days": 10
            }
        },
        {
            "name": "科技 vs 金融板块",
            "args": {
                "stocks": [
                    # 科技
                    {"region": "HK", "code": "700", "name": "腾讯控股", "sector": "科技"},
                    {"region": "HK", "code": "9988", "name": "阿里巴巴", "sector": "科技"},
                    {"region": "HK", "code": "1810", "name": "小米集团", "sector": "科技"},
                    # 金融
                    {"region": "SH", "code": "601398", "name": "工商银行", "sector": "金融"},
                    {"region": "SH", "code": "601288", "name": "农业银行", "sector": "金融"},
                    {"region": "SH", "code": "601318", "name": "中国平安", "sector": "金融"}
                ],
                "period": "day",
                "days": 10
            }
        },
        {
            "name": "新能源汽车板块",
            "args": {
                "stocks": [
                    {"region": "SZ", "code": "002594", "name": "比亚迪", "sector": "新能源车"},
                    {"region": "SH", "code": "600104", "name": "上汽集团", "sector": "新能源车"},
                    {"region": "SZ", "code": "300750", "name": "宁德时代", "sector": "新能源车"}
                ],
                "period": "day",
                "days": 10
            }
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📊 测试 {i}: {test['name']}")
        print("-" * 60)
        
        try:
            result = await SectorAnalysisTool.run(test['args'])
            
            if result.get('isError'):
                print(f"❌ 测试失败:")
                print(result['content'][0]['text'])
            else:
                print(f"✅ 测试成功:")
                text = result['content'][0]['text']
                # 只显示前800字符
                if len(text) > 800:
                    print(text[:800] + "\n...(省略剩余内容)")
                else:
                    print(text)
                    
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
        
        print()


async def main():
    """主测试函数"""
    print("\n🚀 开始测试指数和板块分析工具...")
    
    # 测试指数分析
    await test_index_analysis()
    
    # 等待一下
    await asyncio.sleep(1)
    
    # 测试板块分析
    await test_sector_analysis()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
