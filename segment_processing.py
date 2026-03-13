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
from primitives.srt_reader_interface import SrtReaderInterface
from primitives.logger_interface import LoggerInterface

class SegmentProcessing:
    def __init__(self, config: ConfigParserInterface, input_reader: SrtReaderInterface,
                retry_reader: SrtReaderInterface, logger: LoggerInterface):
        self.__config = config
        self.__failed_translation_marker: str = config.get_failed_translation_marker()

        logger.log_print(f"Using input file: {input_reader.get_path()}")
        self.__segments: list[Segment] = input_reader.get_segments()
        self.__retry_reader = retry_reader
        self.__logger = logger

    def process(self) -> list[Segment]:
        indexed: dict[str, Segment] = {}
        rules = self.__config.get_replace_rules()
        
        for segment in self.__segments:
            indexed[segment.get_source_start_ms()] = segment

            if segment.get_source_text() == self.__failed_translation_marker:
                continue

            original: str = segment.get_source_text()

            for rule in rules:
                newstr = re.sub(rule['pattern'], rule['replacement'],
                    segment.get_source_text()).strip()

                if newstr == "":
                    if not segment.is_skipped():
                        self.__logger.log(f"Segment skipped:\n{original}")
                    
                    segment.set_skipped(True)
                    continue
                
                segment.set_source_text(self.text_process(newstr))

        if self.__retry_reader is not None:
            self.__logger.log_print(f"Using retry file: {self.__retry_reader.get_path()}")
            pass1_segments = self.__retry_reader.get_segments()
            
            for pass1 in pass1_segments:
                if pass1.get_source_text() == self.__failed_translation_marker:
                    continue

                segment = indexed.get(pass1.get_source_start_ms())

                if segment is not None:
                    if segment.is_skipped():
                        continue

                    segment.set_target_text(pass1.get_source_text())
                    segment.set_target_start_ms(pass1.get_source_start_ms())
                    segment.set_target_end_ms(pass1.get_source_end_ms())
        
        return self.__segments

    def text_process(self, text):
        # The madlad model can go crazy because of lower-case letters
        #   that come after a dot.
        text = re.sub(r'(\.\s*)([a-z])', lambda m: m.group(1) + m.group(2).upper(),
            text, flags=re.IGNORECASE)
        
        # Also when a sentence starts with lower case.
        if text[-1] in (".", ":", "!", "?"):
            text = text[0].upper() + text[1:]
        
        return text
