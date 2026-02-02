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
from primitives.segment import Segment
from primitives.window_interface import WindowInterface
from primitives.logger_interface import LoggerInterface
from primitives.model_interface import ModelInterface

class Translator:
    """
    Prepares the prompt for this specific model.
    """
    def __init__(self, model: ModelInterface, config: ConfigParserInterface,
                window: WindowInterface, logger: LoggerInterface):
        self.__model: ModelInterface = model
        self.__window: WindowInterface = window
        self.__logger = logger
        self.__inference_batch_size = config.get_inference_batch_size()

        self.__prefix = config.get_prompt_prefix().replace(
            "{LANG}", config.get_target_language()
        )
        self.__context = config.get_static_context()
        self.__sentinelToken1 = config.get_sentinel_token_template().replace(
            "{ID}", "0"
        )
        self.__sentinelToken2 = config.get_sentinel_token_template().replace(
            "{ID}", "1"
        )

    def run(self):
        ############################################################
        # Iterate through the input while maintaining the window.
        ############################################################
        prompt_batch: list[Segment] = []

        self.__logger.log(f"- before the loop")
        while self.__window.next():
            self.__logger.log(f"- Next in loop: {self.__window.get_current_segment().get_source_text()}")

            current: Segment = self.__window.get_current_segment()
            current.set_prompt(self.__construct_prompt())
            prompt_batch.append(current)

            if len(prompt_batch) >= self.__inference_batch_size:
                self.__inference(prompt_batch)
                prompt_batch.clear()

        if len(prompt_batch) > 0:
            self.__inference(prompt_batch)
            prompt_batch.clear()

    def __construct_prompt(self) -> str:
        """
        Returns the prompt for the current Segment in the Window.
        """
        response: list[str] = []

        response.append(self.__prefix)
        response.append(self.__context)

        for segment in self.__window.get_segments_before_current():
            response.append(segment.get_source_text())

        response.append(self.__sentinelToken1)
        response.append(self.__window.get_current_segment().get_source_text())
        response.append(self.__sentinelToken2)

        for segment in self.__window.get_segments_after_current():
            response.append(segment.get_source_text())
        
        prompt = " ".join(response)

        return prompt

    def __inference(self, segments: list[Segment]):
        prompts: list[str] = []
        for segment in segments:
            prompts.append(segment.get_prompt())

        reponses = self.__model.generate(prompts)

        for i in range(0, len(segments)):
            response = reponses[i]
            pos1 = response.find(self.__sentinelToken1)
            if pos1 < 0:
                raise RuntimeError("Cannot find sentinel_token1 in a translation response: "
                    f"'{response}'.\nPrompt:\n'{segments[i].get_prompt()}'.")
            pos2 = response.find(self.__sentinelToken2)
            if pos2 < 0:
                raise RuntimeError("Cannot find sentinel_token2 in a translation response: "
                    f"'{response}'.\nPrompt:\n'{segments[i].get_prompt()}'.")
            
            if pos2 < pos1:
                raise RuntimeError("The sentinel tokens are in reverse order in a translation "
                    f"response: '{response}'.\nPrompt:\n'{segments[i].get_prompt()}'.")
            
            segments[i].set_target_text(response[pos1 + len(self.__sentinelToken1) : pos2])
            segments[i].set_target_start_ms(segments[i].get_source_start_ms())
            segments[i].set_target_end_ms(segments[i].get_source_end_ms())
            segments[i].set_prompt(None)
