"""
分布式银行系统 - 服务器主程序
"""

import socket
import argparse
import sys
import time
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.constants import *
from common.protocol import OperationType, ResponseStatus
from common.marshaller import Marshaller, ResponseBuilder
from server.account_manager import AccountManager
from server.monitor_manager import MonitorManager
from server.service_handler import ServiceHandler
from semantics.request_history import RequestHistory
from semantics.message_loss_simulator import MessageLossSimulator


class BankingServer:
    """银行服务器"""

    def __init__(self, host: str, port: int, semantics: str, loss_rate: float, verbose: bool = False):
        """
        初始化服务器

        Args:
            host: 监听地址
            port: 监听端口
            semantics: 调用语义类型 (at-least-once 或 at-most-once)
            loss_rate: 消息丢失率 (0.0-1.0)
            verbose: 是否显示详细日志
        """
        self.host = host
        self.port = port
        self.semantics = semantics
        self.verbose = verbose

        # 初始化各模块
        self.account_manager = AccountManager()
        self.monitor_manager = MonitorManager()
        self.service_handler = ServiceHandler(self.account_manager)
        self.loss_simulator = MessageLossSimulator(loss_rate)

        # 至多一次语义需要请求历史
        if self.semantics == SEMANTICS_AT_MOST_ONCE:
            self.request_history = RequestHistory(REQUEST_HISTORY_MAX_AGE)
        else:
            self.request_history = None

        # UDP socket
        self.sock = None

        # 服务器运行标志
        self.running = False

    def start(self):
        """启动服务器"""
        try:
            # 创建UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.host, self.port))

            self.running = True

            print(f"Server started on {self.host}:{self.port}")
            print(f"Semantics: {self.semantics}")
            print(f"Message loss rate: {self.loss_simulator.get_loss_rate():.1%}")
            print("Waiting for clients...\n")

            # 主循环
            while self.running:
                try:
                    # 接收请求
                    self.sock.settimeout(1.0)  # 1秒超时，以便检查running标志
                    data, client_addr = self.sock.recvfrom(MAX_MESSAGE_SIZE)

                    if self.verbose:
                        print(f"[DEBUG] Received request from {client_addr}")

                    # 处理请求
                    response_data = self._process_request(data, client_addr)

                    # 模拟消息丢失（服务器回复）
                    if not self.loss_simulator.should_send():
                        if self.verbose:
                            print(f"[DEBUG] Server response to {client_addr} LOST (simulated)")
                        continue

                    # 发送回复
                    self.sock.sendto(response_data, client_addr)

                    if self.verbose:
                        print(f"[DEBUG] Sent response to {client_addr}")

                except socket.timeout:
                    # 超时，继续循环
                    continue
                except Exception as e:
                    print(f"Error processing request: {e}")
                    continue

                # 定期清理过期记录
                if self.request_history:
                    self.request_history.cleanup_old_records()
                self.monitor_manager.cleanup_expired()

        except KeyboardInterrupt:
            print("\nShutting down server...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()

    def stop(self):
        """停止服务器"""
        self.running = False
        if self.sock:
            self.sock.close()
        print("Server stopped.")

    def _process_request(self, request_data: bytes, client_addr: tuple) -> bytes:
        """
        处理客户端请求

        Args:
            request_data: 请求数据
            client_addr: 客户端地址

        Returns:
            响应数据
        """
        try:
            # 解析请求ID
            request_id, _ = Marshaller.unpack_int(request_data, 0)

            # 至多一次语义：检查重复请求
            if self.semantics == SEMANTICS_AT_MOST_ONCE and self.request_history:
                if self.request_history.is_duplicate(request_id):
                    # 重复请求，返回缓存的响应
                    if self.verbose:
                        print(f"[DEBUG] Duplicate request {request_id}, returning cached response")
                    cached_response = self.request_history.get_cached_response(request_id)
                    if cached_response:
                        return cached_response

            # 解析操作类型
            operation, _ = Marshaller.unpack_int(request_data, 4)
            operation_type = OperationType(operation)

            if self.verbose:
                print(f"[DEBUG] Processing request {request_id}: {operation_type.name}")

            # 处理监控注册
            if operation_type == OperationType.MONITOR_REGISTER:
                response_data = self._handle_monitor_register(request_data, client_addr, request_id)
            else:
                # 其他操作由ServiceHandler处理
                response_data = self.service_handler.handle_request(request_data)

                # 检查是否是修改账户的操作（需要发送监控通知）
                if operation_type in [OperationType.OPEN_ACCOUNT, OperationType.CLOSE_ACCOUNT,
                                     OperationType.DEPOSIT, OperationType.WITHDRAW,
                                     OperationType.TRANSFER]:
                    self._send_monitor_notifications()

            # 至多一次语义：记录请求历史
            if self.semantics == SEMANTICS_AT_MOST_ONCE and self.request_history:
                self.request_history.record_request(request_id, response_data)

            return response_data

        except Exception as e:
            print(f"Error in _process_request: {e}")
            return ResponseBuilder(0, ResponseStatus.ERROR_UNKNOWN).build()

    def _handle_monitor_register(self, request_data: bytes, client_addr: tuple, request_id: int) -> bytes:
        """
        处理监控注册

        Args:
            request_data: 请求数据
            client_addr: 客户端地址
            request_id: 请求ID

        Returns:
            响应数据
        """
        try:
            # 解析监控时长
            offset = 12  # 跳过消息头
            duration, _ = Marshaller.unpack_int(request_data, offset)

            # 限制范围
            duration = max(MIN_MONITOR_DURATION, min(MAX_MONITOR_DURATION, duration))

            # 注册监控
            self.monitor_manager.register_monitor(client_addr, duration)

            print(f"Client {client_addr} registered for monitoring ({duration}s)")

            return ResponseBuilder(request_id, ResponseStatus.SUCCESS).build()

        except Exception as e:
            print(f"Error in _handle_monitor_register: {e}")
            return ResponseBuilder(request_id, ResponseStatus.ERROR_UNKNOWN).build()

    def _send_monitor_notifications(self):
        """向所有监控客户端发送账户更新通知"""
        active_monitors = self.monitor_manager.get_active_monitors()

        if not active_monitors:
            return

        # 获取所有账户信息（简化版：发送所有账户的更新）
        # 实际应用中应该只发送被更新的账户
        accounts = self.account_manager.get_all_accounts()

        for account in accounts.values():
            # 构建回调通知
            callback_data = (
                Marshaller.pack_int(0) +  # request_id (回调消息没有对应请求)
                Marshaller.pack_int(OperationType.MONITOR_CALLBACK) +
                Marshaller.pack_int(0) +  # payload length占位
                Marshaller.pack_int(account.account_number) +
                Marshaller.pack_string(account.name) +
                Marshaller.pack_int(account.currency.value) +
                Marshaller.pack_float(account.balance)
            )

            # 发送给所有监控客户端
            for monitor_addr in active_monitors:
                try:
                    # 模拟消息丢失
                    if not self.loss_simulator.should_send():
                        continue

                    self.sock.sendto(callback_data, monitor_addr)
                except Exception as e:
                    print(f"Failed to send callback to {monitor_addr}: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Distributed Banking System - Server')
    parser.add_argument('--host', type=str, default=DEFAULT_SERVER_HOST,
                        help=f'Server host (default: {DEFAULT_SERVER_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_SERVER_PORT,
                        help=f'Server port (default: {DEFAULT_SERVER_PORT})')
    parser.add_argument('--semantics', type=str, choices=[SEMANTICS_AT_LEAST_ONCE, SEMANTICS_AT_MOST_ONCE],
                        default=SEMANTICS_AT_MOST_ONCE,
                        help='Invocation semantics (default: at-most-once)')
    parser.add_argument('--loss-rate', type=float, default=0.0,
                        help='Message loss rate 0.0-1.0 (default: 0.0)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()

    # 创建并启动服务器
    server = BankingServer(
        host=args.host,
        port=args.port,
        semantics=args.semantics,
        loss_rate=args.loss_rate,
        verbose=args.verbose
    )

    server.start()


if __name__ == '__main__':
    main()
