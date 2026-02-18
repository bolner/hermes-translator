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
from mock.mock_model1 import MockModel1
from mock.mock_window1 import MockWindow1
from mock.mock_logger import MockLogger1
from translator import Translator
from primitives.segment import Segment

class TestTranslator(unittest.TestCase):
    def test_translation(self):
        config = MockConfigParser1()
        model = MockModel1()
        segments: list[Segment] = [
            Segment(1, "Segment 1.", 0, 0),
            Segment(2, "Segment 2.", 0, 0),
            Segment(3, "Segment 3.", 0, 0),
            Segment(4, "Segment 4.", 0, 0),
            Segment(5, "Segment 5.", 0, 0)
        ]
        window = MockWindow1(segments)
        logger = MockLogger1()
        translator = Translator(model, config, window, logger)
        translator.run()

        self.assertEqual(segments[0].get_target_text(), "Segment 1.", "Invalid translation."
                            f"\nLogs: {logger.get_entries()}")
        
        self.assertEqual(segments[4].get_target_text(), "Segment 5.", "Invalid translation."
                            f"\nLogs: {logger.get_entries()}")
