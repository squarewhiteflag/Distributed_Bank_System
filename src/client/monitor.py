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
from common.constants import MAX_RETRIES, DEFAULT_CLIENT_TIMEOUT
from client.ui import ClientUI


class MonitorClient:
    """监控客户端"""

    def __init__(self, server_address: tuple, timeout: float = None, loss_simulator=None, semantics="at-most-once"):
        """
        初始化监控客户端

        Args:
            server_address: 服务器地址 (host, port)
            timeout: socket超时时间（秒），默认使用 DEFAULT_CLIENT_TIMEOUT
            loss_simulator: 用于模拟消息丢失的实例
            semantics: 调用语义（用于日志显示）
        """
        self.server_address = server_address
        self.timeout = timeout if timeout is not None else DEFAULT_CLIENT_TIMEOUT
        self.loss_simulator = loss_simulator
        self.semantics = semantics
        self.sock = None

    def start_monitoring(self, duration: int, registration_request: bytes, request_id: int):
        """
        先注册监控，再阻塞等待回调

        Args:
            duration: 监控时长（秒）
            registration_request: 注册消息字节
            request_id: 请求ID（用于日志）
        """
        try:
            # 创建UDP socket并绑定，确保服务器回调用同一端口
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('0.0.0.0', 0))

            # 注册监控（使用同一socket），使用 MAX_RETRIES 次重试
            for attempt in range(MAX_RETRIES):
                try:
                    self.sock.settimeout(self.timeout)
                    if self.loss_simulator and not self.loss_simulator.should_send():
                        if attempt == MAX_RETRIES - 1:
                            raise Exception("Monitor registration lost (simulated) and max retries reached")
                        ClientUI.display_info(f"Monitor registration lost (simulated), retrying... ({attempt + 1}/{MAX_RETRIES})")
                        time.sleep(0.5)  # 短暂等待后重试
                        continue

                    self.sock.sendto(registration_request, self.server_address)
                    resp, _ = self.sock.recvfrom(1024)

                    resp_id, off = Marshaller.unpack_int(resp, 0)
                    status, off = Marshaller.unpack_int(resp, off)
                    _, off = Marshaller.unpack_int(resp, off)  # payload length
                    if status == 0:
                        ClientUI.display_success("Monitor registration successful!")
                        break
                    else:
                        raise Exception(f"Monitor registration failed with status {status}")
                except socket.timeout:
                    if attempt == MAX_RETRIES - 1:
                        raise Exception("Monitor registration timeout and max retries reached")
                    ClientUI.display_info(f"Monitor registration timeout, retrying... ({attempt + 1}/{MAX_RETRIES})")

            # 获取实际绑定的端口
            actual_port = self.sock.getsockname()[1]
            ClientUI.display_info(f"Monitoring on port {actual_port} for {duration} seconds...")

            start_time = time.time()

            while True:
                elapsed = time.time() - start_time
                if elapsed >= duration:
                    ClientUI.display_info("Monitoring period ended.")
                    break

                try:
                    remaining = duration - elapsed
                    self.sock.settimeout(min(remaining, self.timeout))
                    data, _ = self.sock.recvfrom(1024)
                    self._process_callback(data)
                except socket.timeout:
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
            payload_length, offset = Marshaller.unpack_int(data, offset)

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
