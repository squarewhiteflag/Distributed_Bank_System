# 分布式银行系统 - 快速命令参考

## 🧪 测试命令

```bash
# 运行所有测试
python -m unittest discover tests/

# 运行特定测试
python -m unittest tests.test_marshaller
python -m unittest tests.test_account_manager

# 详细输出
python -m unittest discover tests/ -v
```

## 🚀 启动命令

### 服务器

```bash
# 默认配置
python -m src.server.server

# 自定义配置
python -m src.server.server --host 0.0.0.0 --port 5000 \
  --semantics at-most-once --loss-rate 0.2 --verbose

# 使用脚本
./scripts/run_server.sh
./scripts/run_server.sh 0.0.0.0 5000 at-most-once 0.2
```

### 客户端

```bash
# 本地服务器
python -m src.client.client --server-host localhost

# 远程服务器
python -m src.client.client --server-host 192.168.1.100 --server-port 5000

# 使用脚本
./scripts/run_client.sh localhost
./scripts/run_client.sh 192.168.1.100 5000 at-most-once 0.1
```

## 🧬 实验命令

### 实验1：至少一次语义

```bash
# 终端1 - 服务器
python -m src.server.server --port 5000 \
  --semantics at-least-once --loss-rate 0.3 --verbose

# 终端2 - 客户端
python -m src.client.client --server-host localhost \
  --semantics at-least-once --loss-rate 0.2
```

**观察**: 转账操作可能重复执行

### 实验2：至多一次语义

```bash
# 终端1 - 服务器
python -m src.server.server --port 5000 \
  --semantics at-most-once --loss-rate 0.3 --verbose

# 终端2 - 客户端
python -m src.client.client --server-host localhost \
  --semantics at-most-once --loss-rate 0.2
```

**观察**: 所有操作只执行一次

## 📺 监控演示

```bash
# 终端1 - 服务器
python -m src.server.server --port 5000

# 终端2 - 监控客户端
python -m src.client.client --server-host localhost
# 选择: 7. Monitor Account Updates (60秒)

# 终端3 - 操作客户端
python -m src.client.client --server-host localhost
# 执行: 开户、存款、取款等操作
# 观察终端2实时显示更新通知
```

## 📋 功能快速测试

### 开户流程
```
1. Open Account
   Name: Alice
   Password: test1234
   Currency: 1 (USD)
   Balance: 1000.0
   → Account Number: 10001
```

### 存款流程
```
3. Deposit
   Name: Alice
   Account: 10001
   Password: test1234
   Currency: 1
   Amount: 500.0
   → New Balance: 1500.00
```

### 取款流程
```
4. Withdraw
   Name: Alice
   Account: 10001
   Password: test1234
   Currency: 1
   Amount: 300.0
   → New Balance: 1200.00
```

### 查询账户
```
5. Query Account
   Account: 10001
   Password: test1234
   → 显示完整账户信息
```

### 转账流程
```
1. 先开户B (Bob, 余额500)
6. Transfer
   From: 10001 (Alice)
   Password: test1234
   To: 10002 (Bob)
   Amount: 200.0
   → New Balance: 1000.00
```

## 🔍 常用选项

### 服务器选项
- `--host`: 监听地址 (默认: 0.0.0.0)
- `--port`: 监听端口 (默认: 5000)
- `--semantics`: at-least-once / at-most-once
- `--loss-rate`: 0.0-1.0 (丢包率)
- `--verbose`: 详细日志

### 客户端选项
- `--server-host`: 服务器地址 (必需)
- `--server-port`: 服务器端口 (默认: 5000)
- `--semantics`: at-least-once / at-most-once
- `--loss-rate`: 0.0-1.0 (丢包率)

## 🐛 调试命令

```bash
# 查看详细日志
python -m src.server.server --verbose

# 测试编解码
python -m unittest tests.test_marshaller -v

# 测试账户管理
python -m unittest tests.test_account_manager -v

# 运行演示脚本
./scripts/run_demo.sh
```

## 📊 性能测试

```bash
# 无丢包测试
python -m src.server.server --loss-rate 0.0

# 轻度丢包（10%）
python -m src.server.server --loss-rate 0.1

# 中度丢包（30%）
python -m src.server.server --loss-rate 0.3

# 重度丢包（50%）
python -m src.server.server --loss-rate 0.5
```

## 🔗 网络测试

```bash
# 本地回环测试
python -m src.client.client --server-host 127.0.0.1

# 局域网测试
python -m src.client.client --server-host 192.168.1.x

# 不同端口测试
python -m src.server.server --port 6000
python -m src.client.client --server-host localhost --server-port 6000
```

## 📝 帮助命令

```bash
# 服务器帮助
python -m src.server.server --help

# 客户端帮助
python -m src.client.client --help
```

## ⚠️ 常见错误

### Connection refused
```bash
# 检查服务器是否运行
# 检查地址和端口是否正确
```

### Request timeout
```bash
# 降低丢包率
# 检查网络连接
# 等待自动重传（最多3次）
```

### Account not found
```bash
# 先开户
# 检查账户号是否正确
```

### Invalid password
```bash
# 检查密码拼写
# 密码区分大小写
```

---

**提示**: 使用 `./scripts/run_demo.sh` 快速验证系统状态
