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

class ConfigParserInterface(ABC):
    @abstractmethod
    def get_model_name(self) -> str:
        pass

    @abstractmethod
    def get_model_type(self) -> str:
        pass

    @abstractmethod
    def get_prompt_prefix(self) -> str:
        pass

    @abstractmethod
    def get_sentinel_token_template(self) -> str:
        pass

    @abstractmethod
    def get_inference_batch_size(self) -> int:
        pass

    @abstractmethod
    def get_max_chars_before(self) -> int:
        pass

    @abstractmethod
    def get_max_segments_before(self) -> int:
        pass

    @abstractmethod
    def get_max_chars_after(self) -> int:
        pass

    @abstractmethod
    def get_max_segments_after(self) -> int:
        pass

    @abstractmethod
    def get_target_language(self) -> str:
        pass

    @abstractmethod
    def get_static_context(self) -> str:
        pass

    @abstractmethod
    def get_replace_rules(self) -> list:
        pass

    @abstractmethod
    def get_reading_speed_chars_per_second(self) -> float:
        pass

    @abstractmethod
    def get_min_duration_seconds(self) -> float:
        pass

    @abstractmethod
    def get_max_duration_seconds(self) -> float:
        pass

    @abstractmethod
    def get_allow_backwards_adjustment(self) -> bool:
        pass

    @abstractmethod
    def get_logging_path(self) -> str:
        pass

    @abstractmethod
    def get_offline_mode(self) -> bool:
        pass
