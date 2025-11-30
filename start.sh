#!/bin/bash

# iTick MCP Server 启动脚本

echo "=================================="
echo "🚀 iTick MCP Server"
echo "=================================="

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，正在创建..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请编辑填入您的 iTick API Key"
    echo ""
    echo "请执行以下步骤："
    echo "1. 编辑 .env 文件"
    echo "2. 填入 ITICK_API_KEY=your_api_key_here"
    echo "3. 重新运行此脚本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -q -r requirements.txt

# 启动服务
echo "🌟 启动服务..."
echo ""
python -m uvicorn src.server:app --reload --port 3000
