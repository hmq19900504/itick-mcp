#!/usr/bin/env python3
"""
MCP 协议集成测试
测试 MCP 服务的 initialize、tools/list、tools/call 等端点
"""
import requests
import json

BASE_URL = "http://localhost:3000"
API_KEY = "d3de0307d463469697ac2faf27f5f5e02cedbde8e2d1400c9476d45adcf6a859"

def test_health():
    """测试健康检查"""
    print("=" * 80)
    print("测试 1: 健康检查 /health")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    return response.status_code == 200


def test_initialize():
    """测试 MCP initialize"""
    print("=" * 80)
    print("测试 2: MCP Initialize")
    print("=" * 80)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        },
        "id": 1
    }
    
    response = requests.post(f"{BASE_URL}/mcp", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    return response.status_code == 200


def test_tools_list():
    """测试 tools/list"""
    print("=" * 80)
    print("测试 3: Tools List")
    print("=" * 80)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }
    
    response = requests.post(f"{BASE_URL}/mcp", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if 'result' in data and 'tools' in data['result']:
        tools = data['result']['tools']
        print(f"总工具数: {len(tools)}\n")
        
        for tool in tools:
            print(f"工具: {tool['name']}")
            print(f"  描述: {tool['description'][:100]}...")
            print(f"  必需参数: {tool['inputSchema'].get('required', [])}")
            print()
    else:
        print(f"Response: {json.dumps(data, indent=2)}")
    
    return response.status_code == 200


def test_tool_call_timestamp():
    """测试调用 timestamp 工具"""
    print("=" * 80)
    print("测试 4: 调用 timestamp 工具")
    print("=" * 80)
    
    payload = {
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
    
    headers = {
        "X-Itick-Token": API_KEY
    }
    
    response = requests.post(f"{BASE_URL}/mcp", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if 'result' in data:
        print("Result:")
        print(data['result']['content'][0]['text'][:300])
    else:
        print(f"Response: {json.dumps(data, indent=2)}")
    print()
    
    return response.status_code == 200


def test_tool_call_quote():
    """测试调用 quote 工具"""
    print("=" * 80)
    print("测试 5: 调用 stock_quote 工具")
    print("=" * 80)
    
    payload = {
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
    
    headers = {
        "X-Itick-Token": API_KEY
    }
    
    response = requests.post(f"{BASE_URL}/mcp", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if 'result' in data:
        print("Result:")
        print(data['result']['content'][0]['text'][:500])
    else:
        print(f"Response: {json.dumps(data, indent=2)}")
    print()
    
    return response.status_code == 200


def test_tool_call_kline():
    """测试调用 kline 工具"""
    print("=" * 80)
    print("测试 6: 调用 stock_kline 工具")
    print("=" * 80)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "itick_stock_kline",
            "arguments": {
                "region": "HK",
                "code": "700",
                "start_date": "20251101",
                "end_date": "20251130",
                "period": "day"
            }
        },
        "id": 5
    }
    
    headers = {
        "X-Itick-Token": API_KEY
    }
    
    response = requests.post(f"{BASE_URL}/mcp", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if 'result' in data:
        print("Result:")
        print(data['result']['content'][0]['text'][:500])
    else:
        print(f"Response: {json.dumps(data, indent=2)}")
    print()
    
    return response.status_code == 200


def main():
    """运行所有测试"""
    print("\n🧪" * 40)
    print(" " * 30 + "MCP 协议集成测试")
    print("🧪" * 40 + "\n")
    
    results = {}
    
    results['health'] = test_health()
    results['initialize'] = test_initialize()
    results['tools_list'] = test_tools_list()
    results['timestamp'] = test_tool_call_timestamp()
    results['quote'] = test_tool_call_quote()
    results['kline'] = test_tool_call_kline()
    
    # 总结
    print("=" * 80)
    print("测试总结")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    print(f"通过率: {passed/total*100:.1f}%\n")
    
    for test_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {test_name}")
    
    print("\n" + "=" * 80)
    
    if passed == total:
        print("\n🎉 所有MCP协议测试通过！服务正常运行。\n")
    else:
        print(f"\n⚠️ 有 {total - passed} 项测试失败。\n")


if __name__ == "__main__":
    main()
