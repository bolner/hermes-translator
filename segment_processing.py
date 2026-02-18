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
import re
from primitives.config_parser_interface import ConfigParserInterface
from primitives.segment import Segment

class SegmentProcessing:
    def __init__(self, config: ConfigParserInterface):
        self.__config = config
    
    def process(self, segments: list[Segment]):
        rules = self.__config.get_replace_rules()

        for segment in segments:
            for rule in rules:
                newstr = re.sub(rule['pattern'], rule['replacement'],
                    segment.get_source_text()).strip()

                if newstr == "":
                    segment.set_skipped(True)
                    continue
                
                segment.set_source_text(self.uppercase_after_dot(newstr))

    def uppercase_after_dot(self, text):
        # The madlad model can go crazy because of lower-case letters
        #   that come after a dot.
        return re.sub(r'(\.\s*)([a-z])', lambda m: m.group(1) + m.group(2).upper(),
                      text, flags=re.IGNORECASE)
