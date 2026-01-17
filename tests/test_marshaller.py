"""
消息编解码单元测试
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.common.marshaller import Marshaller, RequestBuilder, ResponseBuilder
from src.common.protocol import OperationType, ResponseStatus


class TestMarshaller(unittest.TestCase):
    """测试Marshaller基础功能"""

    def test_pack_unpack_int(self):
        """测试整型编解码"""
        original = 12345
        packed = Marshaller.pack_int(original)
        unpacked, _ = Marshaller.unpack_int(packed)
        self.assertEqual(original, unpacked)

    def test_pack_unpack_float(self):
        """测试浮点型编解码"""
        original = 1234.56
        packed = Marshaller.pack_float(original)
        unpacked, _ = Marshaller.unpack_float(packed)
        # 浮点数可能有微小精度差异（单精度浮点）
        self.assertAlmostEqual(original, unpacked, places=3)

    def test_pack_unpack_string_fixed_length(self):
        """测试定长字符串编解码"""
        original = "Hello"
        packed = Marshaller.pack_string(original, fixed_length=10)
        unpacked, _ = Marshaller.unpack_string(packed, fixed_length=10)
        self.assertEqual(original, unpacked)

    def test_pack_unpack_string_variable_length(self):
        """测试变长字符串编解码"""
        original = "Hello, 世界!"
        packed = Marshaller.pack_string(original)
        unpacked, _ = Marshaller.unpack_string(packed)
        self.assertEqual(original, unpacked)

    def test_pack_unpack_chinese_string(self):
        """测试中文字符串编解码"""
        original = "张三李四"
        packed = Marshaller.pack_string(original)
        unpacked, _ = Marshaller.unpack_string(packed)
        self.assertEqual(original, unpacked)


class TestRequestBuilder(unittest.TestCase):
    """测试RequestBuilder"""

    def test_simple_request(self):
        """测试简单请求构建"""
        request_id = 100
        operation = OperationType.OPEN_ACCOUNT

        request = (RequestBuilder(request_id, operation)
                   .add_string("Alice")
                   .add_string("password123", fixed_length=16)
                   .add_int(1)  # USD
                   .add_float(1000.0)
                   .build())

        # 验证请求头
        unpacked_id, offset = Marshaller.unpack_int(request, 0)
        unpacked_op, offset = Marshaller.unpack_int(request, offset)
        payload_len, offset = Marshaller.unpack_int(request, offset)

        self.assertEqual(request_id, unpacked_id)
        self.assertEqual(operation, unpacked_op)
        self.assertGreater(payload_len, 0)

        # 验证payload
        name, offset = Marshaller.unpack_string(request, offset)
        password, offset = Marshaller.unpack_string(request, offset, fixed_length=16)
        currency, offset = Marshaller.unpack_int(request, offset)
        balance, _ = Marshaller.unpack_float(request, offset)

        self.assertEqual("Alice", name)
        self.assertEqual("password123", password)
        self.assertEqual(1, currency)
        self.assertAlmostEqual(1000.0, balance, places=4)


class TestResponseBuilder(unittest.TestCase):
    """测试ResponseBuilder"""

    def test_simple_response(self):
        """测试简单响应构建"""
        request_id = 100
        status = ResponseStatus.SUCCESS
        account_number = 12345

        response = (ResponseBuilder(request_id, status)
                    .add_int(account_number)
                    .build())

        # 验证响应头
        unpacked_id, offset = Marshaller.unpack_int(response, 0)
        unpacked_status, offset = Marshaller.unpack_int(response, offset)
        payload_len, offset = Marshaller.unpack_int(response, offset)

        self.assertEqual(request_id, unpacked_id)
        self.assertEqual(status, unpacked_status)
        self.assertGreater(payload_len, 0)

        # 验证payload
        unpacked_account, _ = Marshaller.unpack_int(response, offset)
        self.assertEqual(account_number, unpacked_account)


class TestComplexMessages(unittest.TestCase):
    """测试复杂消息"""

    def test_query_account_request(self):
        """测试查询账户请求"""
        request_id = 200
        account_number = 10001
        password = "testpass"

        request = (RequestBuilder(request_id, OperationType.QUERY_ACCOUNT)
                   .add_int(account_number)
                   .add_string(password, fixed_length=16)
                   .build())

        # 解析并验证
        unpacked_id, offset = Marshaller.unpack_int(request, 0)
        unpacked_op, offset = Marshaller.unpack_int(request, offset)
        _, offset = Marshaller.unpack_int(request, offset)  # payload length

        unpacked_account, offset = Marshaller.unpack_int(request, offset)
        unpacked_password, _ = Marshaller.unpack_string(request, offset, fixed_length=16)

        self.assertEqual(request_id, unpacked_id)
        self.assertEqual(OperationType.QUERY_ACCOUNT, unpacked_op)
        self.assertEqual(account_number, unpacked_account)
        self.assertEqual(password, unpacked_password)

    def test_transfer_request(self):
        """测试转账请求"""
        request_id = 300
        from_account = 10001
        password = "mypass123"
        to_account = 10002
        amount = 500.0

        request = (RequestBuilder(request_id, OperationType.TRANSFER)
                   .add_int(from_account)
                   .add_string(password, fixed_length=16)
                   .add_int(to_account)
                   .add_float(amount)
                   .build())

        # 解析并验证
        unpacked_id, offset = Marshaller.unpack_int(request, 0)
        unpacked_op, offset = Marshaller.unpack_int(request, offset)
        _, offset = Marshaller.unpack_int(request, offset)  # payload length

        unpacked_from, offset = Marshaller.unpack_int(request, offset)
        unpacked_pass, offset = Marshaller.unpack_string(request, offset, fixed_length=16)
        unpacked_to, offset = Marshaller.unpack_int(request, offset)
        unpacked_amount, _ = Marshaller.unpack_float(request, offset)

        self.assertEqual(request_id, unpacked_id)
        self.assertEqual(OperationType.TRANSFER, unpacked_op)
        self.assertEqual(from_account, unpacked_from)
        self.assertEqual(password, unpacked_pass)
        self.assertEqual(to_account, unpacked_to)
        self.assertAlmostEqual(amount, unpacked_amount, places=4)


if __name__ == '__main__':
    unittest.main()
