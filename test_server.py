"""
iTick MCP Server 测试脚本
用于验证服务器功能
"""
import asyncio
import httpx
import json


BASE_URL = "http://localhost:3000"


async def test_health():
    """测试健康检查端点"""
    print("🔍 测试健康检查...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"✅ 健康检查: {response.json()}")
        print()


async def test_mcp_initialize():
    """测试 MCP initialize"""
    print("🔍 测试 MCP initialize...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "initialize",
                "id": 1
            }
        )
        data = response.json()
        print(f"✅ Initialize: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print()


async def test_tools_list():
    """测试工具列表"""
    print("🔍 测试工具列表...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 2
            }
        )
        data = response.json()
        tools = data.get("result", {}).get("tools", [])
        print(f"✅ 可用工具数量: {len(tools)}")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description'][:50]}...")
        print()


async def test_current_timestamp():
    """测试时间戳工具"""
    print("🔍 测试时间戳工具...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "current_timestamp",
                    "arguments": {
                        "format": "datetime"
                    }
                },
                "id": 3
            }
        )
        data = response.json()
        if "result" in data:
            content = data["result"]["content"][0]["text"]
            print(f"✅ 时间戳工具:")
            print(content)
        else:
            print(f"❌ 错误: {data}")
        print()


async def test_stock_quote():
    """测试股票报价工具（需要有效的 API Key）"""
    print("🔍 测试股票报价工具...")
    print("⚠️  此测试需要有效的 iTick API Key")
    
    api_key = input("请输入您的 iTick API Key (或直接回车跳过): ").strip()
    if not api_key:
        print("⏭️  跳过股票报价测试")
        print()
        return
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/mcp",
            headers={"X-Itick-Token": api_key},
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "itick_stock_quote",
                    "arguments": {
                        "region": "HK",
                        "code": "700"
                    }
                },
                "id": 4
            }
        )
        data = response.json()
        if "result" in data:
            content = data["result"]["content"][0]["text"]
            print(f"✅ 股票报价 (腾讯控股 00700.HK):")
            print(content)
        else:
            error = data.get("error", {})
            print(f"❌ 错误: {error.get('message', 'Unknown')}")
        print()


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 iTick MCP Server 测试套件")
    print("=" * 60)
    print()
    
    try:
        await test_health()
        await test_mcp_initialize()
        await test_tools_list()
        await test_current_timestamp()
        await test_stock_quote()
        
        print("=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        print()
        print("请确认：")
        print("1. 服务器是否正在运行 (运行 ./start.sh 或 uvicorn src.server:app)")
        print("2. 服务器端口是否为 3000")
        print("3. .env 文件是否配置正确")


if __name__ == "__main__":
    asyncio.run(main())
