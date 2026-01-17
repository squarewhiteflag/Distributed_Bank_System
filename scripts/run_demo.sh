#!/bin/bash
# 演示脚本：展示基本功能

echo "================================"
echo "分布式银行系统演示"
echo "================================"
echo ""

# 检查Python是否可用
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python"
    exit 1
fi

echo "1. 运行编解码测试..."
python -m unittest tests.test_marshaller 2>&1 | head -20
echo ""

echo "2. 运行账户管理测试..."
python -m unittest tests.test_account_manager 2>&1 | head -20
echo ""

echo "================================"
echo "测试完成！"
echo "================================"
echo ""
echo "接下来可以："
echo "1. 在一个终端启动服务器:"
echo "   ./scripts/run_server.sh"
echo ""
echo "2. 在另一个终端启动客户端:"
echo "   ./scripts/run_client.sh localhost"
echo ""
echo "3. 或使用Python直接运行:"
echo "   python -m src.server.server --help"
echo "   python -m src.client.client --help"
