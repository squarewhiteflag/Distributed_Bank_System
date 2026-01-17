"""
客户端用户界面模块
提供命令行交互菜单
"""


class ClientUI:
    """客户端用户界面"""

    @staticmethod
    def display_menu():
        """显示主菜单"""
        print("\n" + "="*50)
        print("Distributed Banking System - Client")
        print("="*50)
        print("1. Open Account")
        print("2. Close Account")
        print("3. Deposit")
        print("4. Withdraw")
        print("5. Query Account (Idempotent Operation)")
        print("6. Transfer (Non-idempotent Operation)")
        print("7. Monitor Account Updates")
        print("0. Exit")
        print("="*50)

    @staticmethod
    def get_user_choice() -> int:
        """
        获取用户选择

        Returns:
            用户选择的菜单项
        """
        try:
            choice = int(input("Enter your choice: "))
            return choice
        except ValueError:
            return -1

    @staticmethod
    def get_open_account_info():
        """
        获取开户信息

        Returns:
            (name, password, currency, initial_balance)
        """
        print("\n--- Open New Account ---")
        name = input("Enter your name: ")
        password = input("Enter password (max 16 chars): ").ljust(16)[:16]

        print("Currency types: 1=USD, 2=EUR, 3=SGD, 4=CNY")
        currency = int(input("Enter currency type: "))

        initial_balance = float(input("Enter initial balance: "))

        return name, password, currency, initial_balance

    @staticmethod
    def get_close_account_info():
        """
        获取销户信息

        Returns:
            (name, account_number, password)
        """
        print("\n--- Close Account ---")
        name = input("Enter your name: ")
        account_number = int(input("Enter account number: "))
        password = input("Enter password: ").ljust(16)[:16]

        return name, account_number, password

    @staticmethod
    def get_deposit_info():
        """
        获取存款信息

        Returns:
            (name, account_number, password, currency, amount)
        """
        print("\n--- Deposit ---")
        name = input("Enter your name: ")
        account_number = int(input("Enter account number: "))
        password = input("Enter password: ").ljust(16)[:16]

        print("Currency types: 1=USD, 2=EUR, 3=SGD, 4=CNY")
        currency = int(input("Enter currency type: "))

        amount = float(input("Enter amount to deposit: "))

        return name, account_number, password, currency, amount

    @staticmethod
    def get_withdraw_info():
        """
        获取取款信息

        Returns:
            (name, account_number, password, currency, amount)
        """
        print("\n--- Withdraw ---")
        name = input("Enter your name: ")
        account_number = int(input("Enter account number: "))
        password = input("Enter password: ").ljust(16)[:16]

        print("Currency types: 1=USD, 2=EUR, 3=SGD, 4=CNY")
        currency = int(input("Enter currency type: "))

        amount = float(input("Enter amount to withdraw: "))

        return name, account_number, password, currency, amount

    @staticmethod
    def get_query_account_info():
        """
        获取查询账户信息

        Returns:
            (account_number, password)
        """
        print("\n--- Query Account ---")
        account_number = int(input("Enter account number: "))
        password = input("Enter password: ").ljust(16)[:16]

        return account_number, password

    @staticmethod
    def get_transfer_info():
        """
        获取转账信息

        Returns:
            (from_account, password, to_account, amount)
        """
        print("\n--- Transfer ---")
        from_account = int(input("Enter source account number: "))
        password = input("Enter source account password: ").ljust(16)[:16]
        to_account = int(input("Enter destination account number: "))
        amount = float(input("Enter amount to transfer: "))

        return from_account, password, to_account, amount

    @staticmethod
    def get_monitor_info():
        """
        获取监控信息

        Returns:
            duration (int): 监控时长（秒）
        """
        print("\n--- Monitor Account Updates ---")
        print("You will receive updates for all account operations during monitoring.")
        duration = int(input("Enter monitoring duration in seconds (10-300): "))

        # 限制范围
        duration = max(10, min(300, duration))

        return duration

    @staticmethod
    def display_success(message: str):
        """显示成功消息"""
        print(f"✓ Success: {message}")

    @staticmethod
    def display_error(message: str):
        """显示错误消息"""
        print(f"✗ Error: {message}")

    @staticmethod
    def display_info(message: str):
        """显示信息消息"""
        print(f"ℹ {message}")

    @staticmethod
    def display_account_update(account_number: int, name: str, currency: int, balance: float):
        """
        显示账户更新通知

        Args:
            account_number: 账户号
            name: 账户持有人姓名
            currency: 货币类型
            balance: 余额
        """
        currency_names = {1: "USD", 2: "EUR", 3: "SGD", 4: "CNY"}
        currency_name = currency_names.get(currency, "Unknown")

        print(f"\n{'='*50}")
        print("Account Update Notification")
        print(f"{'='*50}")
        print(f"Account Number: {account_number}")
        print(f"Name: {name}")
        print(f"Currency: {currency_name}")
        print(f"Balance: {balance:.2f}")
        print(f"{'='*50}\n")
