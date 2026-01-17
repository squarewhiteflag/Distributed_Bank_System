#!/bin/bash
# 启动银行服务器

# 默认参数
HOST=${1:-"0.0.0.0"}
PORT=${2:-5000}
SEMANTICS=${3:-"at-most-once"}
LOSS_RATE=${4:-0.0}

echo "Starting Banking Server..."
echo "Host: $HOST"
echo "Port: $PORT"
echo "Semantics: $SEMANTICS"
echo "Loss Rate: $LOSS_RATE"
echo ""

python -m src.server.server \
  --host "$HOST" \
  --port "$PORT" \
  --semantics "$SEMANTICS" \
  --loss-rate "$LOSS_RATE" \
  --verbose
