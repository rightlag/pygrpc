import helloworld_pb2
import unittest

from tests import Loader


class GreeterServiceTestCase(Loader):

    def setUp(self):
        super(GreeterServiceTestCase, self).setUp()
        module = '.helloworld_pb2'
        self.client.load(module, package='tests.helloworld')

    def test_stub_context(self):
        super(GreeterServiceTestCase, self).test_stub_context()

    def test_unary_unary(self):
        res = self.client.request('SayHello', name='you')
        self.assertTrue(isinstance(res, helloworld_pb2.HelloReply))
        # Response message should read 'Hello, you!'.
        self.assertEqual(res.message, 'Hello, you!')
        res = self.client.request('SayHello')
        self.assertTrue(isinstance(res, helloworld_pb2.HelloReply))
        # Response message should read 'Hello, !'.
        self.assertEqual(res.message, 'Hello, !')

    def test_exception_invalid_rpc(self):
        with self.assertRaises(AttributeError):
            self.client.request('SayGoodbye', name='you')

    def tearDown(self):
        del self.client

if __name__ == '__main__':
    unittest.main()
