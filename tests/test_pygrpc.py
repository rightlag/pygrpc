import helloworld_pb2
import unittest

from grpc.beta._stub import _AutoIntermediary
from pygrpc import Client


class GRPCTestCase(unittest.TestCase):
    HOST = 'localhost'
    PORT = 50051

    def setUp(self):
        self.client = Client(self.HOST, self.PORT)


class HelloWorldTestCase(GRPCTestCase):
    """Run the `helloworld_pb2` module test cases. In order for these
    tests to pass, the `greeter_server` module *must* be running.

    The `helloworld_pb2` module is generated via the Google Protocol
    Buffer Compiler. More information can be found [here](https://github.com/google/protobuf#protocol-compiler-installation).
    """

    module = '.helloworld_pb2'

    def setUp(self):
        super(HelloWorldTestCase, self).setUp()
        self.client.load(self.module, package='tests')

    def test_returned_helloworld_pb2_stub_functions(self):
        for stub in self.client.stubs:
            self.assertTrue(isinstance(stub, _AutoIntermediary))

    def test_say_hello_message_response(self):
        res = self.client.unary_unary('SayHello', helloworld_pb2.HelloRequest,
                                      name='you')
        self.assertEqual(res.message, 'Hello, you!')
