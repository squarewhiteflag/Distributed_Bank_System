"""
消息编解码模块
手动实现所有数据类型的序列化和反序列化
禁止使用pickle、json等高级序列化工具
"""

import struct
from typing import Tuple


class Marshaller:
    """消息编解码器"""

    @staticmethod
    def pack_int(value: int) -> bytes:
        """
        打包整型（网络字节序）

        Args:
            value: 要打包的整数值

        Returns:
            4字节的字节数组
        """
        return struct.pack('!I', value)

    @staticmethod
    def unpack_int(data: bytes, offset: int = 0) -> Tuple[int, int]:
        """
        解包整型

        Args:
            data: 字节数组
            offset: 起始偏移量

        Returns:
            (整数值, 新偏移量)
        """
        value = struct.unpack('!I', data[offset:offset+4])[0]
        return value, offset + 4

    @staticmethod
    def pack_float(value: float) -> bytes:
        """
        打包浮点型（网络字节序）

        Args:
            value: 要打包的浮点数值

        Returns:
            4字节的字节数组
        """
        return struct.pack('!f', value)

    @staticmethod
    def unpack_float(data: bytes, offset: int = 0) -> Tuple[float, int]:
        """
        解包浮点型

        Args:
            data: 字节数组
            offset: 起始偏移量

        Returns:
            (浮点数值, 新偏移量)
        """
        value = struct.unpack('!f', data[offset:offset+4])[0]
        return value, offset + 4

    @staticmethod
    def pack_string(value: str, fixed_length: int = None) -> bytes:
        """
        打包字符串

        Args:
            value: 要打包的字符串
            fixed_length: 如果指定，则为定长字符串；否则为变长字符串

        Returns:
            打包后的字节数组
        """
        encoded = value.encode('utf-8')
        if fixed_length:
            # 定长字符串：填充到指定长度
            return encoded.ljust(fixed_length, b'\x00')[:fixed_length]
        else:
            # 变长字符串：4字节长度 + 内容
            length = len(encoded)
            return struct.pack('!I', length) + encoded

    @staticmethod
    def unpack_string(data: bytes, offset: int = 0, fixed_length: int = None) -> Tuple[str, int]:
        """
        解包字符串

        Args:
            data: 字节数组
            offset: 起始偏移量
            fixed_length: 如果指定，则按定长解包；否则按变长解包

        Returns:
            (字符串, 新偏移量)
        """
        if fixed_length:
            # 定长字符串
            raw = data[offset:offset+fixed_length]
            value = raw.rstrip(b'\x00').decode('utf-8')
            return value, offset + fixed_length
        else:
            # 变长字符串
            length = struct.unpack('!I', data[offset:offset+4])[0]
            offset += 4
            value = data[offset:offset+length].decode('utf-8')
            return value, offset + length


class RequestBuilder:
    """请求消息构建器"""

    def __init__(self, request_id: int, operation: int):
        """
        初始化请求构建器

        Args:
            request_id: 请求ID
            operation: 操作类型
        """
        self.request_id = request_id
        self.operation = operation
        self.payload = b''

    def add_int(self, value: int) -> 'RequestBuilder':
        """添加整型参数"""
        self.payload += Marshaller.pack_int(value)
        return self

    def add_float(self, value: float) -> 'RequestBuilder':
        """添加浮点型参数"""
        self.payload += Marshaller.pack_float(value)
        return self

    def add_string(self, value: str, fixed_length: int = None) -> 'RequestBuilder':
        """添加字符串参数"""
        self.payload += Marshaller.pack_string(value, fixed_length)
        return self

    def build(self) -> bytes:
        """
        构建完整请求消息

        消息格式：
        [Request ID (4 bytes)] [Operation Type (4 bytes)] [Payload Length (4 bytes)] [Payload]

        Returns:
            完整的字节数组
        """
        header = (
            Marshaller.pack_int(self.request_id) +
            Marshaller.pack_int(self.operation) +
            Marshaller.pack_int(len(self.payload))
        )
        return header + self.payload


class ResponseBuilder:
    """响应消息构建器"""

    def __init__(self, request_id: int, status: int):
        """
        初始化响应构建器

        Args:
            request_id: 对应的请求ID
            status: 响应状态码
        """
        self.request_id = request_id
        self.status = status
        self.payload = b''

    def add_int(self, value: int) -> 'ResponseBuilder':
        """添加整型数据"""
        self.payload += Marshaller.pack_int(value)
        return self

    def add_float(self, value: float) -> 'ResponseBuilder':
        """添加浮点型数据"""
        self.payload += Marshaller.pack_float(value)
        return self

    def add_string(self, value: str, fixed_length: int = None) -> 'ResponseBuilder':
        """添加字符串数据"""
        self.payload += Marshaller.pack_string(value, fixed_length)
        return self

    def build(self) -> bytes:
        """
        构建完整响应消息

        消息格式：
        [Request ID (4 bytes)] [Status (4 bytes)] [Payload Length (4 bytes)] [Payload]

        Returns:
            完整的字节数组
        """
        header = (
            Marshaller.pack_int(self.request_id) +
            Marshaller.pack_int(self.status) +
            Marshaller.pack_int(len(self.payload))
        )
        return header + self.payload
