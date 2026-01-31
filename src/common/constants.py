"""
常量定义模块
定义系统中使用的所有常量
"""

# 消息格式常量
HEADER_SIZE = 12  # Request ID (4) + Operation Type (4) + Payload Length (4)
MAX_MESSAGE_SIZE = 1024  # UDP最大消息大小

# 字符串长度限制
MAX_NAME_LENGTH = 64
PASSWORD_LENGTH = 16

# 网络配置
DEFAULT_SERVER_HOST = "0.0.0.0"
DEFAULT_SERVER_PORT = 5000
DEFAULT_CLIENT_TIMEOUT = 5.0  # 秒
MAX_RETRIES = 5

# 调用语义类型
SEMANTICS_AT_LEAST_ONCE = "at-least-once"
SEMANTICS_AT_MOST_ONCE = "at-most-once"

# 请求历史配置
REQUEST_HISTORY_MAX_AGE = 300  # 5分钟（秒）

# 监控配置
MIN_MONITOR_DURATION = 10  # 最小监控时长（秒）
MAX_MONITOR_DURATION = 300  # 最大监控时长（秒）

# 账户配置
INITIAL_ACCOUNT_NUMBER = 10001  # 起始账户号
