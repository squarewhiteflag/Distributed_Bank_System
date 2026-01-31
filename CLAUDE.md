# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 UDP 套接字的分布式银行系统课程项目，实现了客户端-服务器架构的银行服务。该项目具有以下关键特点：

- **纯 UDP 通信**：不使用 TCP，仅使用 UDP socket
- **手动编解码**：不使用 pickle、json、RMI、RPC 等高级序列化或框架，所有消息编解码手动实现
- **两种调用语义**：支持 at-least-once（至少一次）和 at-most-once（至多一次）两种调用语义
- **消息丢失模拟**：可配置的消息丢失率，用于测试容错能力
- **监控回调机制**：支持多客户端同时监控账户更新

## 项目架构

### 核心模块

**src/common/** - 公共协议和工具
- `protocol.py`: 定义操作类型枚举（OperationType）、货币类型（CurrencyType）、响应状态（ResponseStatus）
- `marshaller.py`: 消息编解码实现，支持整型、浮点型、定长/变长字符串的手动序列化
- `constants.py`: 系统常量，包括消息格式、网络配置、超时时间等

**src/server/** - 服务器端实现
- `server.py`: 服务器主程序，处理 UDP 请求-响应循环
- `account_manager.py`: 账户管理，维护所有银行账户数据
- `service_handler.py:8`: 实现所有银行服务的业务逻辑（开户、销户、存款、取款、查询、转账等）
- `monitor_manager.py`: 管理注册的监控客户端，处理回调通知

**src/client/** - 客户端实现
- `client.py`: 客户端主程序，处理请求发送和响应接收
- `ui.py`: 用户界面，提供命令行菜单交互
- `monitor.py`: 监控客户端，接收服务器推送的账户更新通知

**src/semantics/** - 调用语义实现
- `request_history.py`: 请求历史管理，用于 at-most-once 语义的重复请求检测
- `message_loss_simulator.py`: 消息丢失模拟器，可配置丢包率

## 常用命令

### 运行服务器

```bash
# 使用默认参数 (host=0.0.0.0, port=5000, at-most-once, 无丢包)
python -m src.server.server

# 使用自定义参数
python -m src.server.server --host 0.0.0.0 --port 5000 --semantics at-most-once --loss-rate 0.3 --verbose

# 参数说明：
# --host: 监听地址（默认：0.0.0.0）
# --port: 监听端口（默认：5000）
# --semantics: 调用语义（at-least-once 或 at-most-once，默认：at-most-once）
# --loss-rate: 消息丢失率 0.0-1.0（默认：0.0）
# --verbose: 启用详细日志
```

### 运行客户端

```bash
# 使用默认参数 (server=localhost:5000, at-most-once, 无丢包)
python -m src.client.client --server-host localhost

# 使用自定义参数
python -m src.client.client --server-host localhost --server-port 5000 --semantics at-most-once --loss-rate 0.2

# 参数说明：
# --server-host: 服务器主机地址（必需）
# --server-port: 服务器端口（默认：5000）
# --semantics: 调用语义（默认：at-most-once）
# --loss-rate: 消息丢失率 0.0-1.0（默认：0.0）
```

### 运行测试

```bash
# 使用 pytest 运行所有测试
python -m pytest tests/ -v

# 使用 unittest 运行所有测试
python -m unittest discover tests/

# 运行单个测试文件
python -m pytest tests/test_marshaller.py -v
python -m pytest tests/test_account_manager.py -v
```

### 使用启动脚本

```bash
# 运行演示（测试 + 提示）
./scripts/run_demo.sh

# 使用脚本启动服务器
./scripts/run_server.sh 0.0.0.0 5000 at-most-once 0.2

# 使用脚本启动客户端
./scripts/run_client.sh localhost 5000 at-most-once 0.1
```

## 消息协议设计

### 请求消息格式

```
[Request ID (4 bytes)] [Operation Type (4 bytes)] [Payload Length (4 bytes)] [Payload]
```

- Request ID: 用于检测重复请求（整数，网络字节序）
- Operation Type: 操作类型（1=开户, 2=销户, 3=存款, 4=取款, 5=注册监控, 6=监控回调, 7=查询, 8=转账）
- Payload Length: 载荷长度（整数，网络字节序）
- Payload: 操作特定的参数数据

### 响应消息格式

```
[Request ID (4 bytes)] [Status (4 bytes)] [Payload Length (4 bytes)] [Payload]
```

- Request ID: 对应的请求 ID
- Status: 响应状态码（0=成功, 1=密码错误, 2=账户不存在, 3=余额不足, 等）
- Payload Length: 载荷长度
- Payload: 响应数据（如账户号、余额等）

## 编解码规则

所有数据类型使用 `struct` 模块进行网络字节序转换：

- **整型**: `struct.pack('!I', value)` - 大端序（网络字节序）
- **浮点型**: `struct.pack('!f', value)` - IEEE 754 单精度，大端序
- **定长字符串**: 填充到固定长度，不足用 `\0` 填充
- **变长字符串**: 4字节长度前缀 + UTF-8 编码的字符串内容

## 银行服务

### 必需服务（6个）

1. **开户 (OPEN_ACCOUNT=1)**: 创建新账户
   - 输入：姓名、密码、货币类型、初始余额
   - 输出：新账户号

2. **销户 (CLOSE_ACCOUNT=2)**: 关闭账户
   - 输入：姓名、账户号、密码
   - 输出：确认消息

3. **存款 (DEPOSIT=3)**: 存入资金
   - 输入：姓名、账户号、密码、货币类型、金额
   - 输出：更新后的余额

4. **取款 (WITHDRAW=4)**: 取出资金
   - 输入：姓名、账户号、密码、货币类型、金额
   - 输出：更新后的余额

5. **注册监控 (MONITOR_REGISTER=5)**: 注册账户更新监控
   - 输入：监控时长（秒）
   - 输出：确认消息

6. **监控回调 (MONITOR_CALLBACK=6)**: 服务器推送账户更新
   - 输入：无（服务器主动推送）
   - 输出：更新的账户信息

### 自定义操作（2个）

7. **查询账户 (QUERY_ACCOUNT=7)**: **幂等操作**
   - 输入：账户号、密码
   - 输出：账户完整信息（账户号、姓名、货币类型、余额）

8. **转账 (TRANSFER=8)**: **非幂等操作**
   - 输入：转出账户号、密码、转入账户号、金额
   - 输出：转出账户的新余额

## 调用语义实现

### At-Least-Once（至少一次）

- **客户端**: 发送请求后超时未收到回复则重传（最多 MAX_RETRIES 次）
- **服务器**: 直接处理每个请求，不检测重复
- **问题**: 非幂等操作（如转账）可能被重复执行，导致余额错误

### At-Most-Once（至多一次）

- **客户端**: 同样使用超时重传机制
  - 重要：客户端 socket 在整个重试循环中保持打开，确保端口不变（`client.py:64`）
  - 服务器使用 (client_address, request_id) 作为键来识别重复请求
- **服务器**:
  - 维护请求历史表（RequestHistory），键为 (client_address, request_id)
  - 收到请求时先检查是否为重复请求
  - 若是重复请求，直接返回历史结果，不重新执行
  - 若是新请求，执行后将结果存入历史表
  - 定期清理过期记录（REQUEST_HISTORY_MAX_AGE=300 秒）

## 监控机制

- 客户端调用 MONITOR_REGISTER 注册监控，提供自己的 UDP 地址和端口
- 服务器在 MonitorManager:1 中记录监控客户端地址和过期时间
- 任何账户更新（开户、销户、存款、取款）完成后，服务器向所有活跃监控客户端推送 MONITOR_CALLBACK 消息
- 监控客户端阻塞等待回调，直到监控时长到期
- 服务器定期清理过期的监控客户端

## 测试

项目包含 24 个单元测试，全部通过：

- `tests/test_marshaller.py`: 测试编解码功能（各种数据类型）
- `tests/test_account_manager.py`: 测试账户管理功能（创建、关闭、存款、取款、查询等）

## 错误处理

服务器返回以下状态码（ResponseStatus 枚举）：
- `SUCCESS (0)`: 操作成功
- `ERROR_INVALID_PASSWORD (1)`: 密码错误
- `ERROR_ACCOUNT_NOT_FOUND (2)`: 账户不存在
- `ERROR_INSUFFICIENT_BALANCE (3)`: 余额不足
- `ERROR_ACCOUNT_NOT_OWNED (4)`: 账户不属于该用户
- `ERROR_INVALID_OPERATION (5)`: 无效操作
- `ERROR_DUPLICATE_REQUEST (6)`: 重复请求（仅在 at-most-once 语义下）
- `ERROR_UNKNOWN (99)`: 未知错误

## 重要约束

⚠️ **课程项目限制**：
- ❌ 禁止使用 TCP，仅使用 UDP
- ❌ 禁止使用 RMI、RPC、CORBA 等框架
- ❌ 禁止使用 pickle、json 等高级序列化工具
- ✅ 必须手动实现所有编解码
- ✅ 仅使用 Python 标准库（socket、struct 等）

✅ **本项目特性**：
- Python 3.8+ 兼容
- 无第三方依赖
- 完整的类型注解和文档字符串
- 模块化设计，职责清晰

## 已修复的缺陷

根据 CURRENT_DEFECTS.md，以下问题已在代码中修复：
1. 监控回调端口问题：服务器现在正确记录客户端的请求 socket 端口
2. 监控回调解析问题：客户端正确解析载荷长度
3. 转账响应解析 bug：修复了载荷长度误读为余额的问题
4. At-most-once 重复检测：使用 (client_address, request_id) 作为键，避免跨客户端冲突
5. 查询账户错误顺序：先检查账户存在性，再验证密码
6. 存款/取款缺少验证：添加了所有者和货币类型验证
7. 监控回调广播问题：只向更新的账户发送通知
8. 客户端语义标志未使用：at-most-once 语义下避免重复重试
9. 服务器缺少日志：添加了强制的请求/响应日志输出

## 调试和演示场景

### 场景 1：基本银行操作

```bash
# 终端 1：启动服务器
python -m src.server.server --verbose

# 终端 2：启动客户端并执行操作
python -m src.client.client --server-host localhost
# 依次执行：开户 → 存款 → 取款 → 查询 → 销户
```

### 场景 2：监控回调

```bash
# 终端 1：启动服务器
python -m src.server.server --verbose

# 终端 2：客户端 1 注册监控
python -m src.client.client --server-host localhost
# 选择菜单项 7 (Monitor Account Updates)，输入监控时长 60

# 终端 3：客户端 2 执行操作
python -m src.client.client --server-host localhost
# 执行开户、存款等操作

# 客户端 1 应该实时接收到账户更新通知
```

### 场景 3：调用语义对比 - At-Least-Once 的重复执行问题

```bash
# 终端 1：启动服务器（至少一次语义 + 30% 丢包）
python -m src.server.server --semantics at-least-once --loss-rate 0.3 --verbose

# 终端 2：启动客户端
python -m src.client.client --server-host localhost --semantics at-least-once --loss-rate 0.2

# 执行转账操作，观察余额是否被错误累加
```

### 场景 4：调用语义对比 - At-Most-Once 的正确处理

```bash
# 终端 1：启动服务器（至多一次语义 + 30% 丢包）
python -m src.server.server --semantics at-most-once --loss-rate 0.3 --verbose

# 终端 2：启动客户端
python -m src.client.client --server-host localhost --semantics at-most-once --loss-rate 0.2

# 执行相同操作，验证即使有丢包也不会重复执行
```

## 开发注意事项

- 服务器处理请求的入口在 `server.py:87` 的 `_process_request` 方法
- 账户数据存储在内存中（`AccountManager`），服务器重启后数据丢失
- 请求 ID 由客户端维护的计数器生成（`client.py:42`）
- 服务器和客户端都支持消息丢失模拟，通过 `--loss-rate` 参数控制
- 所有网络通信使用 UDP socket，注意消息大小不超过 MAX_MESSAGE_SIZE (1024 字节)
- 监控回调需要客户端保持 socket 打开并监听，因此使用 `_send_request_with_socket` 方法
- **at-most-once 语义的关键**：客户端必须在重试循环中保持同一 socket 端口，服务器才能通过 (client_address, request_id) 正确识别重复请求