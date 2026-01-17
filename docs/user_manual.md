# 分布式银行系统 - 用户手册

## 目录

1. [快速入门](#快速入门)
2. [系统要求](#系统要求)
3. [安装](#安装)
4. [启动服务器](#启动服务器)
5. [使用客户端](#使用客户端)
6. [功能详解](#功能详解)
7. [常见问题](#常见问题)

## 快速入门

### 最简启动方式

1. **启动服务器**（在终端1）:
   ```bash
   python -m src.server.server
   ```

2. **启动客户端**（在终端2）:
   ```bash
   python -m src.client.client --server-host localhost
   ```

3. **开始使用**：
   - 按照菜单提示选择操作
   - 开户、存款、取款等

## 系统要求

- Python 3.8 或更高版本
- 仅需Python标准库，无需安装第三方包
- 支持Windows、macOS、Linux

## 安装

### 从源码运行

1. 克隆或下载项目代码
2. 进入项目目录：
   ```bash
   cd distributed-banking-system
   ```

3. 验证安装：
   ```bash
   python --version  # 确保Python >= 3.8
   python -m unittest discover tests/  # 运行测试
   ```

## 启动服务器

### 基本启动

```bash
# 使用默认参数
python -m src.server.server
```

服务器将在 `0.0.0.0:5000` 上监听，使用 `at-most-once` 语义，无消息丢失。

### 高级选项

```bash
python -m src.server.server \
  --host 0.0.0.0 \        # 监听地址（默认0.0.0.0）
  --port 5000 \           # 监听端口（默认5000）
  --semantics at-most-once \  # 调用语义：at-least-once或at-most-once
  --loss-rate 0.2 \       # 消息丢失率0.0-1.0（默认0.0）
  --verbose               # 详细日志（可选）
```

### 使用启动脚本

```bash
./scripts/run_server.sh [host] [port] [semantics] [loss-rate]

# 示例
./scripts/run_server.sh 0.0.0.0 5000 at-most-once 0.2
```

### 服务器输出示例

```
Server started on 0.0.0.0:5000
Semantics: at-most-once
Message loss rate: 20.0%
Waiting for clients...
```

### 停止服务器

按 `Ctrl+C` 停止服务器。

## 使用客户端

### 基本启动

```bash
python -m src.client.client --server-host localhost
```

### 高级选项

```bash
python -m src.client.client \
  --server-host 192.168.1.100 \  # 服务器主机地址（必需）
  --server-port 5000 \           # 服务器端口（默认5000）
  --semantics at-most-once \     # 调用语义（默认at-most-once）
  --loss-rate 0.1                # 消息丢失率（默认0.0）
```

### 使用启动脚本

```bash
./scripts/run_client.sh [server_host] [server_port] [semantics] [loss-rate]

# 示例
./scripts/run_client.sh localhost 5000 at-most-once 0.1
```

## 功能详解

### 菜单界面

```
==================================================
Distributed Banking System - Client
==================================================
1. Open Account
2. Close Account
3. Deposit
4. Withdraw
5. Query Account (Idempotent Operation)
6. Transfer (Non-idempotent Operation)
7. Monitor Account Updates
0. Exit
==================================================
```

### 1. 开户 (Open Account)

**功能**：创建新的银行账户

**步骤**：
1. 选择菜单项 `1`
2. 输入姓名（最多64字符）
3. 输入密码（最多16字符）
4. 选择货币类型：
   - `1` = USD (美元)
   - `2` = EUR (欧元)
   - `3` = SGD (新加坡元)
   - `4` = CNY (人民币)
5. 输入初始余额

**示例**：
```
Enter your name: Alice
Enter password (max 16 chars): mypass123
Currency types: 1=USD, 2=EUR, 3=SGD, 4=CNY
Enter currency type: 1
Enter initial balance: 1000.0
✓ Success: Account created successfully! Account Number: 10001
```

### 2. 销户 (Close Account)

**功能**：关闭现有账户

**步骤**：
1. 选择菜单项 `2`
2. 输入姓名
3. 输入账户号
4. 输入密码

**错误处理**：
- 账户不存在：显示 "Account not found!"
- 密码错误：显示 "Invalid password!"
- 账户不属于该用户：显示 "Account does not belong to this user!"

### 3. 存款 (Deposit)

**功能**：向账户存入资金

**步骤**：
1. 选择菜单项 `3`
2. 输入姓名
3. 输入账户号
4. 输入密码
5. 选择货币类型
6. 输入存款金额

**示例**：
```
--- Deposit ---
Enter your name: Alice
Enter account number: 10001
Enter password: mypass123
Currency types: 1=USD, 2=EUR, 3=SGD, 4=CNY
Enter currency type: 1
Enter amount to deposit: 500.0
✓ Success: Deposit successful! New balance: 1500.00
```

### 4. 取款 (Withdraw)

**功能**：从账户取出资金

**步骤**：与存款类似

**错误处理**：
- 余额不足：显示 "Insufficient balance!"

### 5. 查询账户 (Query Account) - 幂等操作

**功能**：查询账户详细信息

**特性**：
- **幂等性**：重复执行不会改变系统状态
- 安全的查询操作，适合测试至少一次语义

**步骤**：
1. 选择菜单项 `5`
2. 输入账户号
3. 输入密码

**示例**：
```
--- Query Account ---
Enter account number: 10001
Enter password: mypass123
✓ Success: Account Information:
  Account Number: 10001
  Name: Alice
  Currency: USD
  Balance: 1500.00
```

### 6. 转账 (Transfer) - 非幂等操作

**功能**：从一个账户转账到另一个账户

**特性**：
- **非幂等性**：重复执行会导致余额错误累加
- 适合测试至少一次语义的问题

**步骤**：
1. 选择菜单项 `6`
2. 输入转出账户号
3. 输入转出账户密码
4. 输入转入账户号
5. 输入转账金额

**示例**：
```
--- Transfer ---
Enter source account number: 10001
Enter source account password: mypass123
Enter destination account number: 10002
Enter amount to transfer: 300.0
✓ Success: Transfer successful! New balance in source account: 1200.00
```

### 7. 监控账户更新 (Monitor Account Updates)

**功能**：实时接收所有账户的更新通知

**步骤**：
1. 选择菜单项 `7`
2. 输入监控时长（10-300秒）
3. 客户端阻塞等待回调通知
4. 期间其他客户端的账户操作会触发通知

**使用场景**：

在**终端1**启动监控：
```
Enter monitoring duration in seconds (10-300): 60
Monitoring on port 12345 for 60 seconds...
```

在**终端2**执行操作：
```
(开户、存款等)
```

**终端1**会实时显示：
```
==================================================
Account Update Notification
==================================================
Account Number: 10001
Name: Alice
Currency: USD
Balance: 1500.00
==================================================
```

## 调用语义实验

### 实验1：至少一次语义 (At-Least-Once)

**特点**：
- 客户端超时重传
- 服务器直接处理所有请求
- 问题：非幂等操作可能重复执行

**实验步骤**：

1. **启动服务器**（至少一次，30%丢包率）：
   ```bash
   python -m src.server.server --semantics at-least-once --loss-rate 0.3
   ```

2. **启动客户端**（至少一次，20%丢包率）：
   ```bash
   python -m src.client.client --server-host localhost --semantics at-least-once --loss-rate 0.2
   ```

3. **执行转账操作**多次：
   - 从账户A转账100到账户B
   - 观察余额是否被错误扣除多次

**预期结果**：
- 由于消息丢失和重传，转账可能执行多次
- 账户A的余额可能被扣除多次（如300而不是100）

### 实验2：至多一次语义 (At-Most-Once)

**特点**：
- 客户端超时重传
- 服务器检测重复请求
- 重复请求返回历史结果

**实验步骤**：

1. **启动服务器**（至多一次，30%丢包率）：
   ```bash
   python -m src.server.server --semantics at-most-once --loss-rate 0.3
   ```

2. **启动客户端**（至多一次，20%丢包率）：
   ```bash
   python -m src.client.client --server-host localhost --semantics at-most-once --loss-rate 0.2
   ```

3. **执行相同的转账操作**

**预期结果**：
- 即使有丢包和重传，转账只执行一次
- 余额正确

## 常见问题

### Q1: 如何测试系统是否正常工作？

运行测试脚本：
```bash
./scripts/run_demo.sh
```

或手动运行测试：
```bash
python -m unittest discover tests/
```

### Q2: 如何在不同机器上运行？

1. 在服务器机器上：
   ```bash
   python -m src.server.server --host 0.0.0.0
   ```

2. 在客户端机器上：
   ```bash
   python -m src.client.client --server-host <服务器IP地址>
   ```

### Q3: 消息丢失率应该设置多少？

- **测试正常功能**：设置为 `0.0`（不丢失）
- **测试容错能力**：设置为 `0.2` - `0.4`（20%-40%丢包率）
- **极端测试**：设置为 `0.5` 或更高（但可能导致大量超时）

### Q4: 监控功能不工作？

检查：
1. 是否正确注册监控（选择菜单项7）
2. 服务器是否运行在正确地址
3. 防火墙是否阻止UDP通信
4. 监控时长是否在10-300秒范围内

### Q5: 为什么密码限制16个字符？

这是项目要求，密码使用定长字符串（16字节）传输。
- 输入少于16字符会自动填充
- 输入超过16字符会被截断

### Q6: 如何查看详细日志？

在启动服务器时使用 `--verbose` 参数：
```bash
python -m src.server.server --verbose
```

会显示：
- 每个接收到的请求
- 处理过程
- 发送的响应
- 消息丢失情况

### Q7: "Connection refused" 错误？

检查：
1. 服务器是否正在运行
2. 服务器地址和端口是否正确
3. 防火墙设置

### Q8: "Request timeout" 错误？

可能原因：
1. 网络延迟过高
2. 服务器负载过高
3. 消息丢失率设置过高

解决方法：
- 降低消息丢失率
- 检查网络连接
- 等待重传（最多3次）

## 技术支持

如有问题，请检查：
1. Python版本是否 >= 3.8
2. 是否在项目根目录运行命令
3. 运行测试确认代码正确性
4. 查看服务器/客户端的错误日志

---

**文档版本**: 1.0
**最后更新**: 2026年1月
