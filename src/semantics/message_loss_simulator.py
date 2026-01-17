"""
消息丢失模拟模块
用于测试调用语义的容错能力
"""

import random


class MessageLossSimulator:
    """消息丢失模拟器"""

    def __init__(self, loss_rate: float = 0.0):
        """
        初始化消息丢失模拟器

        Args:
            loss_rate: 丢包率（0.0到1.0之间），例如0.3表示30%的丢包率
        """
        if not 0.0 <= loss_rate <= 1.0:
            raise ValueError("Loss rate must be between 0.0 and 1.0")
        self.loss_rate = loss_rate
        random.seed()  # 使用当前时间作为随机种子

    def should_send(self) -> bool:
        """
        判断是否应该发送消息

        Returns:
            True如果应该发送，False如果应该丢弃
        """
        return random.random() >= self.loss_rate

    def set_loss_rate(self, loss_rate: float):
        """
        设置新的丢包率

        Args:
            loss_rate: 新的丢包率（0.0到1.0之间）
        """
        if not 0.0 <= loss_rate <= 1.0:
            raise ValueError("Loss rate must be between 0.0 and 1.0")
        self.loss_rate = loss_rate

    def get_loss_rate(self) -> float:
        """
        获取当前丢包率

        Returns:
            当前丢包率
        """
        return self.loss_rate
