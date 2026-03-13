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

from primitives.srt_reader_interface import SrtReaderInterface
from primitives.segment import Segment

class MockSrtReader(SrtReaderInterface):
    def __init__(self, segments: list[Segment], path: str):
        self.__segments = segments
        self.__path = path

    def get_segments(self) -> list[Segment]:
        return self.__segments

    def get_path(self) -> str:
        return self.__path
