# 分布式银行系统 - Claude Code Agent 开发指南

> 本文档专门为使用 Claude Code 进行 agentic 开发准备，包含清晰的任务拆解和实现细节。

---

## 项目快速启动指南

### 第一步：初始化项目结构

```bash
# 创建项目根目录(已经完成)
mkdir distributed-banking-system
cd distributed-banking-system

# 创建所有必要的目录
mkdir -p src/{common,server,client,semantics}
mkdir -p tests scripts/{experiments} logs docs data

# 创建__init__.py文件
touch src/__init__.py
touch src/common/__init__.py
touch src/server/__init__.py
touch src/client/__init__.py
touch src/semantics/__init__.py
touch tests/__init__.py

# 创建主要源文件
touch src/common/{protocol.py,marshaller.py,constants.py}
touch src/server/{server.py,account_manager.py,service_handler.py,monitor_manager.py,operations.py}
touch src/client/{client.py,ui.py,monitor.py,operations.py}
touch src/semantics/{at_least_once.py,at_most_once.py,request_history.py,message_loss_simulator.py}

# 创建文档文件
touch README.md docs/{design_document.md,protocol_specification.md,user_manual.md}

# 创建requirements.txt（本项目仅需标准库）
echo "# This project uses only Python standard library" > requirements.txt
```

---

## Agent 任务分解

### 任务1：实现消息协议和编解码（优先级：最高）

**负责人：成员B**  
**依赖：无**  
**目标：建立通信基础**

#### 1.1 实现 `src/common/protocol.py`

```python
"""
任务：定义所有操作类型、货币类型、响应状态码
要求：
1. 使用 IntEnum 定义枚举类型
2. 定义消息格式常量
3. 不允许使用任何高级序列化库
"""

# Agent 实现要点：
# - OperationType: 至少8个操作类型（6个必需 + 2个自定义）
# - CurrencyType: 至少4种货币
# - ResponseStatus: 至少6种状态码
# - 定义 HEADER_SIZE, MAX_NAME_LENGTH 等常量
```

#### 1.2 实现 `src/common/marshaller.py`

```python
"""
任务：手动实现所有数据类型的序列化和反序列化
要求：
1. 使用 struct.pack/unpack 处理整型和浮点型
2. 使用网络字节序（大端序，'!' 格式）
3. 变长字符串：4字节长度前缀 + UTF-8编码内容
4. 定长字符串：固定长度，空位填充'\x00'
5. 提供 RequestBuilder 和 ResponseBuilder 类

禁止：
- pickle, json 序列化
- BytesIO 等流式对象
"""

# Agent 实现要点：
# - Marshaller 类的静态方法
# - pack_int/unpack_int: 使用 struct.pack('!I', value)
# - pack_float/unpack_float: 使用 struct.pack('!f', value)
# - pack_string/unpack_string: 处理变长和定长两种情况
# - RequestBuilder/ResponseBuilder: 链式调用接口
```

#### 1.3 单元测试

```python
# tests/test_marshaller.py
"""
测试所有编解码功能
- 测试整型正负数
- 测试浮点数精度
- 测试变长字符串（包括中文）
- 测试定长字符串
- 测试消息构建器
"""
```

**验收标准：**
- [ ] 所有数据类型编解码往返测试通过
- [ ] 变长字符串支持任意长度
- [ ] 定长字符串正确填充和截断
- [ ] 消息构建器生成正确的字节序列

---

### 任务2：实现账户管理和服务器核心（优先级：高）

**负责人：成员A**  
**依赖：任务1（协议和编解码）**  
**目标：建立服务器基础功能**

#### 2.1 实现 `src/server/account_manager.py`

```python
"""
任务：实现账户数据管理
要求：
1. 使用 dataclass 定义 Account 数据类
2. AccountManager 维护账户字典 {account_number: Account}
3. 实现账户号自动递增（从10001开始）
4. 实现所有账户操作方法并抛出明确的异常

方法清单：
- create_account(name, password, currency, balance) -> int
- close_account(account_number, name, password) -> bool
- deposit(account_number, password, amount) -> float
- withdraw(account_number, password, amount) -> float
- get_account(account_number) -> Optional[Account]
- verify_password(account_number, password) -> bool
"""

# Agent 实现要点：
# - 使用 @dataclass 装饰器
# - 详细的异常消息（用于错误处理）
# - 线程安全考虑（虽然单线程，但要预留）
```

#### 2.2 实现 `src/server/monitor_manager.py`

```python
"""
任务：管理监控客户端列表
要求：
1. 维护监控客户端列表（IP、端口、过期时间）
2. 支持添加、删除、检查过期
3. 获取所有活跃监控客户端

数据结构：
{
    (ip, port): {
        'expire_time': timestamp,
        'duration': seconds
    }
}
"""

# Agent 实现要点：
# - 使用字典存储客户端信息
# - 使用 time.time() 管理过期时间
# - cleanup_expired() 方法定期清理
```

#### 2.3 实现 `src/server/service_handler.py`

```python
"""
任务：处理客户端请求并调用相应服务
要求：
1. 解析请求消息（使用 Marshaller）
2. 调用 AccountManager 执行操作
3. 构建响应消息
4. 处理所有异常并返回错误码

核心方法：
- handle_request(request_data: bytes) -> bytes
- _handle_open_account(payload: bytes) -> bytes
- _handle_close_account(payload: bytes) -> bytes
- _handle_deposit(payload: bytes) -> bytes
- _handle_withdraw(payload: bytes) -> bytes
"""

# Agent 实现要点：
# - 使用字典映射操作类型到处理函数
# - 统一的异常处理和错误响应
# - 详细的日志记录
```

#### 2.4 实现 `src/server/server.py`

```python
"""
任务：服务器主程序
要求：
1. 解析命令行参数（host, port, semantics, loss-rate）
2. 创建UDP socket并绑定
3. 主循环：接收请求 -> 处理 -> 发送响应
4. 触发监控回调
5. 定期清理过期监控客户端

命令行参数：
--host: 绑定地址（默认 0.0.0.0）
--port: 监听端口（默认 5000）
--semantics: at-least-once 或 at-most-once
--loss-rate: 消息丢失率（0.0-1.0）
--verbose: 详细日志
"""

# Agent 实现要点：
# - 使用 argparse 解析参数
# - socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# - 根据 semantics 参数选择处理器
# - 实现消息丢失模拟
# - 优雅的错误处理和日志
```

**验收标准：**
- [ ] 服务器能正确启动并监听
- [ ] 所有账户操作正确执行
- [ ] 错误处理返回正确的状态码
- [ ] 监控客户端列表维护正确
- [ ] 日志清晰可读

---

### 任务3：实现调用语义和容错机制（优先级：高）

**负责人：成员C**  
**依赖：任务1（协议和编解码）**  
**目标：实现两种调用语义**

#### 3.1 实现 `src/semantics/request_history.py`

```python
"""
任务：请求历史管理（用于至多一次语义）
要求：
1. 存储请求ID到响应的映射
2. 检查重复请求
3. 返回缓存的响应
4. 定期清理过期记录

数据结构：
{
    request_id: (response_bytes, timestamp)
}
"""

# Agent 实现要点：
# - 使用字典存储历史
# - is_duplicate(request_id) -> bool
# - get_cached_response(request_id) -> Optional[bytes]
# - record_request(request_id, response)
# - cleanup_old_records() 清理过期记录
```

#### 3.2 实现 `src/semantics/message_loss_simulator.py`

```python
"""
任务：消息丢失模拟器
要求：
1. 根据配置的丢包率随机丢弃消息
2. 记录丢失的消息（用于调试）
3. 提供统计信息

核心方法：
- should_drop_message(loss_rate: float) -> bool
- log_dropped_message(message_type: str)
- get_statistics() -> dict
"""

# Agent 实现要点：
# - 使用 random.random() < loss_rate
# - 记录丢失计数
# - 日志输出被丢弃的消息
```

#### 3.3 实现 `src/semantics/at_least_once.py`

```python
"""
任务：至少一次语义（客户端）
要求：
1. 发送请求
2. 等待响应（带超时）
3. 超时后重传（最多N次）
4. 不检测重复响应

核心方法：
- send_request_with_retry(
    sock: socket, 
    request: bytes, 
    server_addr: tuple,
    timeout: float = 5.0,
    max_retries: int = 3
  ) -> bytes
"""

# Agent 实现要点：
# - sock.settimeout(timeout)
# - try-except socket.timeout
# - 循环重传逻辑
# - 日志记录每次重传
```

#### 3.4 实现 `src/semantics/at_most_once.py`

```python
"""
任务：至多一次语义（服务器端）
要求：
1. 检查请求是否重复
2. 如果重复，直接返回缓存响应
3. 如果新请求，执行并缓存响应
4. 定期清理历史记录

核心方法：
- process_request(
    request_id: int,
    request_data: bytes,
    handler: Callable
  ) -> bytes
"""

# Agent 实现要点：
# - 使用 RequestHistory
# - 先检查 is_duplicate()
# - 若重复返回 get_cached_response()
# - 若新请求执行 handler() 并 record_request()
```

#### 3.5 实现实验脚本

```python
# scripts/experiments/experiment_at_least_once.py
"""
实验：证明至少一次语义会导致非幂等操作错误

步骤：
1. 启动服务器（至少一次模式，30%丢包率）
2. 客户端开户并存款100元
3. 客户端执行非幂等操作（如转账或添加利息）
4. 模拟消息丢失导致重传
5. 观察余额错误（如变成110而非105）

预期结果：非幂等操作被执行多次，余额错误
"""

# scripts/experiments/experiment_at_most_once.py
"""
实验：证明至多一次语义正确处理所有操作

步骤：
1. 启动服务器（至多一次模式，30%丢包率）
2. 执行相同的操作序列
3. 观察余额正确（105）

预期结果：即使消息丢失，余额仍然正确
"""
```

**验收标准：**
- [ ] 至少一次语义：重传机制工作
- [ ] 至多一次语义：重复检测工作
- [ ] 消息丢失模拟可配置
- [ ] 实验能清晰展示差异
- [ ] 实验结果可记录和分析

---

### 任务4：实现客户端界面和监控（优先级：中）

**负责人：成员D**  
**依赖：任务1、任务2、任务3**  
**目标：提供完整的用户交互**

#### 4.1 实现 `src/client/ui.py`

```python
"""
任务：命令行用户界面
要求：
1. 显示菜单
2. 获取用户输入
3. 验证输入有效性
4. 显示操作结果

菜单项：
0. Exit
1. Open Account
2. Close Account
3. Deposit
4. Withdraw
5. Query Account (幂等)
6. Transfer (非幂等)
7. Monitor Account Updates
"""

# Agent 实现要点：
# - 清晰的菜单显示
# - 友好的输入提示
# - 输入验证和错误处理
# - 结果格式化输出
```

#### 4.2 实现 `src/client/monitor.py`

```python
"""
任务：监控接收逻辑
要求：
1. 发送监控注册请求
2. 阻塞等待回调消息
3. 解析并显示账户更新
4. 监控超时后恢复正常

核心方法：
- register_monitor(sock, duration: int) -> bool
- receive_callbacks(sock, duration: int)
- display_account_update(account_info: dict)
"""

# Agent 实现要点：
# - 发送监控注册请求
# - 使用 sock.settimeout(duration)
# - 循环接收直到超时
# - 格式化显示更新信息
```

#### 4.3 实现 `src/client/operations.py`

```python
"""
任务：自定义幂等操作
要求：
1. 实现查询账户详情操作
2. 构建请求消息
3. 解析响应消息
4. 显示账户信息

幂等操作示例：
- query_account(account_number, password) -> Account Info
"""

# Agent 实现要点：
# - 使用 RequestBuilder 构建请求
# - 发送并接收响应
# - 使用 Marshaller 解析响应
# - 格式化输出账户信息
```

#### 4.4 实现 `src/client/client.py`

```python
"""
任务：客户端主程序
要求：
1. 解析命令行参数
2. 创建UDP socket
3. 主循环：显示菜单 -> 获取选择 -> 执行操作
4. 调用相应的服务请求函数
5. 显示结果或错误

命令行参数：
--server-host: 服务器地址
--server-port: 服务器端口
--semantics: 调用语义类型
--loss-rate: 客户端消息丢失率（可选）
"""

# Agent 实现要点：
# - argparse 解析参数
# - 创建 UDP socket
# - 主循环调用 UI 和操作函数
# - 统一的错误处理
# - 优雅退出
```

**验收标准：**
- [ ] 菜单清晰易用
- [ ] 所有操作都能正确执行
- [ ] 监控功能正常工作
- [ ] 错误消息友好
- [ ] 退出流程正确

---

### 任务5：实现自定义操作（优先级：中）

#### 5.1 服务器端非幂等操作（成员A）

```python
# src/server/operations.py

def transfer_money(
    account_manager: AccountManager,
    from_account: int,
    from_password: str,
    to_account: int,
    amount: float
) -> tuple:
    """
    转账操作（非幂等）
    
    返回：(from_balance, to_balance)
    
    注意：这个操作在重复执行时会导致错误
    """
    # Agent 实现要点：
    # - 验证源账户密码
    # - 检查余额充足
    # - 从源账户扣款
    # - 向目标账户加款
    # - 返回两个账户的新余额
```

#### 5.2 客户端幂等操作（成员D）

```python
# src/client/operations.py

def query_account_details(
    sock: socket,
    account_number: int,
    password: str,
    server_addr: tuple
) -> dict:
    """
    查询账户详情（幂等）
    
    返回：账户完整信息
    
    注意：多次执行不会改变系统状态
    """
    # Agent 实现要点：
    # - 构建查询请求
    # - 发送并接收响应
    # - 解析账户信息
    # - 返回字典格式数据
```

---

## 开发顺序建议

### 第一阶段（1-2天）：建立通信基础
1. **任务1.1 + 1.2**：协议定义和编解码
2. **测试1.3**：确保编解码正确

### 第二阶段（2-3天）：服务器核心功能
3. **任务2.1**：账户管理
4. **任务2.2**：监控管理
5. **任务2.3 + 2.4**：服务处理和服务器主程序

### 第三阶段（2-3天）：调用语义和客户端
6. **任务3.1 + 3.2**：请求历史和消息丢失模拟
7. **任务3.3 + 3.4**：两种调用语义
8. **任务4.1 + 4.4**：客户端界面和主程序

### 第四阶段（1-2天）：完善功能
9. **任务4.2**：监控接收
10. **任务5.1 + 5.2**：自定义操作
11. **任务3.5**：实验脚本

### 第五阶段（1-2天）：测试和文档
12. **集成测试**：完整流程测试
13. **文档编写**：设计文档、用户手册
14. **演示准备**：准备演示脚本

---

## Claude Code Agent 使用技巧

### 1. 分模块开发
```
# 每次让Agent专注一个文件
"请实现 src/common/marshaller.py，包含所有编解码功能"

# 而不是
"请实现整个项目"
```

### 2. 提供清晰的需求
```
# Good
"实现 AccountManager.deposit() 方法：
- 输入：account_number, password, amount
- 验证密码
- 增加余额
- 返回新余额
- 抛出异常：账户不存在、密码错误"

# Bad
"实现存款功能"
```

### 3. 要求测试
```
"实现 Marshaller.pack_string() 并编写单元测试，
测试应包括：空字符串、英文、中文、长字符串"
```

### 4. 迭代改进
```
"运行测试失败了，错误是 XXX，请修复"
"性能有问题，请优化 XXX 部分"
```

### 5. 代码审查
```
"审查 account_manager.py，检查：
- 是否有异常处理
- 是否有类型注解
- 是否有文档字符串
- 是否符合PEP8规范"
```

---

## 调试技巧

### 1. 消息调试

```python
# 在发送前打印消息的十六进制表示
def debug_message(data: bytes, label: str):
    print(f"\n{label}:")
    print(f"Length: {len(data)} bytes")
    print(f"Hex: {data.hex()}")
    print(f"Raw: {data[:100]}...")  # 前100字节

# 使用
debug_message(request_data, "Request")
debug_message(response_data, "Response")
```

### 2. 账户状态跟踪

```python
# 在每次操作后打印账户状态
def debug_account(account: Account):
    print(f"\nAccount {account.account_number}:")
    print(f"  Name: {account.name}")
    print(f"  Balance: {account.balance} {account.currency.name}")
```

### 3. 网络通信日志

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/debug.log'),
        logging.StreamHandler()
    ]
)

# 使用
logging.debug(f"Received request from {client_addr}")
logging.info(f"Created account {account_number}")
logging.error(f"Failed to process request: {e}")
```

---

## 常见错误和解决方案

### 错误1：字节序不一致
**症状**：服务器解析出的数字和客户端发送的不一致

**解决**：
```python
# 错误：使用主机字节序
packed = struct.pack('I', value)  # ❌

# 正确：使用网络字节序
packed = struct.pack('!I', value)  # ✅
```

### 错误2：字符串编码问题
**症状**：中文乱码或解码失败

**解决**：
```python
# 明确使用UTF-8编码
text.encode('utf-8')
bytes_data.decode('utf-8')
```

### 错误3：UDP消息不完整
**症状**：recvfrom() 收到的数据不完整

**解决**：
```python
# 确保缓冲区足够大
data, addr = sock.recvfrom(2048)  # 而不是1024

# 或根据消息长度动态接收
header = sock.recvfrom(HEADER_SIZE)
payload_length = unpack_int(header)
payload = sock.recvfrom(payload_length)
```

### 错误4：超时设置影响监控
**症状**：监控期间正常请求也超时

**解决**：
```python
# 监控前保存原超时设置
original_timeout = sock.gettimeout()

# 监控期间使用长超时
sock.settimeout(monitor_duration + 5)

# 监控后恢复
sock.settimeout(original_timeout)
```

---

## 性能优化建议

### 1. 减少字符串拼接
```python
# 慢
result = ""
for item in items:
    result += str(item)

# 快
result = "".join(str(item) for item in items)
```

### 2. 使用字典而非if-elif链
```python
# 慢
if op == 1:
    return handle_open()
elif op == 2:
    return handle_close()
# ...

# 快
handlers = {
    1: handle_open,
    2: handle_close,
    # ...
}
return handlers[op]()
```

### 3. 缓存重复计算
```python
# 如果消息格式固定，可以预先计算偏移量
OFFSETS = {
    'request_id': 0,
    'operation': 4,
    'payload_length': 8,
    'payload': 12
}
```

---

## 提交前检查清单

```bash
# 1. 代码格式化
python -m black src/

# 2. 类型检查（可选）
python -m mypy src/

# 3. 运行所有测试
python -m pytest tests/ -v

# 4. 检查代码覆盖率
python -m pytest --cov=src tests/

# 5. 生成文档
python -m pydoc -w src/common/protocol
```

---

**开发指南版本**: v1.0  
**目标受众**: Claude Code Agent  
**最后更新**: 2026年1月