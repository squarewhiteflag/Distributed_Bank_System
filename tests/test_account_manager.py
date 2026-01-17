"""
账户管理单元测试
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.server.account_manager import AccountManager, Account
from src.common.protocol import CurrencyType


class TestAccountManager(unittest.TestCase):
    """测试AccountManager"""

    def setUp(self):
        """测试前设置"""
        self.manager = AccountManager()

    def test_create_account(self):
        """测试创建账户"""
        account_number = self.manager.create_account(
            name="Alice",
            password="password123",
            currency=CurrencyType.USD,
            initial_balance=1000.0
        )

        # 验证账户号
        self.assertEqual(account_number, 10001)

        # 验证账户信息
        account = self.manager.get_account(account_number)
        self.assertIsNotNone(account)
        self.assertEqual(account.name, "Alice")
        self.assertEqual(account.password, "password123")
        self.assertEqual(account.currency, CurrencyType.USD)
        self.assertAlmostEqual(account.balance, 1000.0, places=4)

    def test_create_multiple_accounts(self):
        """测试创建多个账户"""
        acc1 = self.manager.create_account("Alice", "pass1", CurrencyType.USD, 1000.0)
        acc2 = self.manager.create_account("Bob", "pass2", CurrencyType.EUR, 2000.0)
        acc3 = self.manager.create_account("Charlie", "pass3", CurrencyType.SGD, 3000.0)

        # 验证账户号递增
        self.assertEqual(acc1, 10001)
        self.assertEqual(acc2, 10002)
        self.assertEqual(acc3, 10003)

        # 验证所有账户都存在
        self.assertIsNotNone(self.manager.get_account(acc1))
        self.assertIsNotNone(self.manager.get_account(acc2))
        self.assertIsNotNone(self.manager.get_account(acc3))

    def test_deposit(self):
        """测试存款"""
        account_number = self.manager.create_account(
            "Alice", "pass123", CurrencyType.USD, 1000.0
        )

        # 存款
        new_balance = self.manager.deposit(account_number, "pass123", 500.0)

        # 验证余额
        self.assertAlmostEqual(new_balance, 1500.0, places=4)
        account = self.manager.get_account(account_number)
        self.assertAlmostEqual(account.balance, 1500.0, places=4)

    def test_deposit_wrong_password(self):
        """测试存款时密码错误"""
        account_number = self.manager.create_account(
            "Alice", "pass123", CurrencyType.USD, 1000.0
        )

        # 密码错误应该抛出异常
        with self.assertRaises(ValueError) as context:
            self.manager.deposit(account_number, "wrongpass", 500.0)
        self.assertIn("password", str(context.exception).lower())

    def test_deposit_nonexistent_account(self):
        """测试向不存在的账户存款"""
        with self.assertRaises(ValueError) as context:
            self.manager.deposit(99999, "pass123", 500.0)
        self.assertIn("not found", str(context.exception).lower())

    def test_withdraw(self):
        """测试取款"""
        account_number = self.manager.create_account(
            "Alice", "pass123", CurrencyType.USD, 1000.0
        )

        # 取款
        new_balance = self.manager.withdraw(account_number, "pass123", 300.0)

        # 验证余额
        self.assertAlmostEqual(new_balance, 700.0, places=4)
        account = self.manager.get_account(account_number)
        self.assertAlmostEqual(account.balance, 700.0, places=4)

    def test_withdraw_insufficient_balance(self):
        """测试余额不足时取款"""
        account_number = self.manager.create_account(
            "Alice", "pass123", CurrencyType.USD, 1000.0
        )

        # 余额不足应该抛出异常
        with self.assertRaises(ValueError) as context:
            self.manager.withdraw(account_number, "pass123", 1500.0)
        self.assertIn("insufficient", str(context.exception).lower())

    def test_withdraw_wrong_password(self):
        """测试取款时密码错误"""
        account_number = self.manager.create_account(
            "Alice", "pass123", CurrencyType.USD, 1000.0
        )

        with self.assertRaises(ValueError) as context:
            self.manager.withdraw(account_number, "wrongpass", 300.0)
        self.assertIn("password", str(context.exception).lower())

    def test_close_account(self):
        """测试销户"""
        account_number = self.manager.create_account(
            "Alice", "pass123", CurrencyType.USD, 1000.0
        )

        # 销户
        result = self.manager.close_account(account_number, "Alice", "pass123")
        self.assertTrue(result)

        # 验证账户已删除
        account = self.manager.get_account(account_number)
        self.assertIsNone(account)

    def test_close_account_wrong_password(self):
        """测试销户时密码错误"""
        account_number = self.manager.create_account(
            "Alice", "pass123", CurrencyType.USD, 1000.0
        )

        with self.assertRaises(ValueError) as context:
            self.manager.close_account(account_number, "Alice", "wrongpass")
        self.assertIn("password", str(context.exception).lower())

    def test_close_account_wrong_name(self):
        """测试销户时姓名不匹配"""
        account_number = self.manager.create_account(
            "Alice", "pass123", CurrencyType.USD, 1000.0
        )

        with self.assertRaises(ValueError) as context:
            self.manager.close_account(account_number, "Bob", "pass123")
        self.assertIn("not owned", str(context.exception).lower())

    def test_verify_password(self):
        """测试密码验证"""
        account_number = self.manager.create_account(
            "Alice", "pass123", CurrencyType.USD, 1000.0
        )

        # 正确密码
        self.assertTrue(self.manager.verify_password(account_number, "pass123"))

        # 错误密码
        self.assertFalse(self.manager.verify_password(account_number, "wrongpass"))

        # 不存在的账户
        self.assertFalse(self.manager.verify_password(99999, "pass123"))

    def test_transfer(self):
        """测试转账"""
        from_acc = self.manager.create_account("Alice", "pass1", CurrencyType.USD, 1000.0)
        to_acc = self.manager.create_account("Bob", "pass2", CurrencyType.USD, 500.0)

        # 转账
        new_balance = self.manager.transfer(from_acc, "pass1", to_acc, 300.0)

        # 验证余额
        self.assertAlmostEqual(new_balance, 700.0, places=4)
        self.assertAlmostEqual(self.manager.get_account(from_acc).balance, 700.0, places=4)
        self.assertAlmostEqual(self.manager.get_account(to_acc).balance, 800.0, places=4)

    def test_transfer_insufficient_balance(self):
        """测试余额不足时转账"""
        from_acc = self.manager.create_account("Alice", "pass1", CurrencyType.USD, 1000.0)
        to_acc = self.manager.create_account("Bob", "pass2", CurrencyType.USD, 500.0)

        with self.assertRaises(ValueError) as context:
            self.manager.transfer(from_acc, "pass1", to_acc, 1500.0)
        self.assertIn("insufficient", str(context.exception).lower())

    def test_transfer_wrong_password(self):
        """测试转账时密码错误"""
        from_acc = self.manager.create_account("Alice", "pass1", CurrencyType.USD, 1000.0)
        to_acc = self.manager.create_account("Bob", "pass2", CurrencyType.USD, 500.0)

        with self.assertRaises(ValueError) as context:
            self.manager.transfer(from_acc, "wrongpass", to_acc, 300.0)
        self.assertIn("password", str(context.exception).lower())


if __name__ == '__main__':
    unittest.main()
