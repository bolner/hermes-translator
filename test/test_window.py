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
from window import Window
from primitives.segment import Segment

class TestWindow(unittest.TestCase):
    def test_char_overflow(self):
        config = MockConfigParser1()

        self.assertEqual(config.get_max_segments_before(), 3,
            "Expected mock config setting: get_max_segments_before = 3")
        self.assertEqual(config.get_max_segments_after(), 3,
            "Expected mock config setting: get_max_segments_after = 3")
        self.assertEqual(config.get_max_chars_before(), 50,
            "Expected mock config setting: get_max_chars_before = 50")
        self.assertEqual(config.get_max_chars_after(), 50,
            "Expected mock config setting: get_max_chars_after = 50")

        window = Window(config, [
            Segment(1, "Sentence 1.", 0, 0),
            Segment(2, "Sentence 2. Sentence 2. Sentence 2. Sentence 2.", 0, 0),
            Segment(3, "Sentence 3. ", 0, 0),
        ])

        self.assertTrue(window.next(), "window.next stopped after the first step.")
        self.test_window_state(window=window, before=[], current="Sentence 1.",
            after=["Sentence 2. Sentence 2. Sentence 2. Sentence 2."])
        
        self.assertTrue(window.next(), "window.next stopped after the second step.")
        
    
    def test_window_state(self, window: Window, before: list[str], current: str,
                          after: list[str]):
        before = window.get_segments_before_current()
        current = window.get_current_segment()
        after = window.get_segments_after_current()


if __name__ == '__main__':
    unittest.main()
