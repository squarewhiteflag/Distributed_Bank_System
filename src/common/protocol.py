"""
消息协议定义模块
定义所有操作类型、消息格式和编码规则
"""

from enum import IntEnum


class OperationType(IntEnum):
    """操作类型枚举"""
    # 必需服务 (6个)
    OPEN_ACCOUNT = 1          # 开户
    CLOSE_ACCOUNT = 2         # 销户
    DEPOSIT = 3               # 存款
    WITHDRAW = 4              # 取款
    MONITOR_REGISTER = 5      # 注册监控
    MONITOR_CALLBACK = 6      # 监控回调

    # 自定义操作 (2个)
    QUERY_ACCOUNT = 7         # 查询账户（幂等操作示例）
    TRANSFER = 8              # 转账（非幂等操作示例）


class CurrencyType(IntEnum):
    """货币类型枚举"""
    USD = 1  # 美元
    EUR = 2  # 欧元
    SGD = 3  # 新加坡元
    CNY = 4  # 人民币


class ResponseStatus(IntEnum):
    """响应状态码"""
    SUCCESS = 0
    ERROR_INVALID_PASSWORD = 1
    ERROR_ACCOUNT_NOT_FOUND = 2
    ERROR_INSUFFICIENT_BALANCE = 3
    ERROR_ACCOUNT_NOT_OWNED = 4
    ERROR_INVALID_OPERATION = 5
    ERROR_DUPLICATE_REQUEST = 6
    ERROR_UNKNOWN = 99
