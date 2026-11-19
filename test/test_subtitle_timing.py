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
from mock.mock_logger import MockLogger1
from subtitle_timing import SubtitleTiming
from primitives.segment import Segment
from primitives.config_parser_interface import ConfigParserInterface


class MockConfigNoBackwards(ConfigParserInterface):
    """Mock config with backwards adjustment disabled."""

    def get_model_name(self) -> str:
        return "google/madlad400-3b-mt"

    def get_model_type(self) -> str:
        return "madlad"

    def get_model_dtype(self) -> str:
        return "fp16"

    def get_prompt_prefix(self) -> str:
        return "<2{LANG}>"

    def get_sentinel_token_template(self) -> str:
        return "<extra_id_{ID}>"

    def get_inference_batch_size(self) -> int:
        return 4

    def get_max_chars_before(self) -> int:
        return 50

    def get_max_segments_before(self) -> int:
        return 3

    def get_max_chars_after(self) -> int:
        return 50

    def get_max_segments_after(self) -> int:
        return 3

    def get_target_language(self) -> str:
        return "en"

    def get_static_context(self) -> str:
        return "Static context"

    def get_replace_rules(self) -> list:
        return []

    def get_reading_speed_chars_per_second(self) -> float:
        return 14.6

    def get_min_duration_seconds(self) -> float:
        return 0.5

    def get_max_duration_seconds(self) -> float:
        return 5.0

    def get_allow_backwards_adjustment(self) -> bool:
        return False

    def get_logging_path(self) -> str:
        return "var/test.log"

    def get_offline_mode(self) -> bool:
        return True

    def get_failed_translation_marker(self) -> str:
        return "%TRANSLATION_FAILED%"


class TestSubtitleTiming(unittest.TestCase):

    def _make_segments(self, specs: list[tuple]) -> list[Segment]:
        """
        Helper to create segments.
        specs: list of (id, text, start_ms, end_ms)
        """
        segments = []
        for (sid, text, start, end) in specs:
            seg = Segment(sid, text, start, end)
            seg.set_target_text(text)
            segments.append(seg)
        return segments

    def test_basic_timing(self):
        """
        Start times match source. End times are based on reading speed.
        14 chars at 14.6 cps = 958.9ms ≈ 959ms
        """
        config = MockConfigParser1()
        logger = MockLogger1()
        # "Hello world!" = 12 chars → 12/14.6*1000 = 821.9ms
        # "Goodbye!" = 8 chars → 8/14.6*1000 = 547.9ms
        segments = self._make_segments([
            (1, "Hello world!", 0, 2000),
            (2, "Goodbye!", 5000, 8000),
        ])

        timing = SubtitleTiming(config, logger)
        timing.run(segments)

        self.assertEqual(segments[0].get_target_start_ms(), 0)
        self.assertEqual(segments[0].get_target_end_ms(), 822)

        self.assertEqual(segments[1].get_target_start_ms(), 5000)
        self.assertEqual(segments[1].get_target_end_ms(), 5548)

    def test_min_duration_clamping(self):
        """
        Very short text gets clamped to min_duration (500ms).
        2 chars at 14.6 cps = 137ms → clamped to 500ms
        """
        config = MockConfigParser1()
        logger = MockLogger1()
        segments = self._make_segments([
            (1, "Hi", 0, 1000),
            (2, "Ok", 5000, 6000),
        ])

        timing = SubtitleTiming(config, logger)
        timing.run(segments)

        self.assertEqual(segments[0].get_target_start_ms(), 0)
        self.assertEqual(segments[0].get_target_end_ms(), 500)

        self.assertEqual(segments[1].get_target_start_ms(), 5000)
        self.assertEqual(segments[1].get_target_end_ms(), 5500)

    def test_max_duration_clamping(self):
        """
        Very long text gets clamped to max_duration (5000ms).
        100 chars at 14.6 cps = 6849ms → clamped to 5000ms
        """
        config = MockConfigParser1()
        logger = MockLogger1()
        long_text = "A" * 100
        segments = self._make_segments([
            (1, long_text, 0, 7000),
            (2, "Hi", 10000, 11000),
        ])

        timing = SubtitleTiming(config, logger)
        timing.run(segments)

        self.assertEqual(segments[0].get_target_start_ms(), 0)
        self.assertEqual(segments[0].get_target_end_ms(), 5000)

        self.assertEqual(segments[1].get_target_start_ms(), 10000)
        self.assertEqual(segments[1].get_target_end_ms(), 10500)

    def test_next_segment_limit(self):
        """
        The end time is limited by the next segment's source start.
        100 chars would need 5000ms, but next starts at 3000ms.
        """
        config = MockConfigParser1()
        logger = MockLogger1()
        long_text = "A" * 100
        segments = self._make_segments([
            (1, long_text, 0, 7000),
            (2, "Hi", 3000, 4000),
        ])

        timing = SubtitleTiming(config, logger)
        timing.run(segments)

        # Clipped to next start (3000) instead of max_duration (5000)
        self.assertEqual(segments[0].get_target_start_ms(), 0)
        self.assertEqual(segments[0].get_target_end_ms(), 3000)

        self.assertEqual(segments[1].get_target_start_ms(), 3000)
        self.assertEqual(segments[1].get_target_end_ms(), 3500)

    def test_backwards_adjustment(self):
        """
        When a segment's end is clipped below its minimum duration by the next
        segment's start, time is stolen from the previous segment.

        Seg 1: 20 chars → 1369.86ms, start=0, next_start=2000 → end=1370
        Seg 2: 51 chars → 3493.15ms, start=2000, limited by seg3 start=2400 → end=2400
                min_end = 2500, deficit = 100
                prev available = 1370 - 500 = 870
                steal 100 → prev end=1270, seg2 end=2500
        Seg 3: 10 chars → 684.93ms, start=2400 → end=3085
        """
        config = MockConfigParser1()
        logger = MockLogger1()
        seg1_text = "A" * 20  # 20 chars → 1369.86ms
        seg2_text = "B" * 51  # 51 chars → 3493.15ms
        seg3_text = "C" * 10  # 10 chars → 684.93ms

        segments = self._make_segments([
            (1, seg1_text, 0, 2000),
            (2, seg2_text, 2000, 3000),
            (3, seg3_text, 2400, 4000),
        ])

        timing = SubtitleTiming(config, logger)
        timing.run(segments)

        # Seg 1: start=0, initial end=1370, after adjustment: 1370-100=1270
        self.assertEqual(segments[0].get_target_start_ms(), 0)
        self.assertEqual(segments[0].get_target_end_ms(), 1270)

        # Seg 2: start=2000, limited to 2400 by next, deficit=100, gets 100 from prev
        # end = 2400 + 100 = 2500
        self.assertEqual(segments[1].get_target_start_ms(), 2000)
        self.assertEqual(segments[1].get_target_end_ms(), 2500)

        # Seg 3: start=2400, reading=684.93ms, end=3085
        self.assertEqual(segments[2].get_target_start_ms(), 2400)
        self.assertEqual(segments[2].get_target_end_ms(), 3085)

    def test_backwards_adjustment_disabled(self):
        """
        Same scenario as test_backwards_adjustment but with backwards disabled.
        The clipped end stays as-is; no time is stolen from the previous.
        """
        config = MockConfigNoBackwards()
        logger = MockLogger1()
        seg1_text = "A" * 20  # 20 chars → 1369.86ms
        seg2_text = "B" * 51  # 51 chars → 3493.15ms
        seg3_text = "C" * 10  # 10 chars → 684.93ms

        segments = self._make_segments([
            (1, seg1_text, 0, 2000),
            (2, seg2_text, 2000, 3000),
            (3, seg3_text, 2400, 4000),
        ])

        timing = SubtitleTiming(config, logger)
        timing.run(segments)

        # Seg 1: no change (no stealing)
        self.assertEqual(segments[0].get_target_start_ms(), 0)
        self.assertEqual(segments[0].get_target_end_ms(), 1370)

        # Seg 2: clipped to 2400, no adjustment
        self.assertEqual(segments[1].get_target_start_ms(), 2000)
        self.assertEqual(segments[1].get_target_end_ms(), 2400)

        # Seg 3: normal
        self.assertEqual(segments[2].get_target_start_ms(), 2400)
        self.assertEqual(segments[2].get_target_end_ms(), 3085)

    def test_backwards_adjustment_limited_by_prev_min(self):
        """
        Backwards adjustment is limited by the previous segment's minimum duration.

        Seg 1: 10 chars → 684.93ms, start=0, next_start=800 → end=685
        Seg 2: 51 chars → 3493.15ms, start=800, limited by seg3 start=1200 → end=1200
               min_end = 1300, deficit = 100
               prev available = 685 - 500 = 185
               steal = min(100, 185) = 100
               prev end = 585, seg2 end = 1300
        Seg 3: 10 chars → 684.93ms, start=1200 → end=1885
        """
        config = MockConfigParser1()
        logger = MockLogger1()
        seg1_text = "A" * 10  # 10 chars → 684.93ms
        seg2_text = "B" * 51  # 51 chars → 3493.15ms
        seg3_text = "C" * 10  # 10 chars → 684.93ms

        segments = self._make_segments([
            (1, seg1_text, 0, 800),
            (2, seg2_text, 800, 2000),
            (3, seg3_text, 1200, 3000),
        ])

        timing = SubtitleTiming(config, logger)
        timing.run(segments)

        # Seg 1: start=0, initial end=685, after adjustment: 685-100=585
        self.assertEqual(segments[0].get_target_start_ms(), 0)
        self.assertEqual(segments[0].get_target_end_ms(), 585)

        # Seg 2: start=800, end was 1200, deficit=100, gets 100 from prev
        # end = 1200 + 100 = 1300
        self.assertEqual(segments[1].get_target_start_ms(), 800)
        self.assertEqual(segments[1].get_target_end_ms(), 1300)

        # Seg 3: start=1200, reading=684.93ms, end=1885
        self.assertEqual(segments[2].get_target_start_ms(), 1200)
        self.assertEqual(segments[2].get_target_end_ms(), 1885)

    def test_backwards_adjustment_prev_at_min(self):
        """
        If the previous segment is already at its minimum duration,
        no time can be stolen.

        Seg 1: 2 chars → 137.67ms → clamped to 500ms, start=0, next_start=1000 → end=500
        Seg 2: 51 chars → 3493.15ms, start=1000, limited by seg3 start=1400 → end=1400
               min_end = 1500, deficit = 100
               prev available = 500 - (0+500) = 0
               steal = 0 → no adjustment
        Seg 3: 10 chars → 684.93ms, start=1400 → end=2085
        """
        config = MockConfigParser1()
        logger = MockLogger1()
        seg1_text = "Hi"              # 2 chars → clamped to 500ms
        seg2_text = "B" * 51          # 51 chars → 3493.15ms
        seg3_text = "C" * 10          # 10 chars → 684.93ms

        segments = self._make_segments([
            (1, seg1_text, 0, 1000),
            (2, seg2_text, 1000, 2000),
            (3, seg3_text, 1400, 3000),
        ])

        timing = SubtitleTiming(config, logger)
        timing.run(segments)

        # Seg 1: at minimum, can't give anything
        self.assertEqual(segments[0].get_target_start_ms(), 0)
        self.assertEqual(segments[0].get_target_end_ms(), 500)

        # Seg 2: no adjustment possible
        self.assertEqual(segments[1].get_target_start_ms(), 1000)
        self.assertEqual(segments[1].get_target_end_ms(), 1400)

        # Seg 3: normal
        self.assertEqual(segments[2].get_target_start_ms(), 1400)
        self.assertEqual(segments[2].get_target_end_ms(), 2085)

    def test_skipped_segments_ignored(self):
        """
        Skipped segments are not processed for timing.
        Only non-skipped segments get adjusted times.
        """
        config = MockConfigParser1()
        logger = MockLogger1()
        segments = self._make_segments([
            (1, "Hello world!", 0, 2000),
            (2, "[SKIP ME]", 2000, 3000),
            (3, "Goodbye!", 5000, 8000),
        ])
        segments[1].set_skipped(True)

        timing = SubtitleTiming(config, logger)
        timing.run(segments)

        # Seg 1: next active is seg 3 at 5000
        # 12 chars → 822ms, end = min(822, 5000) = 822
        self.assertEqual(segments[0].get_target_start_ms(), 0)
        self.assertEqual(segments[0].get_target_end_ms(), 822)

        # Seg 2: skipped, times unchanged (source values)
        self.assertEqual(segments[1].get_target_start_ms(), 2000)
        self.assertEqual(segments[1].get_target_end_ms(), 3000)

        # Seg 3: last segment, 8 chars → 548ms
        self.assertEqual(segments[2].get_target_start_ms(), 5000)
        self.assertEqual(segments[2].get_target_end_ms(), 5548)

    def test_single_segment(self):
        """
        A single segment has no next-segment limit.
        """
        config = MockConfigParser1()
        logger = MockLogger1()
        segments = self._make_segments([
            (1, "Hello world!", 1000, 5000),
        ])

        timing = SubtitleTiming(config, logger)
        timing.run(segments)

        self.assertEqual(segments[0].get_target_start_ms(), 1000)
        # 12 chars → 822ms
        self.assertEqual(segments[0].get_target_end_ms(), 1822)

    def test_empty_segment_list(self):
        """
        Empty list should not raise.
        """
        config = MockConfigParser1()
        logger = MockLogger1()
        timing = SubtitleTiming(config, logger)
        timing.run([])  # Should not raise

    def test_all_skipped(self):
        """
        All segments skipped should not raise.
        """
        config = MockConfigParser1()
        logger = MockLogger1()
        segments = self._make_segments([
            (1, "Hello", 0, 1000),
            (2, "World", 2000, 3000),
        ])
        for seg in segments:
            seg.set_skipped(True)

        timing = SubtitleTiming(config, logger)
        timing.run(segments)  # Should not raise


if __name__ == "__main__":
    unittest.main()
