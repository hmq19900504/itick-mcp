#!/usr/bin/env python3
"""
完整的 MCP 工具测试套件
测试所有5个工具的功能和 MCP 协议合规性
"""
import asyncio
import sys
import os
import json
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tools.stock_quote import StockQuoteTool
from src.tools.stock_kline import StockKlineTool
from src.tools.stock_tick import StockTickTool
from src.tools.stock_depth import StockDepthTool
from src.tools.timestamp import TimestampTool

# API Key
API_KEY = "d3de0307d463469697ac2faf27f5f5e02cedbde8e2d1400c9476d45adcf6a859"


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100 + "\n")


def print_result(tool_name, success, message=""):
    """打印测试结果"""
    status = "✅ 成功" if success else "❌ 失败"
    print(f"{status} - {tool_name}")
    if message:
        print(f"   {message}")


async def test_timestamp_tool():
    """测试时间戳工具"""
    print_section("测试 1/5: 时间戳工具 (current_timestamp)")
    
    try:
        # 测试不同格式
        formats = ["datetime", "date", "time", "timestamp", "readable"]
        
        for fmt in formats:
            result = await TimestampTool.run({"format": fmt}, API_KEY)
            
            if result.get("isError"):
                print_result(f"格式: {fmt}", False, result["content"][0]["text"])
            else:
                print_result(f"格式: {fmt}", True)
                print(f"   {result['content'][0]['text'][:150]}...")
        
        return True
    except Exception as e:
        print_result("时间戳工具", False, str(e))
        return False


async def test_stock_quote_tool():
    """测试股票报价工具"""
    print_section("测试 2/5: 股票实时报价 (itick_stock_quote)")
    
    test_cases = [
        {"region": "HK", "code": "700", "name": "腾讯控股"},
        {"region": "US", "code": "AAPL", "name": "苹果公司"},
        {"region": "SH", "code": "600519", "name": "贵州茅台"},
    ]
    
    results = []
    for case in test_cases:
        try:
            print(f"\n测试: {case['name']} ({case['code']}.{case['region']})")
            result = await StockQuoteTool.run({
                "region": case["region"],
                "code": case["code"]
            }, API_KEY)
            
            if result.get("isError"):
                print_result(case['name'], False, result["content"][0]["text"][:100])
                results.append(False)
            else:
                print_result(case['name'], True)
                # 打印部分结果
                lines = result['content'][0]['text'].split('\n')
                for line in lines[:10]:  # 只显示前10行
                    print(f"   {line}")
                results.append(True)
                
        except Exception as e:
            print_result(case['name'], False, str(e))
            results.append(False)
    
    return all(results)


async def test_stock_kline_tool():
    """测试K线工具"""
    print_section("测试 3/5: 股票K线数据 (itick_stock_kline)")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    test_cases = [
        {
            "region": "HK",
            "code": "700",
            "period": "day",
            "name": "腾讯-日线"
        },
        {
            "region": "US",
            "code": "AAPL",
            "period": "week",
            "name": "苹果-周线"
        },
    ]
    
    results = []
    for case in test_cases:
        try:
            print(f"\n测试: {case['name']}")
            result = await StockKlineTool.run({
                "region": case["region"],
                "code": case["code"],
                "start_date": start_date.strftime("%Y%m%d"),
                "end_date": end_date.strftime("%Y%m%d"),
                "period": case["period"]
            }, API_KEY)
            
            if result.get("isError"):
                print_result(case['name'], False, result["content"][0]["text"][:100])
                results.append(False)
            else:
                print_result(case['name'], True)
                # 打印部分结果
                lines = result['content'][0]['text'].split('\n')
                for line in lines[:15]:  # 只显示前15行
                    print(f"   {line}")
                results.append(True)
                
        except Exception as e:
            print_result(case['name'], False, str(e))
            results.append(False)
    
    return all(results)


async def test_stock_tick_tool():
    """测试Tick数据工具"""
    print_section("测试 4/5: 股票Tick数据 (itick_stock_tick)")
    
    test_cases = [
        {"region": "HK", "code": "700", "name": "腾讯控股"},
        {"region": "SZ", "code": "300750", "name": "宁德时代"},
    ]
    
    results = []
    for case in test_cases:
        try:
            print(f"\n测试: {case['name']}")
            result = await StockTickTool.run({
                "region": case["region"],
                "code": case["code"]
            }, API_KEY)
            
            if result.get("isError"):
                print_result(case['name'], False, result["content"][0]["text"][:100])
                results.append(False)
            else:
                print_result(case['name'], True)
                lines = result['content'][0]['text'].split('\n')
                for line in lines[:12]:
                    print(f"   {line}")
                results.append(True)
                
        except Exception as e:
            print_result(case['name'], False, str(e))
            results.append(False)
    
    return all(results)


async def test_stock_depth_tool():
    """测试盘口深度工具"""
    print_section("测试 5/5: 股票盘口深度 (itick_stock_depth)")
    
    test_cases = [
        {"region": "HK", "code": "700", "name": "腾讯控股"},
    ]
    
    results = []
    for case in test_cases:
        try:
            print(f"\n测试: {case['name']}")
            result = await StockDepthTool.run({
                "region": case["region"],
                "code": case["code"]
            }, API_KEY)
            
            if result.get("isError"):
                print_result(case['name'], False, result["content"][0]["text"][:100])
                results.append(False)
            else:
                print_result(case['name'], True)
                lines = result['content'][0]['text'].split('\n')
                for line in lines[:12]:
                    print(f"   {line}")
                results.append(True)
                
        except Exception as e:
            print_result(case['name'], False, str(e))
            results.append(False)
    
    return all(results)


async def test_mcp_compliance():
    """测试 MCP 协议合规性"""
    print_section("MCP 协议合规性检查")
    
    tools = [
        StockQuoteTool,
        StockKlineTool,
        StockTickTool,
        StockDepthTool,
        TimestampTool
    ]
    
    all_valid = True
    
    for tool in tools:
        print(f"\n检查工具: {tool.name}")
        
        # 检查必需属性
        has_name = hasattr(tool, 'name')
        has_description = hasattr(tool, 'description')
        has_parameters = hasattr(tool, 'parameters')
        has_run = hasattr(tool, 'run')
        
        print(f"   name: {'✅' if has_name else '❌'}")
        print(f"   description: {'✅' if has_description else '❌'}")
        print(f"   parameters: {'✅' if has_parameters else '❌'}")
        print(f"   run method: {'✅' if has_run else '❌'}")
        
        # 检查 parameters 结构
        if has_parameters:
            params = tool.parameters
            has_type = 'type' in params
            has_properties = 'properties' in params
            has_required = 'required' in params
            
            print(f"   parameters.type: {'✅' if has_type else '❌'}")
            print(f"   parameters.properties: {'✅' if has_properties else '❌'}")
            print(f"   parameters.required: {'✅' if has_required else '❌'}")
            
            if not (has_type and has_properties and has_required):
                all_valid = False
        
        # 检查 description 长度
        if has_description:
            desc_len = len(tool.description)
            print(f"   description length: {desc_len} chars ({'✅' if desc_len > 50 else '⚠️  较短'})")
        
        if not all([has_name, has_description, has_parameters, has_run]):
            all_valid = False
    
    return all_valid


async def main():
    """主测试函数"""
    print("\n" + "🚀" * 50)
    print(" " * 20 + "iTick MCP 工具完整测试套件")
    print("🚀" * 50)
    print(f"\nAPI Key: {API_KEY[:20]}...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {}
    
    # 1. MCP 协议合规性
    results['mcp_compliance'] = await test_mcp_compliance()
    
    # 2. 时间戳工具
    results['timestamp'] = await test_timestamp_tool()
    
    # 3. 股票报价
    results['quote'] = await test_stock_quote_tool()
    
    # 4. K线数据
    results['kline'] = await test_stock_kline_tool()
    
    # 5. Tick数据
    results['tick'] = await test_stock_tick_tool()
    
    # 6. 盘口深度
    results['depth'] = await test_stock_depth_tool()
    
    # 总结
    print_section("测试总结")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"测试项目总数: {total}")
    print(f"通过: {passed} ({'✅' if passed == total else '⚠️'})")
    print(f"失败: {total - passed}")
    print(f"通过率: {passed/total*100:.1f}%\n")
    
    for test_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {status} - {test_name}")
    
    print("\n" + "=" * 100)
    
    if passed == total:
        print("\n🎉 所有测试通过！项目已准备就绪。")
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败，请检查错误信息。")
    
    print("\n" + "=" * 100 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
