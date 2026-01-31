"""
服务处理模块
处理所有银行操作的逻辑
"""

from typing import Tuple
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.protocol import OperationType, ResponseStatus
from common.marshaller import Marshaller, ResponseBuilder
from server.account_manager import AccountManager


class ServiceHandler:
    """服务处理器"""

    def __init__(self, account_manager: AccountManager):
        """
        初始化服务处理器

        Args:
            account_manager: 账户管理器实例
        """
        self.account_manager = account_manager

    def handle_request(self, request_data: bytes):
        """
        处理客户端请求

        Args:
            request_data: 请求数据（字节数组）

        Returns:
            (响应数据, 受影响的账户号列表)
        """
        try:
            # 解析请求头
            request_id, offset = Marshaller.unpack_int(request_data, 0)
            operation, offset = Marshaller.unpack_int(request_data, offset)
            payload_length, offset = Marshaller.unpack_int(request_data, offset)

            # 根据操作类型分发处理
            operation_type = OperationType(operation)

            if operation_type == OperationType.OPEN_ACCOUNT:
                return self._handle_open_account(request_data, offset, request_id)
            elif operation_type == OperationType.CLOSE_ACCOUNT:
                return self._handle_close_account(request_data, offset, request_id)
            elif operation_type == OperationType.DEPOSIT:
                return self._handle_deposit(request_data, offset, request_id)
            elif operation_type == OperationType.WITHDRAW:
                return self._handle_withdraw(request_data, offset, request_id)
            elif operation_type == OperationType.MONITOR_REGISTER:
                return self._handle_monitor_register(request_data, offset, request_id)
            elif operation_type == OperationType.QUERY_ACCOUNT:
                return self._handle_query_account(request_data, offset, request_id)
            elif operation_type == OperationType.TRANSFER:
                return self._handle_transfer(request_data, offset, request_id)
            else:
                # 未知操作
                return ResponseBuilder(request_id, ResponseStatus.ERROR_INVALID_OPERATION).build(), []

        except Exception as e:
            # 处理错误
            print(f"Error handling request: {e}")
            # 尝试提取request_id
            try:
                request_id, _ = Marshaller.unpack_int(request_data, 0)
                return ResponseBuilder(request_id, ResponseStatus.ERROR_UNKNOWN).build(), []
            except:
                # 如果无法提取request_id，返回错误响应
                return ResponseBuilder(0, ResponseStatus.ERROR_UNKNOWN).build(), []

    def _handle_open_account(self, request_data: bytes, offset: int, request_id: int) -> bytes:
        """处理开户请求"""
        try:
            # 解析参数：name (变长), password (定长16), currency (int), balance (float)
            name, offset = Marshaller.unpack_string(request_data, offset)
            password, offset = Marshaller.unpack_string(request_data, offset, fixed_length=16)
            currency, offset = Marshaller.unpack_int(request_data, offset)
            balance, offset = Marshaller.unpack_float(request_data, offset)

            print(f"[DEBUG] Creating account: name={name}, currency={currency}, balance={balance}")

            # 执行开户
            account_number = self.account_manager.create_account(
                name=name,
                password=password,
                currency=currency,
                initial_balance=balance
            )

            print(f"[DEBUG] Account created: account_number={account_number}")

            # 构建响应
            response = (ResponseBuilder(request_id, ResponseStatus.SUCCESS)
                    .add_int(account_number)
                    .build())

            print(f"[DEBUG] Response built: request_id={request_id}, status=SUCCESS, account_number={account_number}")

            return response, [account_number]

        except Exception as e:
            print(f"Error in open_account: {e}")
            import traceback
            traceback.print_exc()
            return ResponseBuilder(request_id, ResponseStatus.ERROR_UNKNOWN).build(), []

    def _handle_close_account(self, request_data: bytes, offset: int, request_id: int) -> bytes:
        """处理销户请求"""
        try:
            # 解析参数：name (变长), account_number (int), password (定长16)
            name, offset = Marshaller.unpack_string(request_data, offset)
            account_number, offset = Marshaller.unpack_int(request_data, offset)
            password, offset = Marshaller.unpack_string(request_data, offset, fixed_length=16)

            # 执行销户
            closed_account = self.account_manager.close_account(account_number, name, password)

            # 构建响应
            return ResponseBuilder(request_id, ResponseStatus.SUCCESS).build(), [account_number]

        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg:
                status = ResponseStatus.ERROR_ACCOUNT_NOT_FOUND
            elif "not owned" in error_msg:
                status = ResponseStatus.ERROR_ACCOUNT_NOT_OWNED
            elif "password" in error_msg:
                status = ResponseStatus.ERROR_INVALID_PASSWORD
            else:
                status = ResponseStatus.ERROR_UNKNOWN
            return ResponseBuilder(request_id, status).build(), []
        except Exception as e:
            print(f"Error in close_account: {e}")
            return ResponseBuilder(request_id, ResponseStatus.ERROR_UNKNOWN).build(), []

    def _handle_deposit(self, request_data: bytes, offset: int, request_id: int) -> bytes:
        """处理存款请求"""
        try:
            # 解析参数：name (变长), account_number (int), password (定长16),
            #           currency (int), amount (float)
            name, offset = Marshaller.unpack_string(request_data, offset)
            account_number, offset = Marshaller.unpack_int(request_data, offset)
            password, offset = Marshaller.unpack_string(request_data, offset, fixed_length=16)
            currency, offset = Marshaller.unpack_int(request_data, offset)
            amount, offset = Marshaller.unpack_float(request_data, offset)

            # 执行存款
            new_balance = self.account_manager.deposit(account_number, name, password, currency, amount)

            # 构建响应
            return (ResponseBuilder(request_id, ResponseStatus.SUCCESS)
                    .add_float(new_balance)
                    .build()), [account_number]

        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg:
                status = ResponseStatus.ERROR_ACCOUNT_NOT_FOUND
            elif "password" in error_msg:
                status = ResponseStatus.ERROR_INVALID_PASSWORD
            elif "owned" in error_msg or "currency" in error_msg:
                status = ResponseStatus.ERROR_INVALID_OPERATION
            else:
                status = ResponseStatus.ERROR_UNKNOWN
            return ResponseBuilder(request_id, status).build(), []
        except Exception as e:
            print(f"Error in deposit: {e}")
            return ResponseBuilder(request_id, ResponseStatus.ERROR_UNKNOWN).build(), []

    def _handle_withdraw(self, request_data: bytes, offset: int, request_id: int) -> bytes:
        """处理取款请求"""
        try:
            # 解析参数：name (变长), account_number (int), password (定长16),
            #           currency (int), amount (float)
            name, offset = Marshaller.unpack_string(request_data, offset)
            account_number, offset = Marshaller.unpack_int(request_data, offset)
            password, offset = Marshaller.unpack_string(request_data, offset, fixed_length=16)
            currency, offset = Marshaller.unpack_int(request_data, offset)
            amount, offset = Marshaller.unpack_float(request_data, offset)

            # 执行取款
            new_balance = self.account_manager.withdraw(account_number, name, password, currency, amount)

            # 构建响应
            return (ResponseBuilder(request_id, ResponseStatus.SUCCESS)
                    .add_float(new_balance)
                    .build()), [account_number]

        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg:
                status = ResponseStatus.ERROR_ACCOUNT_NOT_FOUND
            elif "password" in error_msg:
                status = ResponseStatus.ERROR_INVALID_PASSWORD
            elif "Insufficient" in error_msg:
                status = ResponseStatus.ERROR_INSUFFICIENT_BALANCE
            elif "owned" in error_msg or "currency" in error_msg:
                status = ResponseStatus.ERROR_INVALID_OPERATION
            else:
                status = ResponseStatus.ERROR_UNKNOWN
            return ResponseBuilder(request_id, status).build(), []
        except Exception as e:
            print(f"Error in withdraw: {e}")
            return ResponseBuilder(request_id, ResponseStatus.ERROR_UNKNOWN).build(), []

    def _handle_monitor_register(self, request_data: bytes, offset: int, request_id: int) -> bytes:
        """处理监控注册请求"""
        try:
            # 解析参数：duration (int)
            duration, offset = Marshaller.unpack_int(request_data, offset)

            # 注意：实际的监控注册逻辑在服务器主程序中处理
            # 这里只返回成功状态
            # MonitorManager会在服务器主循环中被调用

            # 构建响应
            return ResponseBuilder(request_id, ResponseStatus.SUCCESS).build(), []

        except Exception as e:
            print(f"Error in monitor_register: {e}")
            return ResponseBuilder(request_id, ResponseStatus.ERROR_UNKNOWN).build(), []

    def _handle_query_account(self, request_data: bytes, offset: int, request_id: int) -> bytes:
        """处理查询账户请求（幂等操作）"""
        try:
            # 解析参数：account_number (int), password (定长16)
            account_number, offset = Marshaller.unpack_int(request_data, offset)
            password, offset = Marshaller.unpack_string(request_data, offset, fixed_length=16)

            # 获取账户信息
            account = self.account_manager.get_account(account_number)
            if not account:
                return ResponseBuilder(request_id, ResponseStatus.ERROR_ACCOUNT_NOT_FOUND).build(), []

            # 验证密码
            if account.password != password:
                return ResponseBuilder(request_id, ResponseStatus.ERROR_INVALID_PASSWORD).build(), []

            # 构建响应：account_number, name, currency, balance
            return (ResponseBuilder(request_id, ResponseStatus.SUCCESS)
                    .add_int(account.account_number)
                    .add_string(account.name)
                    .add_int(account.currency.value if hasattr(account.currency, "value") else int(account.currency))
                    .add_float(account.balance)
                    .build()), []

        except Exception as e:
            print(f"Error in query_account: {e}")
            import traceback
            traceback.print_exc()
            return ResponseBuilder(request_id, ResponseStatus.ERROR_UNKNOWN).build(), []

    def _handle_transfer(self, request_data: bytes, offset: int, request_id: int) -> bytes:
        """处理转账请求（非幂等操作）"""
        try:
            # 解析参数：from_account (int), password (定长16),
            #           to_account (int), amount (float)
            from_account, offset = Marshaller.unpack_int(request_data, offset)
            password, offset = Marshaller.unpack_string(request_data, offset, fixed_length=16)
            to_account, offset = Marshaller.unpack_int(request_data, offset)
            amount, offset = Marshaller.unpack_float(request_data, offset)

            # 执行转账
            new_balance = self.account_manager.transfer(
                from_account, password, to_account, amount
            )

            # 构建响应
            return (ResponseBuilder(request_id, ResponseStatus.SUCCESS)
                    .add_float(new_balance)
                    .build()), [from_account, to_account]

        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg:
                status = ResponseStatus.ERROR_ACCOUNT_NOT_FOUND
            elif "password" in error_msg:
                status = ResponseStatus.ERROR_INVALID_PASSWORD
            elif "Insufficient" in error_msg:
                status = ResponseStatus.ERROR_INSUFFICIENT_BALANCE
            else:
                status = ResponseStatus.ERROR_UNKNOWN
            return ResponseBuilder(request_id, status).build(), []
        except Exception as e:
            print(f"Error in transfer: {e}")
            return ResponseBuilder(request_id, ResponseStatus.ERROR_UNKNOWN).build(), []
