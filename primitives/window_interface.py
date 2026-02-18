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

from abc import ABC, abstractmethod
from primitives.segment import Segment

class WindowInterface(ABC):
    @abstractmethod
    def next(self) -> bool:
        pass

    @abstractmethod
    def get_current_segment(self) -> Segment:
        """
        Returns the segment that is currently selected for translation.
        """
        pass

    @abstractmethod
    def get_segments_before_current(self) -> list[Segment]:
        pass

    @abstractmethod
    def get_segments_after_current(self) -> list[Segment]:
        pass

    @abstractmethod
    def get_progress_pct(self) -> int:
        pass
