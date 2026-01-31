"""
请求历史管理模块
用于至多一次（at-most-once）调用语义的重复请求检测
"""

import time
from typing import Optional, Dict, Tuple


class RequestHistory:
    """请求历史记录管理器（支持按客户端+请求ID区分）"""

    def __init__(self, max_age_seconds: int = 300):
        """
        初始化请求历史

        Args:
            max_age_seconds: 历史记录最大保留时间（秒），默认5分钟
        """
        # 格式: {request_key: (response_data, timestamp)}
        self.history: Dict[str, Tuple[bytes, float]] = {}
        self.max_age = max_age_seconds

    def is_duplicate(self, request_key: str) -> bool:
        """
        检查是否为重复请求

        Args:
            request_key: 客户端唯一请求键 (client_ip:port#request_id)

        Returns:
            True如果是重复请求且记录未过期
        """
        if request_key not in self.history:
            return False

        # 检查是否过期
        _, timestamp = self.history[request_key]
        if time.time() - timestamp > self.max_age:
            # 过期，删除记录
            del self.history[request_key]
            return False

        return True

    def get_cached_response(self, request_key: str) -> Optional[bytes]:
        """
        获取缓存的响应

        Args:
            request_key: 唯一请求键

        Returns:
            缓存的响应数据，如果不存在则返回None
        """
        if request_key in self.history:
            response, _ = self.history[request_key]
            return response
        return None

    def record_request(self, request_key: str, response: bytes):
        """
        记录请求和响应

        Args:
            request_key: 唯一请求键
            response: 响应数据
        """
        self.history[request_key] = (response, time.time())

    def cleanup_old_records(self):
        """清理所有过期的记录"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.history.items()
            if current_time - timestamp > self.max_age
        ]
        for key in expired_keys:
            del self.history[key]

    def get_history_size(self) -> int:
        """
        获取当前历史记录数量

        Returns:
            历史记录数量
        """
        return len(self.history)

    def clear_history(self):
        """清空所有历史记录"""
        self.history.clear()
