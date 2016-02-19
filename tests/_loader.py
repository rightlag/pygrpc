import unittest

from grpc.beta._stub import _AutoIntermediary
from pygrpc import Client


class Loader(unittest.TestCase):

    HOST = 'localhost'
    PORT = 50051

    def setUp(self):
        self.client = Client(self.HOST, self.PORT)

    def test_stub_context(self):
        for stub in self.client.stubs:
            self.assertTrue(isinstance(stub, _AutoIntermediary))
