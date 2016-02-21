# pygrpc

pygrpc 0.2.0

Released: Feb-10-2015

# Overview

`pygrpc` is a Python module that provides a high-level client connection object to instantiate [Google Remote Procedure Calls](http://www.grpc.io/) (gRPCs).

# Examples

By default, the [Google Protocol Buffer compiler](http://www.grpc.io/docs/tutorials/basic/python.html#generating-client-and-server-code) generates client and server code.

The following example is a code snippet provided by Google that creates a `helloworld.Greeter` stub object and invokes the `SayHello` method. The `SayHello` method takes a serializer class as its first argument (`helloworld_pb2.HelloRequest`):

```python
"""The Python implementation of the GRPC helloworld.Greeter client."""

from grpc.beta import implementations

import helloworld_pb2

_TIMEOUT_SECONDS = 10

channel = implementations.insecure_channel('localhost', 50051)
stub = helloworld_pb2.beta_create_Greeter_stub(channel)
response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'), _TIMEOUT_SECONDS)
print "Greeter client received: " + response.message
```

The following example demonstrates the same request using `pygrpc`:

```python
from pygrpc import Client

client = Client('localhost', 50051)
# This loads the generated Google Protocol Buffer module.
client.load('helloworld_pb2')
response = client.request('SayHello', name='you')
print "Greeter client received: " + response.message
```

Both examples would output: `Greeter client received: Hello, you!`.

# Differences

The `pygrpc` client only requires the `request` method to be called for issuing gRPC requests.

### pygrpc.Client

`client.request(request, *args, **kwargs)`

Return a simple RPC response or a streaming RPC response. This is known as the [cardinality](https://github.com/grpc/grpc/blob/master/src/python/grpcio/grpc/framework/common/cardinality.py) of the gRPC request/response.

**Type:** `str`

**Parameters:** **request** - the name of the RPC request defined in the `.proto` file.

**Return type:** Reply object defined in the `.proto` file.

**Returns:** Either a simple RPC response or a streaming RPC response.
