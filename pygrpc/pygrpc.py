import importlib
import re

from grpc.beta import implementations
from grpc.framework.common import cardinality as _cardinality
from decorators import method
from exceptions import InvalidCardinalityError


class Client(object):
    DefaultTimeout = 10
    StubRegex = r'^beta_create_.*_stub$'

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
        prog = re.compile(self.StubRegex)
        for attr in module.__dict__.iterkeys():
            match = prog.match(attr)
            if match:
                fn = match.group(0)
                # Instantiate `_AutoIntermediary` object and append it
                # to the `stubs` list object.
                stub = getattr(module, fn)(self._channel)
                stubs.append(stub)
        self._stubs = stubs

    def _request(self, request, *args, **kwargs):
        """An abstract method for issuing RPC requests."""
        if not self._stubs:
            # `_stubs` object is an empty list, therefore, return
            # `None`.
            return None
        for stub in self._stubs:
            group = stub._delegate._group
            # Return a dictionary of serializer classes.
            request_serializers = (
                stub._up.im_self._grpc_link._kernel._request_serializers
            )
            try:
                # The cardinality of the RPC request.
                _cardinality = stub._delegate._cardinalities[request]
                # The cardinality specified in the decorator method.
                cardinality = kwargs.pop('cardinality')
                if cardinality.name != _cardinality.name:
                    raise InvalidCardinalityError(cardinality.name)
                # Override the default `timeout` value if specified when
                # issuing the RPC request.
                timeout = kwargs.pop('timeout', self.DefaultTimeout)
                key = (stub._delegate._group, request)
                serializer = request_serializers[key]
                # The serializer class definition that is to be
                # instantiated when issuing the RPC request.
                serializer = serializer.im_class
                # The `request_or_request_iterator` object determines
                # the type of argument to pass to the object call. It
                # can either be a generator object or the initialized
                # serializer class object.
                if _cardinality.name in ('UNARY_UNARY', 'UNARY_STREAM'):
                    request_or_request_iterator = serializer(**kwargs)
                elif _cardinality.name in ('STREAM_UNARY', 'STREAM_STREAM'):
                    request_or_request_iterator = args[0]
                obj = getattr(stub, request)
                response = obj.__call__(request_or_request_iterator, timeout)
                return response
            except (AttributeError, KeyError):
                continue
        else:
            # The RPC request does not exist in the protocol definition
            # file, therefore, raise an `AttributeError`.
            raise AttributeError('{} object has no attribute "{}"!'
                                 .format(group, request))

    @method(cardinality=_cardinality.Cardinality.UNARY_UNARY)
    def unary_unary(self, *args, **kwargs):
        """A simple RPC where the client sends a request to the server
        using the stub and waits for a response to come back, just like
        a normal function call.
        """
        res = self._request(*args, **kwargs)
        return res

    @method(cardinality=_cardinality.Cardinality.UNARY_STREAM)
    def unary_stream(self, *args, **kwargs):
        """A response-streaming RPC where the client sends a request to
        the server and gets a stream to read a sequence of messages
        back.
        """
        res = self._request(*args, **kwargs)
        return res

    @method(cardinality=_cardinality.Cardinality.STREAM_UNARY)
    def stream_unary(self, *args, **kwargs):
        """A request-streaming RPC where the client writes a sequence of
        messages and sends them to the server, again using a provided
        stream.
        """
        res = self._request(*args, **kwargs)
        return res

    @method(cardinality=_cardinality.Cardinality.STREAM_STREAM)
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
