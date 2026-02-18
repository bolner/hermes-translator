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

import srt
from primitives.segment import Segment
from primitives.config_parser_interface import ConfigParserInterface

class SrtReader:
    def __init__(self, path: str, config: ConfigParserInterface):
        newline_token = config.get_sentinel_token_template().replace("{ID}", "12")

        self.__segments: list[Segment] = []
        with open(path, "r", encoding="utf-8") as f:
            contents = f.read()
            subtitles = srt.parse(contents)
            id_counter = 1
            for sub in subtitles:
                id = sub.index
                if id is None:
                    id = id_counter

                content = sub.content.strip().replace("\n", f" {newline_token} ")

                self.__segments.append(
                    Segment(id, content, int(sub.start.total_seconds() * 1000),
                            int(sub.end.total_seconds() * 1000))
                )
                id_counter += 1

    def get_segments(self) -> list[Segment]:
        return self.__segments
