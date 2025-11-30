#!/usr/bin/env python3
"""
演示脚本：查询腾讯控股(00700.HK)实时报价
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tools.stock_quote import StockQuoteTool


async def query_tencent():
    """查询腾讯控股实时报价"""
    
    print("=" * 60)
    print("📈 查询腾讯控股(00700.HK)实时报价")
    print("=" * 60)
    
    # 准备查询参数
    arguments = {
        "region": "HK",  # 香港市场
        "code": "700"    # 腾讯控股代码（去掉前导零和后缀）
    }
    
    # 检查 API Key
    api_key = os.getenv("ITICK_API_KEY")
    if not api_key:
        print("\n⚠️  警告: 未设置 ITICK_API_KEY 环境变量")
        print("\n请按以下步骤操作：")
        print("1. 访问 https://itick.org/ 注册账号")
        print("2. 在 Dashboard 获取 API Key")
        print("3. 设置环境变量: export ITICK_API_KEY='your_api_key'")
        print("4. 或创建 .env 文件添加: ITICK_API_KEY=your_api_key")
        print("\n" + "=" * 60)
        return
    
    print(f"\n✅ API Key 已配置: {api_key[:10]}...")
    print(f"\n🔍 查询参数:")
    print(f"   市场代码: {arguments['region']}")
    print(f"   股票代码: {arguments['code']}")
    print("\n⏳ 正在查询...\n")
    
    # 调用工具
    try:
        result = await StockQuoteTool.run(arguments, api_key)
        
        if result.get("isError"):
            print("❌ 查询失败:")
            print(result["content"][0]["text"])
        else:
            print(result["content"][0]["text"])
            
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
    
    print("\n" + "=" * 60)


async def main():
    """主函数"""
    await query_tencent()


if __name__ == "__main__":
    asyncio.run(main())
