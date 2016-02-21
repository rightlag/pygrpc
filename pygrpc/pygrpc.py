import importlib
import re

from grpc.beta import implementations
from grpc.framework.common.cardinality import Cardinality


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

    def request(self, request, *args, **kwargs):
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
            # The request serializer key.
            key = (stub._delegate._group, request)
            try:
                # Override the default `timeout` value if specified when
                # issuing the RPC request.
                timeout = kwargs.pop('timeout', self.DefaultTimeout)
                # The `request_or_request_iterator` object determines
                # the type of argument to pass to the object call. It
                # can either be a generator object or the initialized
                # serializer class object.
                cardinality = stub._delegate._cardinalities[request]
                if cardinality.name in (Cardinality.UNARY_UNARY.name,
                                        Cardinality.UNARY_STREAM.name):
                    serializer = request_serializers[key]
                    # The serializer class definition that is to be
                    # instantiated when issuing the RPC request.
                    serializer = serializer.im_class
                    request_or_request_iterator = serializer(**kwargs)
                elif cardinality.name in (Cardinality.STREAM_UNARY.name,
                                          Cardinality.STREAM_STREAM.name):
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

    def __str__(self):
        return '<{!s}>'.format(self.__class__.__name__)

    def __repr__(self):
        return '<{!r}>'.format(self.__class__.__name__)
