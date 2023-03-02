from unittest import TestCase

from yfquotetype import shard_range_parser


class TestPassedArguments(TestCase):

    def test_parse_shard_ranges(self):
        fetch_shards = '1-3,20-30'
        allowed_shards = shard_range_parser(fetch_shards)

        self.assertListEqual(allowed_shards, [1, 2, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29])
