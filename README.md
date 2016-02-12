# pygrpc

pygrpc 0.1.0

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
response = client.unary_unary('SayHello', name='you')
print "Greeter client received: " + response.message
```

Both examples would output: `Hello, you!`.

### Differences

I tried to make `pygrpc` as simple as possible. Instead of having to specify the request serializer class as one of the arguments when issuing a RPC, it automatically determines it for you. The `unary_unary` method in the example above states the [cardinality](http://www.grpc.io/docs/tutorials/basic/python.html#defining-the-service) of the request.

| Method                        | Cardinality   | Description                                                                                                                  |
|-------------------------------|---------------|------------------------------------------------------------------------------------------------------------------------------|
| simple RPC                    | UNARY_UNARY   | client sends a request to the server using the stub and waits for a response to come back, just like a normal function call. |
| response-streaming RPC        | UNARY_STREAM  | client sends a request to the server and gets a stream to read a sequence of messages back.                                  |
| request-streaming RPC         | STREAM_UNARY  | client writes a sequence of messages and sends them to the server, again using a provided stream.                            |
| bidirectionally-streaming RPC | STREAM_STREAM | both sides send a sequence of messages using a read-write stream.                                                            |

The purpose of defining separate methods to issue RPCs is to enforce proper cardinality. For example, if in the event you attempt to issue a `response-streaming` RPC when the client expects a `simple RPC`, then an `InvalidCardinalityError` exception is raised. This forces the developer to ensure proper cardinality when issuing RPCs.
