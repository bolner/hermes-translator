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
from primitives.segment import Segment
from primitives.window_interface import WindowInterface

class Window(WindowInterface):
    def __init__(self, config: ConfigParserInterface,
                 segments: list[Segment]):
        if len(segments) < 1:
            raise ValueError("Empty segment list passed in the Window constructor.")
        
        self.__segments: list[Segment] = segments
        self.__maxCharsBefore: int = config.get_max_chars_before()
        self.__maxCharsAfter: int = config.get_max_chars_after()
        self.__maxSegmentsBefore: int = config.get_max_segments_before()
        self.__maxSegmentsAfter: int = config.get_max_segments_after()
        self.__start: int = 0          # The first segment index that is in the window
        self.__cursor: int = -1        # Translation target index
        self.__end: int = 0            # The last segment index that is in the window

    def next(self) -> bool:
        if self.__cursor >= len(self.__segments) - 1:
            # Already the last segment
            return False
        
        self.__cursor += 1
        
        # Align the start
        if self.__cursor > 0:
            sum_before_count = 0
            sum_before_chars = 0
            for i in range(self.__start, self.__cursor):
                sum_before_count += 1
                sum_before_chars += len(self.__segments[i].get_source_text())
            
            while self.__start < self.__cursor:
                if sum_before_count > self.__maxSegmentsBefore:
                    sum_before_count -= 1
                    self.__start += 1
                    
                    continue
                
                if sum_before_chars > self.__maxCharsBefore:
                    sum_before_chars -= len(self.__segments[0].get_source_text())
                    self.__start += 1
                    continue

                break
        
        # Align the end
        if self.__end < len(self.__segments) - 1:
            sum_after_count = 0
            sum_after_chars = 0

            for i in range(self.__cursor + 1, len(self.__segments)):
                sum_after_count += 1
                if sum_after_count > self.__maxSegmentsAfter:
                    break

                sum_after_chars += len(self.__segments[i].get_source_text())
                if sum_after_chars > self.__maxCharsAfter:
                    break

                self.__end = i

        return True

    def get_current_segment(self) -> Segment:
        """
        Returns the segment that is currently selected for translation.
        """
        return self.__segments[self.__cursor]

    def get_segments_before_current(self) -> list[Segment]:
        response: list[Segment] = []

        for i in range(self.__start, self.__cursor):
            response.append(self.__segments[i])
        
        return response

    def get_segments_after_current(self) -> list[Segment]:
        response: list[Segment] = []

        for i in range(self.__cursor + 1, self.__end + 1):
            response.append(self.__segments[i])
        
        return response
