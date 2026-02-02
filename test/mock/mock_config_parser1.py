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

class MockConfigParser1(ConfigParserInterface):
    def get_model_name(self) -> str:
        return "google/madlad400-3b-mt"

    def get_model_type(self) -> str:
        return "madlad"
    
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
        return "English sentences to be translated:"

    def get_replace_rules(self) -> list:
        return [
            {"pattern": "\\s+", "replacement": " "},
            {"pattern": "\\[[^\\]]*\\]", "replacement": ""}
        ]

    def get_reading_speed_chars_per_second(self) -> float:
        return 14.6

    def get_min_duration_seconds(self) -> float:
        return 0.5

    def get_max_duration_seconds(self) -> float:
        return 5

    def get_allow_backwards_adjustment(self) -> bool:
        return True

    def get_logging_path(self) -> str:
        return "var/run-{TIME}.log"

    def get_offline_mode(self) -> bool:
        return True
