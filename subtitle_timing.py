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

from primitives.config_parser_interface import ConfigParserInterface
from primitives.logger_interface import LoggerInterface
from primitives.segment import Segment


class SubtitleTiming:
    """
    Adjusts the target start/end times of segments based on reading speed.

    Rules:
    - Start times are the same as in the source subtitles.
    - End times are adjusted based on reading speed (chars per second).
    - The start of the next subtitle limits the length of the current subtitle.
    - If there isn't enough space, the extra duration can be adjusted backwards
      (stolen from the previous subtitle) if "allow-backwards-adjustment" is enabled.
    """

    def __init__(self, config: ConfigParserInterface, logger: LoggerInterface):
        self.__config = config
        self.__logger = logger
        self.__reading_speed: float = config.get_reading_speed_chars_per_second()
        self.__min_duration_ms: float = config.get_min_duration_seconds() * 1000.0
        self.__max_duration_ms: float = config.get_max_duration_seconds() * 1000.0
        self.__allow_backwards: bool = config.get_allow_backwards_adjustment()

    def run(self, segments: list[Segment]) -> None:
        """
        Adjusts target times for all non-skipped segments in the list.
        """
        active: list[Segment] = [s for s in segments if not s.is_skipped()]

        if len(active) == 0:
            return

        self.__compute_initial_times(active)

        if self.__allow_backwards:
            self.__apply_backwards_adjustment(active)

    def __compute_initial_times(self, active: list[Segment]) -> None:
        """
        Sets target start/end for each active segment:
        - start = source start
        - end = start + reading_time (clamped to [min, max])
        - end is limited by the next segment's source start
        """
        for i, seg in enumerate(active):
            start_ms: float = float(seg.get_source_start_ms())
            seg.set_target_start_ms(int(start_ms))

            text: str = seg.get_target_text() or ""
            char_count: int = len(text)

            # Compute the duration needed to read the text at the configured speed.
            reading_ms: float = (char_count / self.__reading_speed) * 1000.0

            # Clamp to [min_duration, max_duration].
            reading_ms = max(self.__min_duration_ms, min(self.__max_duration_ms, reading_ms))

            end_ms: float = start_ms + reading_ms

            # The start of the next subtitle limits the length of the current one.
            if i + 1 < len(active):
                next_start_ms: float = float(active[i + 1].get_source_start_ms())
                end_ms = min(end_ms, next_start_ms)

            seg.set_target_end_ms(int(round(end_ms)))

    def __apply_backwards_adjustment(self, active: list[Segment]) -> None:
        """
        If a segment's end time was clipped below its minimum duration by the
        next segment's start, steal time from the previous segment to compensate.
        """
        for i in range(1, len(active)):
            seg: Segment = active[i]
            start_ms: float = float(seg.get_target_start_ms())
            end_ms: float = float(seg.get_target_end_ms())

            min_end: float = start_ms + self.__min_duration_ms

            if end_ms < min_end:
                deficit: float = min_end - end_ms

                prev: Segment = active[i - 1]
                prev_start: float = float(prev.get_target_start_ms())
                prev_end: float = float(prev.get_target_end_ms())
                prev_floor: float = prev_start + self.__min_duration_ms
                available: float = prev_end - prev_floor

                if available > 0:
                    steal: float = min(deficit, available)
                    prev.set_target_end_ms(int(round(prev_end - steal)))
                    new_end: float = end_ms + steal
                    # Don't exceed the max duration.
                    new_end = min(new_end, start_ms + self.__max_duration_ms)
                    seg.set_target_end_ms(int(round(new_end)))
