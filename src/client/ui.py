"""
客户端用户界面模块
提供命令行交互菜单
"""


class ClientUI:
    """客户端用户界面"""

    @staticmethod
    def _get_int_input(prompt: str, min_val: int = None, max_val: int = None) -> int:
        """
        获取整数输入，带验证循环

        Args:
            prompt: 提示信息
            min_val: 最小值（可选）
            max_val: 最大值（可选）

        Returns:
            用户输入的有效整数
        """
        while True:
            try:
                value = int(input(prompt))
                if min_val is not None and value < min_val:
                    print(f"Input must be at least {min_val}. Please try again.")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Input must be at most {max_val}. Please try again.")
                    continue
                return value
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    @staticmethod
    def _get_float_input(prompt: str, min_val: float = 0.0) -> float:
        """
        获取浮点数输入，带验证循环

        Args:
            prompt: 提示信息
            min_val: 最小值（默认为 0）

        Returns:
            用户输入的有效浮点数
        """
        while True:
            try:
                value = float(input(prompt))
                if value < min_val:
                    print(f"Input must be at least {min_val}. Please try again.")
                    continue
                return value
            except ValueError:
                print("Invalid input. Please enter a valid number.")

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
        currency = ClientUI._get_int_input("Enter currency type: ", min_val=1, max_val=4)

        initial_balance = ClientUI._get_float_input("Enter initial balance: ")

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
        account_number = ClientUI._get_int_input("Enter account number: ", min_val=1)
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
        account_number = ClientUI._get_int_input("Enter account number: ", min_val=1)
        password = input("Enter password: ").ljust(16)[:16]

        print("Currency types: 1=USD, 2=EUR, 3=SGD, 4=CNY")
        currency = ClientUI._get_int_input("Enter currency type: ", min_val=1, max_val=4)

        amount = ClientUI._get_float_input("Enter amount to deposit: ")

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
        account_number = ClientUI._get_int_input("Enter account number: ", min_val=1)
        password = input("Enter password: ").ljust(16)[:16]

        print("Currency types: 1=USD, 2=EUR, 3=SGD, 4=CNY")
        currency = ClientUI._get_int_input("Enter currency type: ", min_val=1, max_val=4)

        amount = ClientUI._get_float_input("Enter amount to withdraw: ")

        return name, account_number, password, currency, amount

    @staticmethod
    def get_query_account_info():
        """
        获取查询账户信息

        Returns:
            (account_number, password)
        """
        print("\n--- Query Account ---")
        account_number = ClientUI._get_int_input("Enter account number: ", min_val=1)
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
        from_account = ClientUI._get_int_input("Enter source account number: ", min_val=1)
        password = input("Enter source account password: ").ljust(16)[:16]
        to_account = ClientUI._get_int_input("Enter destination account number: ", min_val=1)
        amount = ClientUI._get_float_input("Enter amount to transfer: ")

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
        duration = ClientUI._get_int_input("Enter monitoring duration in seconds (10-500): ", min_val=10, max_val=500)

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
