"""
账户管理模块
负责账户数据的创建、查询、更新和删除
"""

from dataclasses import dataclass
from typing import Optional, Dict
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.protocol import CurrencyType
from common.constants import INITIAL_ACCOUNT_NUMBER


@dataclass
class Account:
    """账户数据类"""
    account_number: int
    name: str
    password: str  # 实际应用中应该加密存储
    currency: CurrencyType
    balance: float


class AccountManager:
    """账户管理器"""

    def __init__(self):
        """初始化账户管理器"""
        # 使用字典存储账户：{account_number: Account}
        self.accounts: Dict[int, Account] = {}
        self.next_account_number = INITIAL_ACCOUNT_NUMBER

    def create_account(self, name: str, password: str,
                      currency: CurrencyType, initial_balance: float) -> int:
        """
        创建新账户

        Args:
            name: 账户持有人姓名
            password: 账户密码
            currency: 货币类型
            initial_balance: 初始余额

        Returns:
            新创建的账户号
        """
        account_number = self.next_account_number
        self.next_account_number += 1

        # 确保使用CurrencyType枚举
        if not isinstance(currency, CurrencyType):
            currency = CurrencyType(int(currency))

        account = Account(
            account_number=account_number,
            name=name,
            password=password,
            currency=currency,
            balance=initial_balance
        )

        self.accounts[account_number] = account
        return account_number

    def close_account(self, account_number: int, name: str, password: str):
        """
        关闭账户

        Args:
            account_number: 账户号
            name: 账户持有人姓名
            password: 账户密码

        Returns:
            被关闭的账户对象（用于回调），关闭失败抛出异常

        Raises:
            ValueError: 如果账户不存在、密码错误或账户不属于该用户
        """
        account = self.accounts.get(account_number)
        if not account:
            raise ValueError("Account not found")
        if account.name != name:
            raise ValueError("Account not owned by this user")
        if account.password != password:
            raise ValueError("Invalid password")

        # 保留快照用于回调
        closed_account = Account(
            account_number=account.account_number,
            name=account.name,
            password=account.password,
            currency=account.currency,
            balance=account.balance
        )
        del self.accounts[account_number]
        return closed_account

    def deposit(self, account_number: int, name: str, password: str,
                currency, amount: float) -> float:
        """
        存款

        Args:
            account_number: 账户号
            password: 账户密码
            amount: 存款金额

        Returns:
            存款后的新余额

        Raises:
            ValueError: 如果账户不存在、密码错误、账户不属于该用户或币种不匹配
        """
        account = self.accounts.get(account_number)
        if not account:
            raise ValueError("Account not found")
        if account.name != name:
            raise ValueError("Account not owned by this user")
        if account.password != password:
            raise ValueError("Invalid password")
        if not isinstance(currency, CurrencyType):
            currency = CurrencyType(int(currency))
        if account.currency != currency:
            raise ValueError("Currency mismatch")

        account.balance += amount
        return account.balance

    def withdraw(self, account_number: int, name: str, password: str,
                 currency, amount: float) -> float:
        """
        取款

        Args:
            account_number: 账户号
            password: 账户密码
            amount: 取款金额

        Returns:
            取款后的新余额

        Raises:
            ValueError: 如果账户不存在、密码错误、账户不属于该用户、币种不匹配或余额不足
        """
        account = self.accounts.get(account_number)
        if not account:
            raise ValueError("Account not found")
        if account.name != name:
            raise ValueError("Account not owned by this user")
        if account.password != password:
            raise ValueError("Invalid password")
        if not isinstance(currency, CurrencyType):
            currency = CurrencyType(int(currency))
        if account.currency != currency:
            raise ValueError("Currency mismatch")
        if account.balance < amount:
            raise ValueError("Insufficient balance")

        account.balance -= amount
        return account.balance

    def get_account(self, account_number: int) -> Optional[Account]:
        """
        获取账户信息

        Args:
            account_number: 账户号

        Returns:
            账户对象，如果不存在则返回None
        """
        return self.accounts.get(account_number)

    def verify_password(self, account_number: int, password: str) -> bool:
        """
        验证密码

        Args:
            account_number: 账户号
            password: 密码

        Returns:
            True如果密码正确，否则False
        """
        account = self.accounts.get(account_number)
        return account and account.password == password

    def transfer(self, from_account: int, from_password: str,
                 to_account: int, amount: float) -> float:
        """
        转账（非幂等操作）

        Args:
            from_account: 转出账户号
            from_password: 转出账户密码
            to_account: 转入账户号
            amount: 转账金额

        Returns:
            转出账户的新余额

        Raises:
            ValueError: 如果账户不存在、密码错误或余额不足
        """
        # 验证转出账户
        from_acc = self.accounts.get(from_account)
        if not from_acc:
            raise ValueError("Source account not found")
        if from_acc.password != from_password:
            raise ValueError("Invalid source account password")
        if from_acc.balance < amount:
            raise ValueError("Insufficient balance in source account")

        # 验证转入账户
        to_acc = self.accounts.get(to_account)
        if not to_acc:
            raise ValueError("Destination account not found")

        # 保证币种一致
        if from_acc.currency != to_acc.currency:
            raise ValueError("Currency mismatch between accounts")

        # 执行转账
        from_acc.balance -= amount
        to_acc.balance += amount

        return from_acc.balance

    def get_all_accounts(self) -> Dict[int, Account]:
        """
        获取所有账户（用于调试）

        Returns:
            所有账户的字典
        """
        return self.accounts.copy()
