"""
监控客户端管理模块
负责维护监控客户端列表、发送回调通知
"""

import time
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class MonitorClient:
    """监控客户端信息"""
    address: Tuple[str, int]  # (IP, Port)
    expire_time: float  # 过期时间戳


class MonitorManager:
    """监控客户端管理器"""

    def __init__(self):
        """初始化监控管理器"""
        # 字典存储监控客户端：{address_key: MonitorClient}
        # address_key格式: "ip:port"
        self.monitors: Dict[str, MonitorClient] = {}

    def register_monitor(self, client_address: Tuple[str, int], duration: int) -> bool:
        """
        注册监控客户端

        Args:
            client_address: 客户端地址 (IP, Port)
            duration: 监控时长（秒）

        Returns:
            True如果注册成功
        """
        ip, port = client_address
        key = f"{ip}:{port}"

        expire_time = time.time() + duration

        # 如果客户端已存在，更新过期时间
        self.monitors[key] = MonitorClient(
            address=client_address,
            expire_time=expire_time
        )

        return True

    def unregister_monitor(self, client_address: Tuple[str, int]) -> bool:
        """
        注销监控客户端

        Args:
            client_address: 客户端地址

        Returns:
            True如果注销成功，False如果客户端不存在
        """
        ip, port = client_address
        key = f"{ip}:{port}"

        if key in self.monitors:
            del self.monitors[key]
            return True
        return False

    def get_active_monitors(self) -> list:
        """
        获取所有活跃的监控客户端

        Returns:
            监控客户端地址列表 [(ip, port), ...]
        """
        current_time = time.time()
        active_monitors = []

        # 清理过期的监控客户端
        expired_keys = []
        for key, monitor in self.monitors.items():
            if current_time > monitor.expire_time:
                expired_keys.append(key)
            else:
                active_monitors.append(monitor.address)

        # 删除过期客户端
        for key in expired_keys:
            del self.monitors[key]

        return active_monitors

    def is_monitoring(self, client_address: Tuple[str, int]) -> bool:
        """
        检查客户端是否正在监控

        Args:
            client_address: 客户端地址

        Returns:
            True如果正在监控且未过期
        """
        ip, port = client_address
        key = f"{ip}:{port}"

        if key not in self.monitors:
            return False

        monitor = self.monitors[key]
        if time.time() > monitor.expire_time:
            # 已过期，删除
            del self.monitors[key]
            return False

        return True

    def get_monitor_count(self) -> int:
        """
        获取当前监控客户端数量（包括已过期的）

        Returns:
            监控客户端数量
        """
        return len(self.monitors)

    def cleanup_expired(self):
        """清理所有过期的监控客户端"""
        current_time = time.time()
        expired_keys = [
            key for key, monitor in self.monitors.items()
            if current_time > monitor.expire_time
        ]
        for key in expired_keys:
            del self.monitors[key]
