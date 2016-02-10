import importlib

from grpc.beta import implementations
from grpc.framework.common import cardinality as _cardinality
from decorators import method
from exceptions import InvalidCardinalityError


class Client(object):
    StubSuffix = '_stub'
    DefaultTimeout = 10

    def __init__(self, host, port, channel_credentials=None):
        """
        :type host: str
        :param host: The name of the remote host to which to connect.

        :type port: int
        :param port: The port of the remote host to which to connect.
        """
        if channel_credentials is None:
            # Create an `insecure_channel`.
            channel = implementations.insecure_channel(host, port)
        else:
            # Create a `secure_channel`.
            channel = implementations.secure_channel(host, port,
                                                     channel_credentials)
        self._channel = channel
        self._stubs = []

    @property
    def stubs(self):
        return self._stubs

    @stubs.setter
    def stubs(self, value):
        self._stubs = value

    def load(self, name, package=None):
        """Load the Google Protocol Buffer module and generate the
        associated stub objects.
        """
        module = importlib.import_module(name, package=package)
        stubs = []
        for attr in module.__dict__.iterkeys():
            if attr.endswith(self.StubSuffix):
                # Instantiate `_AutoIntermediary` object and append it
                # to the `stubs` list object.
                stub = getattr(module, attr)(self._channel)
                stubs.append(stub)
        self._stubs = stubs

    def _request(self, request, serializer, timeout=DefaultTimeout, **kwargs):
        """An abstract method for issuing RPC requests."""
        if self._stubs:
            for stub in self._stubs:
                group = stub._delegate._group
                try:
                    # The cardinality of the RPC request.
                    _cardinality = stub._delegate._cardinalities[request]
                    # The cardinality specified in the decorator method.
                    cardinality = kwargs.pop('cardinality')
                    if cardinality.name != _cardinality.name:
                        raise InvalidCardinalityError(cardinality.name)
                    obj = getattr(stub, request)
                    if 'timeout' in kwargs:
                        # Override the default `timeout` value if
                        # specified when issuing the RPC request.
                        timeout = kwargs.pop('timeout')
                    res = obj.__call__(serializer(**kwargs), timeout)
                    return res
                except AttributeError:
                    continue
                finally:
                    # Destroy the thread associated with the stub.
                    stub.__del__()
            else:
                raise AttributeError('{} object has no attribute "{}"!'
                                     .format(group, request))
        else:
            # `_stubs` object is an empty list, therefore, return
            # `None`.
            return None

    @method(_cardinality.Cardinality.UNARY_UNARY)
    def unary_unary(self, *args, **kwargs):
        """A simple RPC where the client sends a request to the server
        using the stub and waits for a response to come back, just like
        a normal function call.
        """
        res = self._request(*args, **kwargs)
        return res

    @method(_cardinality.Cardinality.UNARY_STREAM)
    def unary_stream(self, *args, **kwargs):
        """A response-streaming RPC where the client sends a request to
        the server and gets a stream to read a sequence of messages
        back.
        """
        res = self._request(*args, **kwargs)
        return res

    @method(_cardinality.Cardinality.STREAM_UNARY)
    def stream_unary(self, *args, **kwargs):
        """A request-streaming RPC where the client writes a sequence of
        messages and sends them to the server, again using a provided
        stream.
        """
        res = self._request(*args, **kwargs)
        return res

    @method(_cardinality.Cardinality.STREAM_STREAM)
    def stream_stream(self, *args, **kwargs):
        """A bidirectionally-streaming RPC where both sides send a
        sequence of messages using a read-write stream.
        """
        res = self._request(*args, **kwargs)
        return res

    def __str__(self):
        return '<{!s}>'.format(self.__class__.__name__)

    def __repr__(self):
        return '<{!r}>'.format(self.__class__.__name__)
