import route_guide_pb2
import unittest

from tests import Loader
from pygrpc.exceptions import InvalidCardinalityError


class RouteGuideServiceTestCase(Loader):

    def setUp(self):
        super(RouteGuideServiceTestCase, self).setUp()
        module = '.route_guide_pb2'
        self._client.load(module, package='tests.route_guide')

    def test_stub_context(self):
        super(RouteGuideServiceTestCase, self).test_stub_context()

    def test_unary_unary(self):
        res = self._client.unary_unary('GetFeature', latitude=409146138,
                                       longitude=(-746188906))
        self.assertTrue(isinstance(res, route_guide_pb2.Feature))
        # Response message should contain a `Feature` object.
        self.assertEqual(res.name, 'Berkshire Valley Management Area Trail, Jefferson, NJ, USA')
        self.assertEqual(res.location.latitude, 409146138)
        self.assertEqual(res.location.longitude, (-746188906))

    def test_exception_unary_unary(self):
        with self.assertRaises(InvalidCardinalityError):
            # The cardinality of the `GetFeature' RPC request is
            # 'UNARY_UNARY', therefore, any other cardinality method
            # should raise an `InvalidCardinalityError`.
            coords = {
                'latitude': 409146138,
                'longitude': (-746188906),
            }
            self._client.unary_stream('GetFeature', **coords)
            self._client.stream_unary('GetFeature', **coords)
            self._client.stream_stream('GetFeature', **coords)

if __name__ == '__main__':
    unittest.main()
