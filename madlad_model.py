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
from torch import compile, inference_mode
from primitives.model_interface import ModelInterface
from primitives.config_parser_interface import ConfigParserInterface
from primitives.logger_interface import LoggerInterface
from transformers import T5ForConditionalGeneration
from transformers.models.t5.modeling_t5 import T5ForConditionalGeneration
from transformers.models.t5.tokenization_t5_fast import T5TokenizerFast

class MadladModel(ModelInterface):
    """
    Handles the Madlad model.
    """
    def __init__(self, config: ConfigParserInterface,
            logger: LoggerInterface, device: str = "cuda:0"):
        self.__model_name: str = config.get_model_name()
        self.__device: str = device
        self.__logger = logger
        self.__model = compile(
            T5ForConditionalGeneration.from_pretrained(config.get_model_name()).to(device)
        )
        logger.log(f"Model type: {str(type(self.__model))}")
        self.__tokenizer = (
            T5TokenizerFast.from_pretrained(config.get_model_name())
        )
        logger.log(f"Tokenizer type: {str(type(self.__tokenizer))}")
    
    def generate(self, prompts: list[str]) -> list[str]:
        """
        Runs inference on multiple prompts in parallel.
        Args:
            prompts (list[str]): The translation prompts.
        Returns:
            list[str]: The generated texts. (Translations)
        """
        self.__logger.log(f"Translating: {prompts}")

        inputs = self.__tokenizer(prompts, return_tensors="pt", padding=True).to(self.__device)
        with inference_mode():
            outputs = self.__model.generate(**inputs, max_new_tokens=512)

        translations = self.__tokenizer.batch_decode(outputs, skip_special_tokens=True)

        self.__logger.log(f"Translations: {translations}")

        if len(translations) != len(prompts):
            raise RuntimeError("tokenizer.batch_decode returned the wrong number of translations.")

        return translations
    
    def get_model_name(self) -> str:
        """
        Returns the name of the model.
        Returns:
            str: The model name.
        """
        return self.__model_name
    
    def get_device(self) -> str:
        """
        Returns the device on which the model is loaded.
        Returns:
            str: The device string (e.g., "cuda:0" or "cpu").
        """
        return self.__device
