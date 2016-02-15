import random
import route_guide_pb2
import route_guide_resources
import time
import unittest

from tests import Loader
from pygrpc.exceptions import InvalidCardinalityError


class RouteGuideServiceTestCase(Loader):
    _TIMEOUT = 30

    def setUp(self):
        super(RouteGuideServiceTestCase, self).setUp()
        module = '.route_guide_pb2'
        self._client.load(module, package='tests.route_guide')

    def generate_route(self, features):
        for _ in xrange(10):
            random_feature = features[random.randint(0, len(features) - 1)]
            yield random_feature.location
            time.sleep(random.uniform(0.5, 1.5))

    def make_route_note(self, message, latitude, longitude):
        return route_guide_pb2.RouteNote(
            message=message,
            location=route_guide_pb2.Point(
                latitude=latitude,
                longitude=longitude
            )
        )

    def generate_messages(self):
        messages = [
            self.make_route_note('First message', 0, 0),
            self.make_route_note('Second message', 0, 1),
            self.make_route_note('Third message', 1, 0),
            self.make_route_note('Fourth message', 0, 0),
            self.make_route_note('Fifth message', 1, 0),
        ]
        for message in messages:
            yield message
            time.sleep(random.uniform(0.5, 1.0))

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

    def test_unary_stream(self):
        params = {
            'lo': route_guide_pb2.Point(
                latitude=400000000, longitude=(-750000000)
            ),
            'hi': route_guide_pb2.Point(
                latitude=420000000, longitude=(-730000000)
            ),
        }
        responses = self._client.unary_stream('ListFeatures',
                                              timeout=self._TIMEOUT, **params)
        for response in responses:
            self.assertTrue(
                (400000000 < response.location.latitude < 420000000)
            )
            self.assertTrue(
                (-750000000) < response.location.longitude < (-730000000)
            )
            self.assertTrue(isinstance(response, route_guide_pb2.Feature))

    def test_stream_unary(self):
        feature_list = route_guide_resources.read_route_guide_database()
        route_iter = self.generate_route(feature_list)
        res = self._client.stream_unary('RecordRoute', route_iter,
                                        timeout=self._TIMEOUT)
        self.assertTrue(isinstance(res, route_guide_pb2.RouteSummary))

    def test_stream_stream(self):
        responses = self._client.stream_stream('RouteChat',
                                               self.generate_messages(),
                                               timeout=self._TIMEOUT)
        for response in responses:
            self.assertTrue(isinstance(response, route_guide_pb2.RouteNote))

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

    def tearDown(self):
        del self._client

if __name__ == '__main__':
    unittest.main()
