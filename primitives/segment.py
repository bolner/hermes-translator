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

from primitives.model_interface import ModelInterface

class Segment:
    """
    Represents a text segment with its tokenized form.
    """
    def __init__(self, id: int, text: str, start_ms: int, end_ms: int):
        """
        Constructor.
        Args:
            id (int): The unique identifier of the segment.
            text (str): The source text of the segment.
            start_ms (int): The start time of the segment in milliseconds.
            end_ms (int): The end time of the segment in milliseconds.
        """
        self.__source_id: int = id
        self.__source_text: str = text.strip()
        self.__source_start_ms: int = start_ms
        self.__source_end_ms: int = end_ms

        self.__target_id: int = 0
        self.__target_text: str = None
        self.__target_start_ms: int = start_ms
        self.__target_end_ms: int = end_ms

        self.__skipped: bool = False
        self.__prompt: str = None

    def get_source_id(self) -> int:
        """
        The SRT ID in the source document.
        """
        return self.__source_id

    def get_source_text(self) -> str:
        return self.__source_text
    
    def set_source_text(self, source_text: str) -> None:
        self.__source_text = source_text

    def get_source_start_ms(self) -> int:
        return self.__source_start_ms

    def get_source_end_ms(self) -> int:
        return self.__source_end_ms

    def get_token_list_id(self) -> int:
        return self.__token_list_id

    def get_model(self) -> ModelInterface:
        return self.__model

    def get_target_id(self) -> int:
        """
        The SRT ID in the target document.
        """
        return self.__target_id

    def set_target_id(self, target_id: int) -> None:
        self.__target_id = target_id

    def get_target_text(self) -> str:
        return self.__target_text

    def set_target_text(self, target_text: str) -> None:
        self.__target_text = target_text

    def get_target_start_ms(self) -> int:
        return self.__target_start_ms

    def set_target_start_ms(self, target_start_ms: int) -> None:
        self.__target_start_ms = target_start_ms

    def get_target_end_ms(self) -> int:
        return self.__target_end_ms

    def set_target_end_ms(self, target_end_ms: int) -> None:
        self.__target_end_ms = target_end_ms

    def is_skipped(self) -> bool:
        return self.__skipped

    def set_skipped(self, skipped: bool) -> None:
        self.__skipped = skipped

    def set_prompt(self, prompt: str) -> None:
        self.__prompt = prompt

    def get_prompt(self) -> str:
        return self.__prompt
