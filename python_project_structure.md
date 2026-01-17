# 分布式银行系统 Python 项目架构

## 项目目录结构

```
distributed-banking-system/
│
├── README.md                          # 项目说明文档
├── requirements.txt                   # Python依赖（本项目仅需标准库）
├── .gitignore                        # Git忽略文件
│
├── docs/                             # 文档目录
│   ├── project_requirements.md       # 项目需求文档
│   ├── design_document.md            # 系统设计文档
│   ├── protocol_specification.md     # 消息协议规范
│   ├── experiment_report.md          # 实验报告
│   └── user_manual.md                # 用户手册
│
├── src/                              # 源代码目录
│   ├── __init__.py
│   │
│   ├── common/                       # 公共模块（成员B负责）
│   │   ├── __init__.py
│   │   ├── protocol.py               # 消息协议定义
│   │   ├── marshaller.py             # 编解码工具
│   │   └── constants.py              # 常量定义
│   │
│   ├── server/                       # 服务器模块（成员A负责）
│   │   ├── __init__.py
│   │   ├── server.py                 # 服务器主程序
│   │   ├── account_manager.py        # 账户管理
│   │   ├── service_handler.py        # 服务处理逻辑
│   │   ├── monitor_manager.py        # 监控客户端管理
│   │   └── operations.py             # 自定义操作（非幂等）
│   │
│   ├── client/                       # 客户端模块（成员D负责）
│   │   ├── __init__.py
│   │   ├── client.py                 # 客户端主程序
│   │   ├── ui.py                     # 用户界面
│   │   ├── monitor.py                # 监控接收逻辑
│   │   └── operations.py             # 自定义操作（幂等）
│   │
│   └── semantics/                    # 调用语义模块（成员C负责）
│       ├── __init__.py
│       ├── at_least_once.py          # 至少一次语义
│       ├── at_most_once.py           # 至多一次语义
│       ├── request_history.py        # 请求历史管理
│       └── message_loss_simulator.py # 消息丢失模拟
│
├── tests/                            # 测试目录
│   ├── __init__.py
│   ├── test_marshaller.py            # 编解码测试
│   ├── test_account_manager.py       # 账户管理测试
│   ├── test_semantics.py             # 调用语义测试
│   └── integration_test.py           # 集成测试
│
├── scripts/                          # 脚本目录
│   ├── run_server.sh                 # 启动服务器脚本
│   ├── run_client.sh                 # 启动客户端脚本
│   ├── run_demo.sh                   # 演示脚本
│   └── experiments/                  # 实验脚本
│       ├── experiment_at_least_once.py
│       └── experiment_at_most_once.py
│
├── logs/                             # 日志目录
│   ├── server.log
│   └── client.log
│
└── data/                             # 数据目录（可选）
    └── accounts.json                 # 账户数据（可选持久化）
```

---

## 核心模块详细说明

### 1. common/protocol.py - 消息协议定义

**负责人：成员B**

```python
"""
消息协议定义模块
定义所有操作类型、消息格式和编码规则
"""

from enum import IntEnum

class OperationType(IntEnum):
    """操作类型枚举"""
    OPEN_ACCOUNT = 1      # 开户
    CLOSE_ACCOUNT = 2     # 销户
    DEPOSIT = 3           # 存款
    WITHDRAW = 4          # 取款
    MONITOR_REGISTER = 5  # 注册监控
    MONITOR_CALLBACK = 6  # 监控回调
    QUERY_ACCOUNT = 7     # 查询账户（幂等操作示例）
    TRANSFER = 8          # 转账（非幂等操作示例）

class CurrencyType(IntEnum):
    """货币类型枚举"""
    USD = 1
    EUR = 2
    SGD = 3
    CNY = 4

class ResponseStatus(IntEnum):
    """响应状态码"""
    SUCCESS = 0
    ERROR_INVALID_PASSWORD = 1
    ERROR_ACCOUNT_NOT_FOUND = 2
    ERROR_INSUFFICIENT_BALANCE = 3
    ERROR_ACCOUNT_NOT_OWNED = 4
    ERROR_DUPLICATE_REQUEST = 5
    ERROR_UNKNOWN = 99

# 消息格式常量
HEADER_SIZE = 12  # Request ID (4) + Operation Type (4) + Payload Length (4)
MAX_NAME_LENGTH = 64
PASSWORD_LENGTH = 16
MAX_MESSAGE_SIZE = 1024
```

### 2. common/marshaller.py - 编解码工具

**负责人：成员B**

```python
"""
消息编解码模块
手动实现所有数据类型的序列化和反序列化
禁止使用pickle、json等高级序列化工具
"""

import struct

class Marshaller:
    """消息编解码器"""
    
    @staticmethod
    def pack_int(value: int) -> bytes:
        """打包整型（网络字节序）"""
        return struct.pack('!I', value)
    
    @staticmethod
    def unpack_int(data: bytes, offset: int = 0) -> tuple:
        """解包整型，返回(值, 新偏移量)"""
        value = struct.unpack('!I', data[offset:offset+4])[0]
        return value, offset + 4
    
    @staticmethod
    def pack_float(value: float) -> bytes:
        """打包浮点型"""
        return struct.pack('!f', value)
    
    @staticmethod
    def unpack_float(data: bytes, offset: int = 0) -> tuple:
        """解包浮点型，返回(值, 新偏移量)"""
        value = struct.unpack('!f', data[offset:offset+4])[0]
        return value, offset + 4
    
    @staticmethod
    def pack_string(value: str, fixed_length: int = None) -> bytes:
        """
        打包字符串
        如果指定fixed_length，则为定长字符串
        否则为变长字符串（4字节长度 + 实际内容）
        """
        encoded = value.encode('utf-8')
        if fixed_length:
            # 定长字符串
            return encoded.ljust(fixed_length, b'\x00')[:fixed_length]
        else:
            # 变长字符串：长度前缀 + 内容
            length = len(encoded)
            return struct.pack('!I', length) + encoded
    
    @staticmethod
    def unpack_string(data: bytes, offset: int = 0, fixed_length: int = None) -> tuple:
        """
        解包字符串，返回(字符串, 新偏移量)
        """
        if fixed_length:
            # 定长字符串
            raw = data[offset:offset+fixed_length]
            value = raw.rstrip(b'\x00').decode('utf-8')
            return value, offset + fixed_length
        else:
            # 变长字符串
            length = struct.unpack('!I', data[offset:offset+4])[0]
            offset += 4
            value = data[offset:offset+length].decode('utf-8')
            return value, offset + length

# 请求消息构建器
class RequestBuilder:
    """请求消息构建器"""
    
    def __init__(self, request_id: int, operation: int):
        self.request_id = request_id
        self.operation = operation
        self.payload = b''
    
    def add_int(self, value: int):
        self.payload += Marshaller.pack_int(value)
        return self
    
    def add_float(self, value: float):
        self.payload += Marshaller.pack_float(value)
        return self
    
    def add_string(self, value: str, fixed_length: int = None):
        self.payload += Marshaller.pack_string(value, fixed_length)
        return self
    
    def build(self) -> bytes:
        """构建完整消息"""
        header = (
            Marshaller.pack_int(self.request_id) +
            Marshaller.pack_int(self.operation) +
            Marshaller.pack_int(len(self.payload))
        )
        return header + self.payload

# 响应消息构建器
class ResponseBuilder:
    """响应消息构建器"""
    
    def __init__(self, request_id: int, status: int):
        self.request_id = request_id
        self.status = status
        self.payload = b''
    
    def add_int(self, value: int):
        self.payload += Marshaller.pack_int(value)
        return self
    
    def add_float(self, value: float):
        self.payload += Marshaller.pack_float(value)
        return self
    
    def add_string(self, value: str, fixed_length: int = None):
        self.payload += Marshaller.pack_string(value, fixed_length)
        return self
    
    def build(self) -> bytes:
        """构建完整响应"""
        header = (
            Marshaller.pack_int(self.request_id) +
            Marshaller.pack_int(self.status) +
            Marshaller.pack_int(len(self.payload))
        )
        return header + self.payload
```

### 3. server/account_manager.py - 账户管理

**负责人：成员A**

```python
"""
账户管理模块
负责账户数据的创建、查询、更新和删除
"""

from dataclasses import dataclass
from typing import Optional, Dict
from common.protocol import CurrencyType

@dataclass
class Account:
    """账户数据类"""
    account_number: int
    name: str
    password: str  # 实际应用中应该加密存储
    currency: CurrencyType
    balance: float

class AccountManager:
    """账户管理器"""
    
    def __init__(self):
        self.accounts: Dict[int, Account] = {}
        self.next_account_number = 10001  # 起始账户号
    
    def create_account(self, name: str, password: str, 
                      currency: CurrencyType, initial_balance: float) -> int:
        """创建新账户，返回账户号"""
        account_number = self.next_account_number
        self.next_account_number += 1
        
        account = Account(
            account_number=account_number,
            name=name,
            password=password,
            currency=currency,
            balance=initial_balance
        )
        
        self.accounts[account_number] = account
        return account_number
    
    def close_account(self, account_number: int, name: str, password: str) -> bool:
        """关闭账户"""
        account = self.accounts.get(account_number)
        if not account:
            raise ValueError("Account not found")
        if account.name != name:
            raise ValueError("Account not owned by this user")
        if account.password != password:
            raise ValueError("Invalid password")
        
        del self.accounts[account_number]
        return True
    
    def deposit(self, account_number: int, password: str, amount: float) -> float:
        """存款，返回新余额"""
        account = self.accounts.get(account_number)
        if not account:
            raise ValueError("Account not found")
        if account.password != password:
            raise ValueError("Invalid password")
        
        account.balance += amount
        return account.balance
    
    def withdraw(self, account_number: int, password: str, amount: float) -> float:
        """取款，返回新余额"""
        account = self.accounts.get(account_number)
        if not account:
            raise ValueError("Account not found")
        if account.password != password:
            raise ValueError("Invalid password")
        if account.balance < amount:
            raise ValueError("Insufficient balance")
        
        account.balance -= amount
        return account.balance
    
    def get_account(self, account_number: int) -> Optional[Account]:
        """获取账户信息"""
        return self.accounts.get(account_number)
    
    def verify_password(self, account_number: int, password: str) -> bool:
        """验证密码"""
        account = self.accounts.get(account_number)
        return account and account.password == password
```

### 4. semantics/at_most_once.py - 至多一次语义

**负责人：成员C**

```python
"""
至多一次调用语义实现
通过请求历史表检测重复请求
"""

from typing import Optional, Dict, Tuple
import time

class RequestHistory:
    """请求历史记录"""
    
    def __init__(self, max_age_seconds: int = 300):
        """
        初始化请求历史
        max_age_seconds: 历史记录最大保留时间（秒）
        """
        # 格式: {request_id: (response_data, timestamp)}
        self.history: Dict[int, Tuple[bytes, float]] = {}
        self.max_age = max_age_seconds
    
    def is_duplicate(self, request_id: int) -> bool:
        """检查是否为重复请求"""
        return request_id in self.history
    
    def get_cached_response(self, request_id: int) -> Optional[bytes]:
        """获取缓存的响应"""
        if request_id in self.history:
            return self.history[request_id][0]
        return None
    
    def record_request(self, request_id: int, response: bytes):
        """记录请求和响应"""
        self.history[request_id] = (response, time.time())
    
    def cleanup_old_records(self):
        """清理过期记录"""
        current_time = time.time()
        expired_keys = [
            req_id for req_id, (_, timestamp) in self.history.items()
            if current_time - timestamp > self.max_age
        ]
        for key in expired_keys:
            del self.history[key]
```

### 5. client/ui.py - 客户端界面

**负责人：成员D**

```python
"""
客户端用户界面
提供命令行交互菜单
"""

class ClientUI:
    """客户端用户界面"""
    
    @staticmethod
    def display_menu():
        """显示主菜单"""
        print("\n" + "="*50)
        print("Distributed Banking System - Client")
        print("="*50)
        print("1. Open Account")
        print("2. Close Account")
        print("3. Deposit")
        print("4. Withdraw")
        print("5. Query Account (Idempotent)")
        print("6. Transfer (Non-idempotent)")
        print("7. Monitor Account Updates")
        print("0. Exit")
        print("="*50)
    
    @staticmethod
    def get_user_choice() -> int:
        """获取用户选择"""
        try:
            choice = int(input("Enter your choice: "))
            return choice
        except ValueError:
            return -1
    
    @staticmethod
    def get_open_account_info():
        """获取开户信息"""
        print("\n--- Open New Account ---")
        name = input("Enter your name: ")
        password = input("Enter password (16 chars): ").ljust(16)[:16]
        
        print("Currency types: 1=USD, 2=EUR, 3=SGD, 4=CNY")
        currency = int(input("Enter currency type: "))
        
        initial_balance = float(input("Enter initial balance: "))
        
        return name, password, currency, initial_balance
    
    @staticmethod
    def get_close_account_info():
        """获取销户信息"""
        print("\n--- Close Account ---")
        name = input("Enter your name: ")
        account_number = int(input("Enter account number: "))
        password = input("Enter password: ").ljust(16)[:16]
        
        return name, account_number, password
    
    # ... 其他输入方法
```

---

## 开发规范文档

### Python 编码规范

```python
# 1. 使用类型注解
def pack_message(request_id: int, operation: int, payload: bytes) -> bytes:
    pass

# 2. 详细的文档字符串
def create_account(name: str, password: str) -> int:
    """
    创建新账户
    
    Args:
        name: 账户持有人姓名
        password: 账户密码（16字符定长）
    
    Returns:
        int: 新创建的账户号
    
    Raises:
        ValueError: 如果参数无效
    """
    pass

# 3. 使用常量而非魔法数字
HEADER_SIZE = 12
MAX_RETRIES = 3
TIMEOUT_SECONDS = 5

# 4. 合理的错误处理
try:
    response = send_request(request)
except socket.timeout:
    print("Request timeout, retrying...")
except Exception as e:
    logging.error(f"Unexpected error: {e}")
```

### 禁止使用的Python特性

```python
# ❌ 禁止使用高级序列化
import pickle  # 不允许
import json    # 不允许用于消息序列化

# ❌ 禁止使用流式对象
from io import BytesIO  # 不允许用于网络消息

# ✅ 只允许使用
import socket  # UDP socket
import struct  # 字节序转换
```

---

## 配置文件示例

### config.yaml (可选)

```yaml
# 服务器配置
server:
  host: "0.0.0.0"
  port: 5000
  max_message_size: 1024
  
# 调用语义配置
semantics:
  type: "at-most-once"  # 或 "at-least-once"
  timeout_seconds: 5
  max_retries: 3
  request_history_max_age: 300

# 消息丢失模拟
simulation:
  enabled: true
  loss_rate: 0.2  # 20% 丢包率

# 日志配置
logging:
  level: "INFO"
  file: "logs/server.log"
```

---

## 命令行参数设计

### 服务器启动

```bash
python -m src.server.server \
  --host 0.0.0.0 \
  --port 5000 \
  --semantics at-most-once \
  --loss-rate 0.2 \
  --verbose
```

### 客户端启动

```bash
python -m src.client.client \
  --server-host 192.168.1.100 \
  --server-port 5000 \
  --semantics at-most-once \
  --loss-rate 0.1
```

---

## Git工作流建议

### 分支策略

```
main              # 主分支（稳定版本）
├── develop       # 开发分支
│   ├── feature/member-a-server-core
│   ├── feature/member-b-protocol
│   ├── feature/member-c-semantics
│   └── feature/member-d-client
```

### 提交信息规范

```
feat: 添加账户管理模块
fix: 修复消息解码bug
docs: 更新协议规范文档
test: 添加编解码单元测试
refactor: 重构请求历史管理
```

---

## 开发检查清单

### 成员A检查清单
- [ ] 服务器UDP socket创建和绑定
- [ ] 账户数据结构完整
- [ ] 4个基本操作正确实现
- [ ] 监控客户端列表维护
- [ ] 回调触发逻辑正确
- [ ] 自定义非幂等操作实现

### 成员B检查清单
- [ ] 所有操作类型定义
- [ ] 整型、浮点、字符串编解码正确
- [ ] 请求/响应消息构建器完整
- [ ] 消息格式文档详细
- [ ] 跨平台字节序兼容

### 成员C检查清单
- [ ] 至少一次语义：超时重传
- [ ] 至多一次语义：重复检测
- [ ] 请求历史表管理
- [ ] 消息丢失模拟开关
- [ ] 实验脚本完整
- [ ] 实验结果分析

### 成员D检查清单
- [ ] 命令行菜单系统
- [ ] 所有操作的用户输入
- [ ] 监控注册流程
- [ ] 回调接收和显示
- [ ] 自定义幂等操作实现
- [ ] 用户手册完整

---

## 测试策略

### 单元测试示例

```python
# tests/test_marshaller.py
import unittest
from src.common.marshaller import Marshaller

class TestMarshaller(unittest.TestCase):
    
    def test_pack_unpack_int(self):
        original = 12345
        packed = Marshaller.pack_int(original)
        unpacked, _ = Marshaller.unpack_int(packed)
        self.assertEqual(original, unpacked)
    
    def test_pack_unpack_string(self):
        original = "Hello, 世界"
        packed = Marshaller.pack_string(original)
        unpacked, _ = Marshaller.unpack_string(packed)
        self.assertEqual(original, unpacked)
```

### 集成测试脚本

```python
# tests/integration_test.py
"""
集成测试：启动服务器和客户端，执行完整流程
"""

import subprocess
import time
import unittest

class IntegrationTest(unittest.TestCase):
    
    def setUp(self):
        # 启动服务器
        self.server_process = subprocess.Popen([
            'python', '-m', 'src.server.server',
            '--port', '5001'
        ])
        time.sleep(1)  # 等待服务器启动
    
    def tearDown(self):
        self.server_process.terminate()
    
    def test_full_workflow(self):
        # 运行客户端测试脚本
        result = subprocess.run([
            'python', '-m', 'src.client.client',
            '--server-port', '5001',
            '--test-mode'
        ])
        self.assertEqual(result.returncode, 0)
```

---

## 演示准备

### 演示场景1：基本银行操作

```bash
# 终端1：启动服务器
python -m src.server.server --port 5000 --semantics at-most-once

# 终端2：客户端执行操作
python -m src.client.client --server-port 5000
# 依次执行：开户 -> 存款 -> 取款 -> 查询 -> 销户
```

### 演示场景2：监控回调

```bash
# 终端1：服务器
python -m src.server.server --port 5000

# 终端2：监控客户端
python -m src.client.client --server-port 5000
# 选择：7. Monitor Account Updates (60秒)

# 终端3：操作客户端
python -m src.client.client --server-port 5000
# 执行开户、存款等操作，观察终端2实时显示
```

### 演示场景3：调用语义对比

```bash
# 实验1：至少一次语义 + 消息丢失
python scripts/experiments/experiment_at_least_once.py

# 实验2：至多一次语义 + 消息丢失
python scripts/experiments/experiment_at_most_once.py
```

---

## 常见问题 FAQ

### Q1: Python的struct模块够用吗？
**A**: 完全够用。`struct.pack()` 和 `struct.unpack()` 相当于C的 `htonl()`/`ntohl()`，满足手动编解码要求。

### Q2: 如何实现超时重传？
**A**: 使用 `socket.settimeout(seconds)` 设置超时，捕获 `socket.timeout` 异常后重传。

### Q3: 如何获取客户端地址？
**A**: 服务器端使用 `data, addr = sock.recvfrom(1024)` 时，`addr` 包含客户端的IP和端口。

### Q4: 需要处理并发吗？
**A**: 不需要多线程。服务器顺序处理请求即可，但需维护监控客户端列表（用普通字典）。

---

## 提交前最终检查

### 代码检查
- [ ] 所有文件都有详细注释
- [ ] 没有使用禁止的库（pickle、json序列化、RMI等）
- [ ] 代码风格统一（推荐使用black格式化）
- [ ] 所有TODO都已完成

### 文档检查
- [ ] README.md 包含编译运行说明
- [ ] 设计文档完整
- [ ] 协议规范清晰
- [ ] 实验报告包含截图和分析

### 功能检查
- [ ] 6个必需服务全部实现
- [ ] 2个自定义操作实现
- [ ] 两种调用语义都能切换
- [ ] 消息丢失模拟工作正常
- [ ] 监控回调功能正常

### 演示准备
- [ ] 至少两台电脑可用
- [ ] 网络连通性测试通过
- [ ] 演示脚本准备完成
- [ ] 测试数据准备完成

---

## 附录：Python Socket 快速参考

```python
import socket

# 创建UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 服务器：绑定地址
sock.bind(('0.0.0.0', 5000))

# 服务器：接收数据
data, client_addr = sock.recvfrom(1024)  # client_addr是(ip, port)元组

# 服务器：发送回复
sock.sendto(response_data, client_addr)

# 客户端：发送请求
sock.sendto(request_data, ('192.168.1.100', 5000))

# 客户端：接收回复（带超时）
sock.settimeout(5.0)  # 5秒超时
try:
    data, server_addr = sock.recvfrom(1024)
except socket.timeout:
    print("Timeout! Retrying...")

# 关闭socket
sock.close()
```

---

**项目架构版本**: v1.0  
**适用于**: Python 3.8+  
**最后更新**: 2026年1月