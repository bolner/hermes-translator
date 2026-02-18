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
import re
from datetime import timedelta
from primitives.segment import Segment
from primitives.config_parser_interface import ConfigParserInterface

class SrtWriter:
    def __init__(self, path: str, segments: list[Segment],
                config: ConfigParserInterface):
        newline_token = config.get_sentinel_token_template().replace("{ID}", "12")
        subtitles: list[srt.Subtitle] = []

        for segment in segments:
            if segment.is_skipped():
                continue
            
            text = re.sub(f"\\s*{newline_token}\\s*", "\n", segment.get_target_text())
            subtitles.append(
                srt.Subtitle(
                    index=segment.get_target_id(),
                    start=timedelta(milliseconds=segment.get_target_start_ms()),
                    end=timedelta(milliseconds=segment.get_target_end_ms()),
                    content=text
                )
            )

        with open(path, "w", encoding="utf-8") as f:
            f.write(srt.compose(
                subtitles=subtitles,
                reindex=True,
                start_index=1
            ))
