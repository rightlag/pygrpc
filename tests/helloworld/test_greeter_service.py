import helloworld_pb2
import unittest

from tests import Loader


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

if __name__ == '__main__':
    unittest.main()
