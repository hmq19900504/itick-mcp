"""
验证修复后的指数分析工具
测试A股指数（应该成功）和港股/美股指数（应该优雅失败）
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from src.tools.index_analysis import IndexAnalysisTool


async def test_a_stock_indices():
    """测试A股指数 - 应该成功"""
    print("\n" + "=" * 80)
    print("✅ 测试 A股指数（预期成功）")
    print("=" * 80)
    
    args = {
        "indices": [
            {"region": "SH", "code": "000001", "name": "上证指数"},
            {"region": "SZ", "code": "399006", "name": "创业板指"}
        ],
        "period": "day",
        "days": 5,
        "compare": True
    }
    
    result = await IndexAnalysisTool.run(args)
    
    if result.get('isError'):
        print("❌ 测试失败（不应该失败）")
        print(result['content'][0]['text'])
    else:
        print("✅ 测试成功")
        # 只显示前500字符
        text = result['content'][0]['text']
        print(text[:500] + "...\n")


async def test_foreign_indices():
    """测试港股/美股指数 - 应该优雅失败"""
    print("\n" + "=" * 80)
    print("⚠️  测试 港股/美股指数（预期失败，但不崩溃）")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "港股指数",
            "indices": [{"region": "HK", "code": "HSI", "name": "恒生指数"}]
        },
        {
            "name": "美股指数", 
            "indices": [{"region": "US", "code": "IXIC", "name": "纳斯达克"}]
        }
    ]
    
    for test in test_cases:
        print(f"\n📊 测试: {test['name']}")
        print("-" * 80)
        
        args = {
            "indices": test['indices'],
            "period": "day",
            "days": 5
        }
        
        result = await IndexAnalysisTool.run(args)
        
        # 检查错误消息
        text = result['content'][0]['text']
        
        # 旧的错误: 'NoneType' object has no attribute 'get'
        # 新的错误: API返回空数据，可能是指数代码不正确或未订阅该市场
        
        if "'NoneType'" in text:
            print("❌ 仍然有 NoneType 错误（修复未生效）")
            print(text[:200])
        elif "API返回空数据" in text or "获取失败" in text:
            print("✅ 错误处理正常（优雅失败）")
            print("   错误提示:", text[text.find("错误:"):text.find("错误:")+100])
        else:
            print("⚠️  意外结果:")
            print(text[:200])
        
        await asyncio.sleep(2)  # 避免速率限制


async def test_mixed_indices():
    """测试混合指数 - A股和港股一起"""
    print("\n" + "=" * 80)  
    print("🔀 测试混合指数（A股+港股，部分成功）")
    print("=" * 80)
    
    args = {
        "indices": [
            {"region": "SH", "code": "000001", "name": "上证指数"},  # 应该成功
            {"region": "HK", "code": "HSI", "name": "恒生指数"},     # 应该失败
            {"region": "SZ", "code": "399006", "name": "创业板指"}   # 应该成功
        ],
        "period": "day",
        "days": 5,
        "compare": True
    }
    
    result = await IndexAnalysisTool.run(args)
    text = result['content'][0]['text']
    
    # 统计成功和失败数量
    success_count = text.count("✅")
    fail_count = text.count("❌")
    
    print(f"结果统计: {success_count} 个成功, {fail_count} 个失败")
    print("\n部分输出:")
    print(text[:600] + "...\n")


async def main():
    """主测试函数"""
    print("\n" + "🚀" * 40)
    print("修复验证测试 - 指数分析工具")
    print("🚀" * 40)
    
    # 等待一下，避免之前的速率限制
    print("\n⏳ 等待5秒以避免API速率限制...")
    await asyncio.sleep(5)
    
    # 测试1: A股指数（应该完全成功）
    await test_a_stock_indices()
    await asyncio.sleep(3)
    
    # 测试2: 港股/美股指数（应该优雅失败）
    await test_foreign_indices()
    await asyncio.sleep(3)
    
    # 测试3: 混合指数（部分成功）
    await test_mixed_indices()
    
    print("\n" + "=" * 80)
    print("✅ 所有测试完成")
    print("=" * 80)
    
    print("\n📝 结论:")
    print("- A股指数应该能正常工作")
    print("- 港股/美股指数应该显示友好的错误提示，而不是崩溃")
    print("- 错误消息应该是'API返回空数据'，而不是'NoneType'错误")


if __name__ == "__main__":
    asyncio.run(main())
