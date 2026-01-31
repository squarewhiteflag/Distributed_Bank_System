"""
分布式银行系统 - 客户端主程序
"""

import socket
import argparse
import sys
import time
import os
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.constants import *
from common.protocol import OperationType, ResponseStatus, CurrencyType
from common.marshaller import Marshaller, RequestBuilder
from semantics.message_loss_simulator import MessageLossSimulator
from client.ui import ClientUI
from client.monitor import MonitorClient


class BankingClient:
    """银行客户端"""

    def __init__(self, server_host: str, server_port: int, semantics: str, loss_rate: float):
        """
        初始化客户端

        Args:
            server_host: 服务器主机地址
            server_port: 服务器端口
            semantics: 调用语义类型
            loss_rate: 消息丢失率
        """
        self.server_address = (server_host, server_port)
        self.semantics = semantics
        self.loss_simulator = MessageLossSimulator(loss_rate)
        self.request_counter = 0
        self.sock = None

    def _get_next_request_id(self) -> int:
        """获取下一个请求ID"""
        self.request_counter += 1
        return self.request_counter

    def _send_request(self, request_data: bytes, max_retries: int = None) -> bytes:
        """
        发送请求到服务器（带超时重传）

        Args:
            request_data: 请求数据
            max_retries: 最大重试次数

        Returns:
            响应数据

        Raises:
            Exception: 如果所有重试都失败
        """
        retries = max_retries if max_retries is not None else MAX_RETRIES

        # 在循环外创建socket，保持端口一致（重要：at-most-once语义依赖此）
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(DEFAULT_CLIENT_TIMEOUT)

        try:
            for attempt in range(retries):
                try:
                    # 模拟消息丢失（客户端请求）
                    if not self.loss_simulator.should_send():
                        if attempt == retries - 1:
                            raise Exception("Request lost (simulated) and max retries reached")
                        ClientUI.display_info(f"Request lost (simulated), retrying... ({attempt + 1}/{retries})")
                        time.sleep(0.5)  # 短暂等待后重试
                        continue

                    # 发送请求
                    self.sock.sendto(request_data, self.server_address)

                    # 接收响应
                    response_data, _ = self.sock.recvfrom(MAX_MESSAGE_SIZE)
                    return response_data

                except socket.timeout:
                    if attempt == retries - 1:
                        raise Exception("Request timeout and max retries reached")
                    ClientUI.display_info(f"Request timeout, retrying... ({attempt + 1}/{retries})")
        finally:
            # 只在所有重试结束后关闭一次socket
            if self.sock:
                self.sock.close()

        raise Exception("Failed to receive response")

    def _send_request_with_socket(self, sock: socket.socket, request_data: bytes,
                                  max_retries: int = None) -> bytes:
        """
        使用已有socket发送请求（用于监控场景，保持端口一致）
        """
        retries = max_retries if max_retries is not None else MAX_RETRIES

        for attempt in range(retries):
            try:
                sock.settimeout(DEFAULT_CLIENT_TIMEOUT)

                if not self.loss_simulator.should_send():
                    if attempt == retries - 1:
                        raise Exception("Request lost (simulated) and max retries reached")
                    ClientUI.display_info(f"Request lost (simulated), retrying... ({attempt + 1}/{retries})")
                    time.sleep(0.5)
                    continue

                sock.sendto(request_data, self.server_address)
                response_data, _ = sock.recvfrom(MAX_MESSAGE_SIZE)
                return response_data
            except socket.timeout:
                if attempt == retries - 1:
                    raise Exception("Request timeout and max retries reached")
                ClientUI.display_info(f"Request timeout, retrying... ({attempt + 1}/{retries})")
        raise Exception("Failed to receive response")

    def open_account(self):
        """开户"""
        name, password, currency, initial_balance = ClientUI.get_open_account_info()

        # 构建请求
        request_id = self._get_next_request_id()
        request = (RequestBuilder(request_id, OperationType.OPEN_ACCOUNT)
                   .add_string(name)
                   .add_string(password, fixed_length=PASSWORD_LENGTH)
                   .add_int(currency)
                   .add_float(initial_balance)
                   .build())

        try:
            # 发送请求
            response_data = self._send_request(request)

            # 解析响应
            resp_request_id, offset = Marshaller.unpack_int(response_data, 0)
            status, offset = Marshaller.unpack_int(response_data, offset)
            payload_length, offset = Marshaller.unpack_int(response_data, offset)

            if status == ResponseStatus.SUCCESS:
                account_number, _ = Marshaller.unpack_int(response_data, offset)
                ClientUI.display_success(f"Account created successfully! Account Number: {account_number}")
            else:
                ClientUI.display_error(f"Failed to create account. Status: {status}")

        except Exception as e:
            ClientUI.display_error(str(e))

    def close_account(self):
        """销户"""
        name, account_number, password = ClientUI.get_close_account_info()

        # 构建请求
        request_id = self._get_next_request_id()
        request = (RequestBuilder(request_id, OperationType.CLOSE_ACCOUNT)
                   .add_string(name)
                   .add_int(account_number)
                   .add_string(password, fixed_length=PASSWORD_LENGTH)
                   .build())

        try:
            # 发送请求
            response_data = self._send_request(request)

            # 解析响应
            resp_request_id, offset = Marshaller.unpack_int(response_data, 0)
            status, offset = Marshaller.unpack_int(response_data, offset)
            payload_length, offset = Marshaller.unpack_int(response_data, offset)

            if status == ResponseStatus.SUCCESS:
                ClientUI.display_success("Account closed successfully!")
            elif status == ResponseStatus.ERROR_ACCOUNT_NOT_FOUND:
                ClientUI.display_error("Account not found!")
            elif status == ResponseStatus.ERROR_INVALID_PASSWORD:
                ClientUI.display_error("Invalid password!")
            elif status == ResponseStatus.ERROR_ACCOUNT_NOT_OWNED:
                ClientUI.display_error("Account does not belong to this user!")
            else:
                ClientUI.display_error(f"Failed to close account. Status: {status}")

        except Exception as e:
            ClientUI.display_error(str(e))

    def deposit(self):
        """存款"""
        name, account_number, password, currency, amount = ClientUI.get_deposit_info()

        # 构建请求
        request_id = self._get_next_request_id()
        request = (RequestBuilder(request_id, OperationType.DEPOSIT)
                   .add_string(name)
                   .add_int(account_number)
                   .add_string(password, fixed_length=PASSWORD_LENGTH)
                   .add_int(currency)
                   .add_float(amount)
                   .build())

        try:
            # 发送请求
            response_data = self._send_request(request)

            # 解析响应
            resp_request_id, offset = Marshaller.unpack_int(response_data, 0)
            status, offset = Marshaller.unpack_int(response_data, offset)
            payload_length, offset = Marshaller.unpack_int(response_data, offset)

            if status == ResponseStatus.SUCCESS:
                new_balance, _ = Marshaller.unpack_float(response_data, offset)
                ClientUI.display_success(f"Deposit successful! New balance: {new_balance:.2f}")
            elif status == ResponseStatus.ERROR_ACCOUNT_NOT_FOUND:
                ClientUI.display_error("Account not found!")
            elif status == ResponseStatus.ERROR_INVALID_PASSWORD:
                ClientUI.display_error("Invalid password!")
            else:
                ClientUI.display_error(f"Failed to deposit. Status: {status}")

        except Exception as e:
            ClientUI.display_error(str(e))

    def withdraw(self):
        """取款"""
        name, account_number, password, currency, amount = ClientUI.get_withdraw_info()

        # 构建请求
        request_id = self._get_next_request_id()
        request = (RequestBuilder(request_id, OperationType.WITHDRAW)
                   .add_string(name)
                   .add_int(account_number)
                   .add_string(password, fixed_length=PASSWORD_LENGTH)
                   .add_int(currency)
                   .add_float(amount)
                   .build())

        try:
            # 发送请求
            response_data = self._send_request(request)

            # 解析响应
            resp_request_id, offset = Marshaller.unpack_int(response_data, 0)
            status, offset = Marshaller.unpack_int(response_data, offset)
            payload_length, offset = Marshaller.unpack_int(response_data, offset)

            if status == ResponseStatus.SUCCESS:
                new_balance, _ = Marshaller.unpack_float(response_data, offset)
                ClientUI.display_success(f"Withdrawal successful! New balance: {new_balance:.2f}")
            elif status == ResponseStatus.ERROR_ACCOUNT_NOT_FOUND:
                ClientUI.display_error("Account not found!")
            elif status == ResponseStatus.ERROR_INVALID_PASSWORD:
                ClientUI.display_error("Invalid password!")
            elif status == ResponseStatus.ERROR_INSUFFICIENT_BALANCE:
                ClientUI.display_error("Insufficient balance!")
            else:
                ClientUI.display_error(f"Failed to withdraw. Status: {status}")

        except Exception as e:
            ClientUI.display_error(str(e))

    def query_account(self):
        """查询账户（幂等操作）"""
        account_number, password = ClientUI.get_query_account_info()

        # 构建请求
        request_id = self._get_next_request_id()
        request = (RequestBuilder(request_id, OperationType.QUERY_ACCOUNT)
                   .add_int(account_number)
                   .add_string(password, fixed_length=PASSWORD_LENGTH)
                   .build())

        try:
            # 发送请求
            response_data = self._send_request(request)

            # 解析响应
            resp_request_id, offset = Marshaller.unpack_int(response_data, 0)
            status, offset = Marshaller.unpack_int(response_data, offset)
            payload_length, offset = Marshaller.unpack_int(response_data, offset)

            if status == ResponseStatus.SUCCESS:
                # 解析账户信息
                acc_number, offset = Marshaller.unpack_int(response_data, offset)
                name, offset = Marshaller.unpack_string(response_data, offset)
                currency, offset = Marshaller.unpack_int(response_data, offset)
                balance, _ = Marshaller.unpack_float(response_data, offset)

                currency_names = {1: "USD", 2: "EUR", 3: "SGD", 4: "CNY"}
                currency_name = currency_names.get(currency, "Unknown")

                ClientUI.display_success(f"Account Information:")
                print(f"  Account Number: {acc_number}")
                print(f"  Name: {name}")
                print(f"  Currency: {currency_name}")
                print(f"  Balance: {balance:.2f}")

            elif status == ResponseStatus.ERROR_ACCOUNT_NOT_FOUND:
                ClientUI.display_error("Account not found!")
            elif status == ResponseStatus.ERROR_INVALID_PASSWORD:
                ClientUI.display_error("Invalid password!")
            else:
                ClientUI.display_error(f"Failed to query account. Status: {status}")

        except Exception as e:
            ClientUI.display_error(str(e))

    def transfer(self):
        """转账（非幂等操作）"""
        from_account, password, to_account, amount = ClientUI.get_transfer_info()

        # 构建请求
        request_id = self._get_next_request_id()
        request = (RequestBuilder(request_id, OperationType.TRANSFER)
                   .add_int(from_account)
                   .add_string(password, fixed_length=PASSWORD_LENGTH)
                   .add_int(to_account)
                   .add_float(amount)
                   .build())

        try:
            # 发送请求
            response_data = self._send_request(request)

            # 解析响应
            resp_request_id, offset = Marshaller.unpack_int(response_data, 0)
            status, offset = Marshaller.unpack_int(response_data, offset)
            payload_length, offset = Marshaller.unpack_int(response_data, offset)

            if status == ResponseStatus.SUCCESS:
                new_balance, _ = Marshaller.unpack_float(response_data, offset)
                ClientUI.display_success(f"Transfer successful! New balance in source account: {new_balance:.2f}")
            elif status == ResponseStatus.ERROR_ACCOUNT_NOT_FOUND:
                ClientUI.display_error("One or both accounts not found!")
            elif status == ResponseStatus.ERROR_INVALID_PASSWORD:
                ClientUI.display_error("Invalid source account password!")
            elif status == ResponseStatus.ERROR_INSUFFICIENT_BALANCE:
                ClientUI.display_error("Insufficient balance in source account!")
            else:
                ClientUI.display_error(f"Failed to transfer. Status: {status}")

        except Exception as e:
            ClientUI.display_error(str(e))

    def monitor_updates(self):
        """监控账户更新"""
        duration = ClientUI.get_monitor_info()

        request_id = self._get_next_request_id()
        request = (RequestBuilder(request_id, OperationType.MONITOR_REGISTER)
                   .add_int(duration)
                   .build())

        try:
            monitor = MonitorClient(self.server_address, loss_simulator=self.loss_simulator,
                                    semantics=self.semantics)
            monitor.start_monitoring(duration, request, request_id)
        except Exception as e:
            ClientUI.display_error(str(e))

    def run(self):
        """运行客户端主循环"""
        ClientUI.display_info(f"Connected to server at {self.server_address[0]}:{self.server_address[1]}")
        ClientUI.display_info(f"Invocation semantics: {self.semantics}")
        ClientUI.display_info(f"Message loss rate: {self.loss_simulator.get_loss_rate():.1%}")

        while True:
            ClientUI.display_menu()
            choice = ClientUI.get_user_choice()

            if choice == 0:
                print("Goodbye!")
                break
            elif choice == 1:
                self.open_account()
            elif choice == 2:
                self.close_account()
            elif choice == 3:
                self.deposit()
            elif choice == 4:
                self.withdraw()
            elif choice == 5:
                self.query_account()
            elif choice == 6:
                self.transfer()
            elif choice == 7:
                self.monitor_updates()
            else:
                ClientUI.display_error("Invalid choice. Please try again.")

            input("\nPress Enter to continue...")


def main():
    """主函数"""
    # Tee 日志到文件
    class Tee:
        def __init__(self, stream, file_path):
            self.stream = stream
            self.file = open(file_path, "a", buffering=1)

        def write(self, data):
            self.stream.write(data)
            self.file.write(data)

        def flush(self):
            self.stream.flush()
            self.file.flush()

    project_root = Path(__file__).resolve().parents[2]
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # 清空客户端日志文件
    client_log_path = logs_dir / "client.log"
    client_log_path.write_text("")  # 清空日志文件

    sys.stdout = Tee(sys.stdout, client_log_path)
    sys.stderr = Tee(sys.stderr, client_log_path)

    parser = argparse.ArgumentParser(description='Distributed Banking System - Client')
    parser.add_argument('--server-host', type=str, required=True,
                        help='Server host address')
    parser.add_argument('--server-port', type=int, default=DEFAULT_SERVER_PORT,
                        help=f'Server port (default: {DEFAULT_SERVER_PORT})')
    parser.add_argument('--semantics', type=str, choices=[SEMANTICS_AT_LEAST_ONCE, SEMANTICS_AT_MOST_ONCE],
                        default=SEMANTICS_AT_MOST_ONCE,
                        help='Invocation semantics (default: at-most-once)')
    parser.add_argument('--loss-rate', type=float, default=0.0,
                        help='Message loss rate 0.0-1.0 (default: 0.0)')

    args = parser.parse_args()

    # 创建并运行客户端
    client = BankingClient(
        server_host=args.server_host,
        server_port=args.server_port,
        semantics=args.semantics,
        loss_rate=args.loss_rate
    )

    try:
        client.run()
    except KeyboardInterrupt:
        print("\nClient terminated.")


if __name__ == '__main__':
    main()
