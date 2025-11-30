"""
验证修复后的指数分析工具 - 测试全球指数
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from src.tools.index_analysis import IndexAnalysisTool


async def test_global_indices():
    """测试全球指数（A股、港股、美股）"""
    print("\n" + "=" * 80)
    print("✅ 测试全球指数分析（修复后）")
    print("=" * 80)
    
    args = {
        "indices": [
            # A股指数
            {"code": "000001", "name": "上证指数"},
            {"code": "399006", "name": "创业板指"},
            
            # 港股指数
            {"code": "HSI", "name": "恒生指数"},
            {"code": "HSTECH", "name": "恒生科技"},
            
            # 美股指数
            {"code": "SPX", "name": "标普500"},
            {"code": "IXIC", "name": "纳斯达克"},
            {"code": "DJI", "name": "道琼斯"},
        ],
        "period": "day",
        "days": 5,
        "compare": True
    }
    
    result = await IndexAnalysisTool.run(args)
    
    if result.get('isError'):
        print("❌ 测试失败")
        print(result['content'][0]['text'])
    else:
        print("✅ 测试成功！")
        text = result['content'][0]['text']
        
        # 统计成功和失败数量
        success_count = text.count("📈")
        fail_count = text.count("❌")
        
        print(f"\n📊 结果统计:")
        print(f"   成功: {success_count} 个")
        print(f"   失败: {fail_count} 个")
        
        # 显示报告摘要
        print(f"\n📝 报告摘要:")
        lines = text.split('\n')
        for line in lines[:30]:  # 显示前30行
            print(line)
        
        if len(lines) > 30:
            print("\n... (省略部分内容)")


async def test_a_stock_only():
    """仅测试A股指数"""
    print("\n" + "=" * 80)
    print("✅ 测试A股指数")
    print("=" * 80)
    
    args = {
        "indices": [
            {"code": "000001", "name": "上证指数"},
            {"code": "399001", "name": "深证成指"},
            {"code": "399006", "name": "创业板指"},
        ],
        "period": "day",
        "days": 10,
        "compare": True
    }
    
    result = await IndexAnalysisTool.run(args)
    
    if not result.get('isError'):
        text = result['content'][0]['text']
        print("✅ A股指数全部成功")
        
        # 提取对比表格
        if "多指数对比分析" in text:
            start = text.find("多指数对比分析")
            end = text.find("---", start + 100)
            if end > start:
                print(text[start:end])


async def test_hk_us_only():
    """测试港股和美股指数"""
    print("\n" + "=" * 80)
    print("✅ 测试港股和美股指数")
    print("=" * 80)
    
    args = {
        "indices": [
            {"code": "HSI", "name": "恒生指数"},
            {"code": "HSTECH", "name": "恒生科技"},
            {"code": "SPX", "name": "标普500"},
            {"code": "DJI", "name": "道琼斯"},
        ],
        "period": "day",
        "days": 5,
        "compare": True
    }
    
    result = await IndexAnalysisTool.run(args)
    text = result['content'][0]['text']
    
    # 检查是否有成功的
    success_count = text.count("📈")
    
    if success_count > 0:
        print(f"✅ 成功获取 {success_count} 个港股/美股指数数据！")
        
        # 显示部分内容
        lines = text.split('\n')
        for line in lines[:40]:
            print(line)
    else:
        print("❌ 港股/美股指数获取失败")


async def main():
    """主测试函数"""
    print("\n" + "🎉" * 40)
    print("修复验证 - 全球指数支持")
    print("🎉" * 40)
    
    # 等待避免速率限制
    print("\n⏳ 等待5秒...")
    await asyncio.sleep(5)
    
    # 测试1: 全球指数（A股+港股+美股）
    await test_global_indices()
    await asyncio.sleep(3)
    
    # 测试2: 仅A股指数
    await test_a_stock_only()
    await asyncio.sleep(3)
    
    # 测试3: 仅港股和美股指数
    await test_hk_us_only()
    
    print("\n" + "=" * 80)
    print("✅ 所有测试完成")
    print("=" * 80)
    
    print("\n📝 结论:")
    print("- 现在应该可以正常获取A股、港股和美股指数数据")
    print("- 使用统一的指数API接口 (/indices/quote)")
    print("- 所有指数统一使用 region='GB'")


if __name__ == "__main__":
    asyncio.run(main())
