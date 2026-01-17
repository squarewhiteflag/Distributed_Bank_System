# 分布式银行系统 (Distributed Banking System)

基于UDP套接字的分布式银行系统实现，支持多种银行操作、监控回调和两种调用语义。

## 项目概述

本项目是一个课程项目，要求实现一个分布式银行系统，具有以下特点：

- **通信协议**：纯UDP（不使用TCP）
- **消息编解码**：手动实现，不使用pickle、json等高级序列化工具
- **调用语义**：支持至少一次（at-least-once）和至多一次（at-most-once）两种语义
- **消息丢失模拟**：可配置的丢包率，用于测试容错能力
- **监控机制**：支持多客户端同时监控账户更新

## 功能特性

### 必需服务（6个）

1. **开户 (Open Account)**：创建新银行账户
2. **销户 (Close Account)**：关闭现有账户
3. **存款 (Deposit)**：向账户存入资金
4. **取款 (Withdraw)**：从账户取出资金
5. **监控注册 (Monitor Registration)**：注册接收账户更新通知
6. **回调通知 (Callback Notification)**：向监控客户端推送账户更新

### 自定义操作（2个）

1. **查询账户 (Query Account)** - **幂等操作**
   - 查询账户详细信息（账户号、姓名、货币类型、余额）
   - 重复执行不会改变系统状态

2. **转账 (Transfer)** - **非幂等操作**
   - 从一个账户转账到另一个账户
   - 在至少一次语义下，重复执行会导致余额错误

## 项目结构

```
distributed-banking-system/
├── src/                          # 源代码
│   ├── common/                   # 公共模块
│   │   ├── protocol.py           # 消息协议定义
│   │   ├── marshaller.py         # 消息编解码工具
│   │   └── constants.py          # 常量定义
│   ├── server/                   # 服务器模块
│   │   ├── server.py             # 服务器主程序
│   │   ├── account_manager.py    # 账户管理
│   │   ├── service_handler.py    # 服务处理逻辑
│   │   └── monitor_manager.py    # 监控客户端管理
│   ├── client/                   # 客户端模块
│   │   ├── client.py             # 客户端主程序
│   │   ├── ui.py                 # 用户界面
│   │   └── monitor.py            # 监控接收逻辑
│   └── semantics/                # 调用语义模块
│       ├── request_history.py    # 请求历史管理
│       └── message_loss_simulator.py  # 消息丢失模拟
├── tests/                        # 测试
│   ├── test_marshaller.py        # 编解码测试
│   └── test_account_manager.py   # 账户管理测试
├── scripts/                      # 启动脚本
│   ├── run_server.sh             # 启动服务器
│   └── run_client.sh             # 启动客户端
├── docs/                         # 文档
├── logs/                         # 日志目录
└── README.md                     # 本文件
```

## 安装和运行

### 系统要求

- Python 3.8 或更高版本
- 仅使用Python标准库，无需安装第三方包

### 运行服务器

```bash
# 使用默认参数 (host=0.0.0.0, port=5000, at-most-once, 无丢包)
python -m src.server.server

# 使用自定义参数
python -m src.server.server \
  --host 0.0.0.0 \
  --port 5000 \
  --semantics at-most-once \
  --loss-rate 0.2 \
  --verbose

# 或使用启动脚本
./scripts/run_server.sh 0.0.0.0 5000 at-most-once 0.2
```

### 运行客户端

```bash
# 使用默认参数 (server=localhost:5000, at-most-once, 无丢包)
python -m src.client.client --server-host localhost

# 使用自定义参数
python -m src.client.client \
  --server-host 192.168.1.100 \
  --server-port 5000 \
  --semantics at-most-once \
  --loss-rate 0.1

# 或使用启动脚本
./scripts/run_client.sh localhost 5000 at-most-once 0.1
```

### 命令行参数说明

#### 服务器参数

- `--host`：监听地址（默认：0.0.0.0）
- `--port`：监听端口（默认：5000）
- `--semantics`：调用语义（at-least-once 或 at-most-once，默认：at-most-once）
- `--loss-rate`：消息丢失率 0.0-1.0（默认：0.0，即不丢失）
- `--verbose`：启用详细日志

#### 客户端参数

- `--server-host`：服务器主机地址（必需）
- `--server-port`：服务器端口（默认：5000）
- `--semantics`：调用语义（默认：at-most-once）
- `--loss-rate`：消息丢失率 0.0-1.0（默认：0.0）

## 使用示例

### 基本银行操作

1. **开户**
   - 选择菜单项 1
   - 输入姓名、密码、货币类型（1=USD, 2=EUR, 3=SGD, 4=CNY）和初始余额
   - 服务器返回新账户号

2. **存款**
   - 选择菜单项 3
   - 输入姓名、账户号、密码、货币类型和存款金额
   - 服务器返回更新后的余额

3. **取款**
   - 选择菜单项 4
   - 输入姓名、账户号、密码、货币类型和取款金额
   - 服务器返回更新后的余额

4. **查询账户（幂等操作）**
   - 选择菜单项 5
   - 输入账户号和密码
   - 服务器返回完整账户信息

5. **转账（非幂等操作）**
   - 选择菜单项 6
   - 输入转出账户号、密码、转入账户号和转账金额
   - 服务器返回转出账户的新余额

### 监控账户更新

1. 在客户端1中选择菜单项 7
2. 输入监控时长（10-300秒）
3. 客户端1阻塞等待回调通知
4. 在客户端2中执行任何账户操作（开户、存款等）
5. 客户端1会实时显示账户更新通知

## 测试

### 运行单元测试

```bash
# 测试编解码功能
python -m pytest tests/test_marshaller.py -v

# 测试账户管理功能
python -m pytest tests/test_account_manager.py -v

# 运行所有测试
python -m pytest tests/ -v

# 或使用unittest
python -m unittest tests.test_marshaller
python -m unittest tests.test_account_manager
```

## 调用语义对比实验

### 至少一次（at-least-once）

- 客户端发送请求后超时未收到回复则重传
- 服务器直接处理每个请求，不检测重复
- **问题**：非幂等操作（如转账）可能被重复执行

实验步骤：
```bash
# 终端1：启动服务器（至少一次语义，30%丢包率）
python -m src.server.server --port 5000 --semantics at-least-once --loss-rate 0.3

# 终端2：启动客户端
python -m src.client.client --server-host localhost --semantics at-least-once --loss-rate 0.2

# 执行转账操作，观察余额是否错误累加
```

### 至多一次（at-most-once）

- 客户端同样使用超时重传机制
- 服务器维护请求历史表，检测重复请求
- 重复请求直接返回历史结果，不重新执行
- **优势**：所有操作都能正确处理

实验步骤：
```bash
# 终端1：启动服务器（至多一次语义，30%丢包率）
python -m src.server.server --port 5000 --semantics at-most-once --loss-rate 0.3

# 终端2：启动客户端
python -m src.client.client --server-host localhost --semantics at-most-once --loss-rate 0.2

# 执行相同的操作，验证即使有丢包也不会重复执行
```

## 技术实现细节

### 消息格式

所有消息都使用以下格式：

**请求消息**：
```
[Request ID (4 bytes)] [Operation Type (4 bytes)] [Payload Length (4 bytes)] [Payload]
```

**响应消息**：
```
[Request ID (4 bytes)] [Status (4 bytes)] [Payload Length (4 bytes)] [Payload]
```

### 编码规则

- **整型**：使用`struct.pack('!I')`转换为网络字节序（大端）
- **浮点型**：使用`struct.pack('!f')`转换为网络字节序
- **定长字符串**：填充到固定长度，不足部分用`\0`填充
- **变长字符串**：4字节长度前缀 + 实际字符串内容

### 错误处理

服务器返回以下状态码：
- `SUCCESS (0)`：操作成功
- `ERROR_INVALID_PASSWORD (1)`：密码错误
- `ERROR_ACCOUNT_NOT_FOUND (2)`：账户不存在
- `ERROR_INSUFFICIENT_BALANCE (3)`：余额不足
- `ERROR_ACCOUNT_NOT_OWNED (4)`：账户不属于该用户
- `ERROR_INVALID_OPERATION (5)`：无效操作
- `ERROR_DUPLICATE_REQUEST (6)`：重复请求
- `ERROR_UNKNOWN (99)`：未知错误

## 开发规范

- 所有代码都有详细的类型注解和文档字符串
- 模块化设计，各组件职责清晰
- 禁止使用`pickle`、`json`等高级序列化工具
- 仅使用`socket`和`struct`进行网络通信和编解码

## 项目限制

本项目是课程项目，有以下限制：
- 不使用TCP，仅使用UDP
- 不使用RMI、RPC、CORBA等框架
- 不使用Java序列化或Python的pickle
- 所有编解码必须手动实现

## 作者

课程项目团队

## 许可证

本项目仅用于教学目的。

---

**最后更新**：2026年1月
