# 分布式银行系统 - 消息协议规范

## 1. 概述

本文档详细描述了分布式银行系统中使用的消息协议格式和编码规则。所有消息通过UDP传输，使用自定义的二进制格式进行编解码。

## 2. 消息结构

### 2.1 通用消息头

所有消息（请求和响应）都使用以下通用格式：

```
+---------------------+
| Request ID (4 bytes)   |
+---------------------+
| Type/Status (4 bytes)  |
+---------------------+
| Payload Length (4 bytes)|
+---------------------+
| Payload (variable)     |
+---------------------+
```

- **Request ID**：4字节无符号整数，用于唯一标识请求和检测重复
- **Type/Status**：
  - 请求消息：操作类型（4字节无符号整数）
  - 响应消息：状态码（4字节无符号整数）
- **Payload Length**：4字节无符号整数，表示payload的字节长度
- **Payload**：变长数据，具体格式取决于操作类型

### 2.2 字节序

所有多字节整数（整型、浮点型）使用**网络字节序**（大端序，Big-Endian）。
- Python: 使用`struct.pack('!I')`和`struct.pack('!f')`
- C: 使用`htonl()`和`ntohl()`

## 3. 数据类型编码

### 3.1 整型 (Integer)

**编码**：4字节无符号整数，网络字节序

```
值: 12345
编码: 00 00 30 39
```

### 3.2 浮点型 (Float)

**编码**：4字节IEEE 754单精度浮点数，网络字节序

```
值: 1234.56
编码: 44 9A 52 2B
```

### 3.3 定长字符串 (Fixed-Length String)

**编码**：固定长度的UTF-8编码字符串，不足部分用`0x00`填充

```
值: "password" (固定长度16)
编码: 70 61 73 73 77 6F 72 64 00 00 00 00 00 00 00 00
```

### 3.4 变长字符串 (Variable-Length String)

**编码**：4字节长度前缀 + UTF-8编码字符串内容

```
值: "Alice"
编码: 00 00 00 05 41 6C 69 63 65
       |--------| |----------|
       长度(5)    内容
```

## 4. 操作类型定义

| 操作码 | 操作名称 | 操作类型 |
|--------|----------|----------|
| 1 | OPEN_ACCOUNT | 开户 |
| 2 | CLOSE_ACCOUNT | 销户 |
| 3 | DEPOSIT | 存款 |
| 4 | WITHDRAW | 取款 |
| 5 | MONITOR_REGISTER | 监控注册 |
| 6 | MONITOR_CALLBACK | 监控回调 |
| 7 | QUERY_ACCOUNT | 查询账户（幂等） |
| 8 | TRANSFER | 转账（非幂等） |

## 5. 状态码定义

| 状态码 | 名称 | 含义 |
|--------|------|------|
| 0 | SUCCESS | 操作成功 |
| 1 | ERROR_INVALID_PASSWORD | 密码错误 |
| 2 | ERROR_ACCOUNT_NOT_FOUND | 账户不存在 |
| 3 | ERROR_INSUFFICIENT_BALANCE | 余额不足 |
| 4 | ERROR_ACCOUNT_NOT_OWNED | 账户不属于该用户 |
| 5 | ERROR_INVALID_OPERATION | 无效操作 |
| 6 | ERROR_DUPLICATE_REQUEST | 重复请求 |
| 99 | ERROR_UNKNOWN | 未知错误 |

## 6. 请求消息格式

### 6.1 开户请求 (OPEN_ACCOUNT)

**操作码**: 1

**Payload格式**:
```
+------------------+
| Name (变长字符串)   |
+------------------+
| Password (定长16字节)|
+------------------+
| Currency (4字节整数)|
+------------------+
| Balance (4字节浮点)|
+------------------+
```

**示例**:
```
Name: "Alice"
Password: "pass123"
Currency: 1 (USD)
Balance: 1000.0

完整消息 (字节序列):
[Header: RequestID=1, Op=1, Len=...]
41 6C 69 63 65                          # Name (5字节) "Alice"
00 00 00 05                              # Name长度
70 61 73 73 31 32 33 00 00 00 00 00 00 00 00  # Password (16字节)
00 00 00 01                              # Currency = 1
44 7A 00 00                              # Balance = 1000.0 (浮点)
```

### 6.2 销户请求 (CLOSE_ACCOUNT)

**操作码**: 2

**Payload格式**:
```
+------------------+
| Name (变长字符串)   |
+------------------+
| Account Number (4字节整数)|
+------------------+
| Password (定长16字节)|
+------------------+
```

### 6.3 存款请求 (DEPOSIT)

**操作码**: 3

**Payload格式**:
```
+------------------+
| Name (变长字符串)   |
+------------------+
| Account Number (4字节整数)|
+------------------+
| Password (定长16字节)|
+------------------+
| Currency (4字节整数)|
+------------------+
| Amount (4字节浮点)|
+------------------+
```

### 6.4 取款请求 (WITHDRAW)

**操作码**: 4

**Payload格式**: 同存款请求

### 6.5 监控注册请求 (MONITOR_REGISTER)

**操作码**: 5

**Payload格式**:
```
+---------------------+
| Duration (4字节整数)  |  监控时长（秒）
+---------------------+
```

### 6.6 查询账户请求 (QUERY_ACCOUNT)

**操作码**: 7

**Payload格式**:
```
+------------------+
| Account Number (4字节整数)|
+------------------+
| Password (定长16字节)|
+------------------+
```

### 6.7 转账请求 (TRANSFER)

**操作码**: 8

**Payload格式**:
```
+-----------------------+
| From Account (4字节整数)|
+-----------------------+
| Password (定长16字节)   |
+-----------------------+
| To Account (4字节整数) |
+-----------------------+
| Amount (4字节浮点)     |
+-----------------------+
```

## 7. 响应消息格式

### 7.1 通用响应格式

**Response Header**:
```
+---------------------+
| Request ID (4字节)   |  对应的请求ID
+---------------------+
| Status (4字节)       |  状态码
+---------------------+
| Payload Length (4字节)|
+---------------------+
| Payload (variable)   |
+---------------------+
```

### 7.2 开户响应

**成功时 (Status=0)**:
```
+------------------+
| Account Number (4字节整数)|
+------------------+
```

**失败时 (Status!=0)**:
```
无Payload
```

### 7.3 存款/取款响应

**成功时 (Status=0)**:
```
+------------------+
| New Balance (4字节浮点)|
+------------------+
```

### 7.4 查询账户响应

**成功时 (Status=0)**:
```
+------------------+
| Account Number (4字节整数)|
+------------------+
| Name (变长字符串)   |
+------------------+
| Currency (4字节整数)|
+------------------+
| Balance (4字节浮点)|
+------------------+
```

### 7.5 转账响应

**成功时 (Status=0)**:
```
+------------------+
| New Balance of Source Account (4字节浮点)|
+------------------+
```

## 8. 监控回调消息格式

### 8.1 回调通知 (MONITOR_CALLBACK)

**操作码**: 6

**Payload格式**:
```
+------------------+
| Account Number (4字节整数)|
+------------------+
| Name (变长字符串)   |
+------------------+
| Currency (4字节整数)|
+------------------+
| Balance (4字节浮点)|
+------------------+
```

**注意**: 回调消息的Request ID设置为0，因为回调不是客户端请求的响应。

## 9. 消息大小限制

- **最大消息大小**: 1024字节
- **建议payload大小**: < 512字节（为消息头留出空间）
- **最大字符串长度**: 64字节（姓名）

## 10. 编解码示例

### 10.1 Python编解码示例

```python
import struct

# 编码整型
def pack_int(value):
    return struct.pack('!I', value)

# 解码整型
def unpack_int(data, offset=0):
    return struct.unpack('!I', data[offset:offset+4])[0]

# 编码变长字符串
def pack_string(value):
    encoded = value.encode('utf-8')
    length = len(encoded)
    return struct.pack('!I', length) + encoded

# 解码变长字符串
def unpack_string(data, offset=0):
    length = struct.unpack('!I', data[offset:offset+4])[0]
    offset += 4
    value = data[offset:offset+length].decode('utf-8')
    return value, offset + length
```

### 10.2 完整消息示例

**开户请求示例**:
```python
# 构建请求
request_id = 1
operation = 1  # OPEN_ACCOUNT
name = "Alice"
password = "pass123".ljust(16, '\x00')
currency = 1  # USD
balance = 1000.0

# 编码
payload = (
    pack_string(name) +
    password.encode('utf-8') +
    pack_int(currency) +
    struct.pack('!f', balance)
)

header = pack_int(request_id) + pack_int(operation) + pack_int(len(payload))
request = header + payload
```

## 11. 错误处理

### 11.1 客户端错误处理

- 超时未收到响应：重传（最多3次）
- 收到错误响应：根据状态码显示相应错误信息
- 网络错误：显示连接错误并退出

### 11.2 服务器错误处理

- 解析请求失败：返回ERROR_UNKNOWN
- 操作失败：返回对应的状态码
- 重复请求（at-most-once语义）：返回历史响应

## 12. 安全考虑

### 12.1 密码传输

- 密码以明文形式传输（本项目为教学项目，未实现加密）
- 实际应用中应使用加密传输（如TLS）

### 12.2 输入验证

- 服务器应验证所有输入参数的合法性
- 字符串长度应限制在合理范围内
- 数值范围应进行检查

## 附录A：货币类型编码

| 值 | 货币 |
|----|------|
| 1 | USD (美元) |
| 2 | EUR (欧元) |
| 3 | SGD (新加坡元) |
| 4 | CNY (人民币) |

## 附录B：典型操作的字节序列示例

### 示例1：开户请求完整字节序列

```
Header:
00 00 00 01    # Request ID = 1
00 00 00 01    # Operation = OPEN_ACCOUNT
00 00 00 1D    # Payload Length = 29

Payload:
00 00 00 05    # Name length = 5
41 6C 69 63 65 # Name = "Alice"
70 61 73 73 31 32 33 00 00 00 00 00 00 00 00  # Password = "pass123"
00 00 00 01    # Currency = 1 (USD)
44 7A 00 00    # Balance = 1000.0

总长度: 12 + 29 = 41字节
```

---

**文档版本**: 1.0
**最后更新**: 2026年1月
