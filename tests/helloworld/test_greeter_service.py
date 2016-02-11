import helloworld_pb2
import unittest

from tests import Loader
from pygrpc.exceptions import InvalidCardinalityError


class GreeterServiceTestCase(Loader):

    def setUp(self):
        super(GreeterServiceTestCase, self).setUp()
        module = '.helloworld_pb2'
        self._client.load(module, package='tests.helloworld')

    def test_stub_context(self):
        super(GreeterServiceTestCase, self).test_stub_context()

    def test_unary_unary(self):
        res = self._client.unary_unary('SayHello', name='you')
        self.assertTrue(isinstance(res, helloworld_pb2.HelloReply))
        # Response message should read 'Hello, you!'.
        self.assertEqual(res.message, 'Hello, you!')
        res = self._client.unary_unary('SayHello')
        self.assertTrue(isinstance(res, helloworld_pb2.HelloReply))
        # Response message should read 'Hello, !'.
        self.assertEqual(res.message, 'Hello, !')

    def test_exception_unary_unary(self):
        with self.assertRaises(InvalidCardinalityError):
            # The cardinality of the `SayHello' RPC request is
            # 'UNARY_UNARY', therefore, any other cardinality method
            # should raise an `InvalidCardinalityError`.
            self._client.unary_stream('SayHello', name='you')
            self._client.stream_unary('SayHello', name='you')
            self._client.stream_stream('SayHello', name='you')

    def test_exception_invalid_rpc(self):
        with self.assertRaises(AttributeError):
            self._client.unary_unary('SayGoodbye', name='you')

if __name__ == '__main__':
    unittest.main()
