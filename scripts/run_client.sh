#!/bin/bash
# 启动银行客户端

# 默认参数
SERVER_HOST=${1:-"localhost"}
SERVER_PORT=${2:-5000}
SEMANTICS=${3:-"at-most-once"}
LOSS_RATE=${4:-0.0}

echo "Starting Banking Client..."
echo "Server: $SERVER_HOST:$SERVER_PORT"
echo "Semantics: $SEMANTICS"
echo "Loss Rate: $LOSS_RATE"
echo ""

python -m src.client.client \
  --server-host "$SERVER_HOST" \
  --server-port "$SERVER_PORT" \
  --semantics "$SEMANTICS" \
  --loss-rate "$LOSS_RATE"
