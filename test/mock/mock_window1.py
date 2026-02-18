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

from primitives.segment import Segment
from primitives.window_interface import WindowInterface

class MockWindow1(WindowInterface):
    def __init__(self, segments: list[Segment]):
        self.__segments = segments
        self.__cursor = -1

    def next(self) -> bool:
        if self.__cursor >= len(self.__segments) - 1:
            return False
    
        self.__cursor += 1
        return True

    def get_current_segment(self) -> Segment:
        """
        Returns the segment that is currently selected for translation.
        """
        return self.__segments[self.__cursor]

    def get_segments_before_current(self) -> list[Segment]:
        response: list[Segment] = []

        for i in range(0, self.__cursor):
            response.append(self.__segments[i])
        
        return response

    def get_segments_after_current(self) -> list[Segment]:
        response: list[Segment] = []

        for i in range(self.__cursor + 1, len(self.__segments)):
            response.append(self.__segments[i])
        
        return response

    def get_progress_pct(self) -> int:
        return int(((self.__cursor + 1) / len(self.__segments)) * 100)
