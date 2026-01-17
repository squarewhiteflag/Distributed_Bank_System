# 分布式银行系统 - 项目检查清单

## 快速验证

### 1. 运行测试

```bash
python -m unittest discover tests/
```

✅ **预期结果**: 24个测试全部通过
- test_marshaller: 9个测试
- test_account_manager: 15个测试

### 2. 运行演示脚本

```bash
./scripts/run_demo.sh
```

✅ **预期结果**:
- 显示"测试完成！"
- 所有测试通过

### 3. 启动服务器

```bash
python -m src.server.server --help
```

✅ **预期结果**: 显示帮助信息

### 4. 启动客户端

```bash
python -m src.client.client --help
```

✅ **预期结果**: 显示帮助信息

## 功能验证清单

### 核心服务（6个必需服务）

- [ ] **开户 (Open Account)**
  - [ ] 能创建新账户
  - [ ] 返回正确的账户号
  - [ ] 账户号自动递增
  - [ ] 支持不同货币类型

- [ ] **销户 (Close Account)**
  - [ ] 能删除账户
  - [ ] 验证密码
  - [ ] 验证账户所有权
  - [ ] 处理错误情况

- [ ] **存款 (Deposit)**
  - [ ] 能增加余额
  - [ ] 验证密码
  - [ ] 验证账户存在
  - [ ] 返回新余额

- [ ] **取款 (Withdraw)**
  - [ ] 能减少余额
  - [ ] 验证密码
  - [ ] 验证账户存在
  - [ ] 检查余额充足
  - [ ] 返回新余额

- [ ] **监控注册 (Monitor Registration)**
  - [ ] 能注册监控
  - [ ] 维护监控客户端列表
  - [ ] 支持多客户端同时监控

- [ ] **回调通知 (Callback Notification)**
  - [ ] 账户更新时自动通知
  - [ ] 向所有监控客户端发送
  - [ ] 自动过期清理

### 自定义操作（2个）

- [ ] **查询账户 (Query Account) - 幂等操作**
  - [ ] 返回完整账户信息
  - [ ] 验证密码
  - [ ] 重复执行不改变状态

- [ ] **转账 (Transfer) - 非幂等操作**
  - [ ] 能从A账户转账到B账户
  - [ ] 验证双方账户
  - [ ] 验证转出账户密码
  - [ ] 检查余额充足
  - [ ] 更新双方余额

### 调用语义

- [ ] **至少一次 (at-least-once)**
  - [ ] 客户端超时重传
  - [ ] 服务器直接处理所有请求
  - [ ] 非幂等操作可能重复执行

- [ ] **至多一次 (at-most-once)**
  - [ ] 客户端超时重传
  - [ ] 服务器检测重复请求
  - [ ] 重复请求返回历史结果
  - [ ] 所有操作正确执行

### 消息丢失模拟

- [ ] **可配置丢包率**
  - [ ] 支持0.0-1.0范围
  - [ ] 客户端丢包模拟
  - [ ] 服务器丢包模拟

## 技术要求验证

### 通信协议

- [x] 仅使用UDP（不使用TCP）
- [x] 自定义消息格式
- [x] 手动编解码

### 编解码实现

- [x] 整型：网络字节序
- [x] 浮点型：IEEE 754
- [x] 定长字符串：固定长度
- [x] 变长字符串：长度前缀+内容

### 禁止使用的特性

- [x] 不使用pickle
- [x] 不使用json（用于消息序列化）
- [x] 不使用RMI
- [x] 不使用RPC
- [x] 不使用CORBA
- [x] 不使用Java序列化

### 代码质量

- [x] 详细注释
- [x] 类型注解
- [x] 模块化设计
- [x] 错误处理
- [x] 单元测试

## 文档完整性

- [x] **README.md**
  - [x] 项目概述
  - [x] 功能特性
  - [x] 安装运行说明
  - [x] 使用示例

- [x] **协议规范文档**
  - [x] 消息格式定义
  - [x] 编解码规则
  - [x] 操作类型定义
  - [x] 字节序列示例

- [x] **用户手册**
  - [x] 快速入门
  - [x] 功能详解
  - [x] 实验指导
  - [x] 常见问题

- [x] **代码注释**
  - [x] 模块文档字符串
  - [x] 类文档字符串
  - [x] 函数文档字符串
  - [x] 关键代码注释

## 实验准备

### 场景1：基本银行操作

```bash
# 服务器
python -m src.server.server --port 5000

# 客户端
python -m src.client.client --server-host localhost
```

测试流程：
1. [ ] 开户
2. [ ] 存款
3. [ ] 取款
4. [ ] 查询
5. [ ] 销户

### 场景2：监控回调

```bash
# 服务器
python -m src.server.server --port 5000

# 客户端1（监控）
python -m src.client.client --server-host localhost
# 选择：7

# 客户端2（操作）
python -m src.client.client --server-host localhost
# 执行各种操作
```

验证：
- [ ] 客户端1收到更新通知
- [ ] 显示正确的账户信息

### 场景3：调用语义对比

#### 实验1：至少一次语义

```bash
# 服务器
python -m src.server.server --port 5000 \
  --semantics at-least-once --loss-rate 0.3

# 客户端
python -m src.client.client --server-host localhost \
  --semantics at-least-once --loss-rate 0.2
```

测试：
1. [ ] 开户A（余额1000）
2. [ ] 开户B
3. [ ] 转账：A → B 100
4. [ ] 观察余额
   - [ ] 可能出现：A余额=700（被扣3次）

#### 实验2：至多一次语义

```bash
# 服务器
python -m src.server.server --port 5000 \
  --semantics at-most-once --loss-rate 0.3

# 客户端
python -m src.client.client --server-host localhost \
  --semantics at-most-once --loss-rate 0.2
```

测试：
1. [ ] 执行相同操作
2. [ ] 观察余额
   - [ ] A余额=900（正确）

## 演示准备检查

- [ ] 准备至少两台电脑（或使用虚拟机）
- [ ] 测试网络连通性
- [ ] 准备演示脚本
- [ ] 准备测试数据
- [ ] 运行所有测试确保正常
- [ ] 准备演示流程说明

## 提交前检查

### 代码

- [x] 所有文件有详细注释
- [x] 没有使用禁止的库
- [x] 代码风格统一
- [x] 所有TODO已完成

### 测试

- [x] 单元测试通过
- [x] 功能测试通过
- [x] 集成测试通过

### 文档

- [x] README完整
- [x] 协议规范详细
- [x] 用户手册清晰
- [x] 实验报告准备

### 演示

- [ ] 多台电脑可用
- [ ] 网络测试通过
- [ ] 演示脚本准备
- [ ] 测试数据准备

## 快速命令参考

### 测试

```bash
# 运行所有测试
python -m unittest discover tests/

# 运行特定测试
python -m unittest tests.test_marshaller
python -m unittest tests.test_account_manager
```

### 启动服务器

```bash
# 默认配置
python -m src.server.server

# 自定义配置
python -m src.server.server --host 0.0.0.0 --port 5000 \
  --semantics at-most-once --loss-rate 0.2 --verbose

# 使用脚本
./scripts/run_server.sh
```

### 启动客户端

```bash
# 默认配置
python -m src.client.client --server-host localhost

# 自定义配置
python -m src.client.client --server-host 192.168.1.100 \
  --server-port 5000 --semantics at-most-once --loss-rate 0.1

# 使用脚本
./scripts/run_client.sh localhost
```

### 实验命令

```bash
# 至少一次语义实验
python -m src.server.server --semantics at-least-once --loss-rate 0.3
python -m src.client.client --server-host localhost --semantics at-least-once --loss-rate 0.2

# 至多一次语义实验
python -m src.server.server --semantics at-most-once --loss-rate 0.3
python -m src.client.client --server-host localhost --semantics at-most-once --loss-rate 0.2
```

---

**检查清单版本**: 1.0
**最后更新**: 2026年1月17日
