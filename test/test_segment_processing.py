'''
Copyright 2026 Tamas Bolner

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import unittest
from mock.mock_config_parser1 import MockConfigParser1
from segment_processing import SegmentProcessing
from primitives.segment import Segment

class TestSegmentProcessing(unittest.TestCase):
    def test_segment_processing(self):
        config = MockConfigParser1()
        proc = SegmentProcessing(config)
        list = [
            Segment(1, " First\n\nSentence.  ", 0, 0),
            Segment(2, "[THIS WILL GET REMOVED]", 0, 0),
            Segment(3, "\nLast  \t  Sentence.\t", 0, 0)
        ]

        proc.process(list)

        self.assertEqual(list[0].get_source_text(), "First Sentence.",
            "Processing the first sentence failed.")
