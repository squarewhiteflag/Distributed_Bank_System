"""
客户端监控接收逻辑模块
处理监控期间的回调通知接收
"""

import socket
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.marshaller import Marshaller
from common.protocol import OperationType
from client.ui import ClientUI


class MonitorClient:
    """监控客户端"""

    def __init__(self, server_address: tuple, timeout: float = 5.0):
        """
        初始化监控客户端

        Args:
            server_address: 服务器地址 (host, port)
            timeout: socket超时时间（秒）
        """
        self.server_address = server_address
        self.timeout = timeout
        self.sock = None

    def start_monitoring(self, duration: int):
        """
        开始监控，阻塞等待回调通知

        Args:
            duration: 监控时长（秒）
        """
        try:
            # 创建UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(self.timeout)

            # 绑定到任意可用端口
            self.sock.bind(('0.0.0.0', 0))

            # 获取实际绑定的端口
            actual_port = self.sock.getsockname()[1]
            ClientUI.display_info(f"Monitoring on port {actual_port} for {duration} seconds...")

            start_time = time.time()

            while True:
                # 检查是否超时
                elapsed = time.time() - start_time
                if elapsed >= duration:
                    ClientUI.display_info("Monitoring period ended.")
                    break

                try:
                    # 接收回调消息（带超时）
                    remaining_time = duration - elapsed
                    self.sock.settimeout(min(remaining_time, self.timeout))

                    data, _ = self.sock.recvfrom(1024)

                    # 解析回调消息
                    self._process_callback(data)

                except socket.timeout:
                    # 超时，继续循环
                    continue

        except Exception as e:
            ClientUI.display_error(f"Monitoring error: {e}")
        finally:
            if self.sock:
                self.sock.close()

    def _process_callback(self, data: bytes):
        """
        处理回调通知

        Args:
            data: 回调数据
        """
        try:
            # 解析回调消息
            request_id, offset = Marshaller.unpack_int(data, 0)
            operation, offset = Marshaller.unpack_int(data, offset)

            # 应该是MONITOR_CALLBACK操作
            if operation == OperationType.MONITOR_CALLBACK:
                # 解析账户信息：account_number, name, currency, balance
                account_number, offset = Marshaller.unpack_int(data, offset)
                name, offset = Marshaller.unpack_string(data, offset)
                currency, offset = Marshaller.unpack_int(data, offset)
                balance, offset = Marshaller.unpack_float(data, offset)

                # 显示更新通知
                ClientUI.display_account_update(account_number, name, currency, balance)
            else:
                ClientUI.display_info(f"Received non-callback message: {operation}")

        except Exception as e:
            ClientUI.display_error(f"Failed to process callback: {e}")
