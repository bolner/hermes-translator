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
import torch
from torch import compile, inference_mode
from primitives.model_interface import ModelInterface
from primitives.config_parser_interface import ConfigParserInterface
from primitives.logger_interface import LoggerInterface
from transformers import T5ForConditionalGeneration, BitsAndBytesConfig
from transformers.models.t5.tokenization_t5_fast import T5TokenizerFast

class MadladModel(ModelInterface):
    """
    Handles the Madlad model.
    """
    def __init__(self, config: ConfigParserInterface,
            logger: LoggerInterface, device: str = "cuda:0"):
        self.__model_name: str = config.get_model_name()
        self.__device: str = device
        self.__dtype: str = config.get_model_dtype()
        self.__model = self.__load_model(logger)
        logger.log(f"Model type: {str(type(self.__model))}")
        self.__tokenizer = (
            T5TokenizerFast.from_pretrained(config.get_model_name())
        )
        logger.log(f"Tokenizer type: {str(type(self.__tokenizer))}")

    def __load_model(self, logger: LoggerInterface):
        """
        Loads the model with the configured dtype.
        - fp32: full precision, ~12 GB VRAM (default, original behaviour).
        - fp16: half precision, ~6 GB VRAM, 2-4x faster on Turing+ GPUs.
        - int8: 8-bit quantization via bitsandbytes, ~4 GB VRAM,
          recommended for 8 GB VRAM cards.
        """
        if not self.__device.startswith("cuda"):
            if self.__dtype != "fp32":
                raise ValueError(
                    f"Model dtype '{self.__dtype}' requires a CUDA device. "
                    "Use dtype 'fp32' when running on CPU.")

        if self.__dtype == "int8":
            # 8-bit quantization via the bitsandbytes library.
            # bnb requires device_map (the model ends up on the device
            # directly), and torch.compile is skipped, because the bnb
            # kernels break the compiled graph.
            logger.log(f"Loading model with 8-bit quantization (bitsandbytes) "
                       f"on device {self.__device}")
            return T5ForConditionalGeneration.from_pretrained(
                self.__model_name,
                quantization_config=BitsAndBytesConfig(load_in_8bit=True),
                device_map=self.__device
            )

        torch_dtype = torch.float16 if self.__dtype == "fp16" else torch.float32
        logger.log(f"Loading model with dtype '{self.__dtype}' "
                   f"on device {self.__device}")
        return compile(
            T5ForConditionalGeneration.from_pretrained(
                self.__model_name, dtype=torch_dtype
            ).to(self.__device)
        )
    
    def generate(self, prompts: list[str]) -> list[str]:
        """
        Runs inference on multiple prompts in parallel.
        Args:
            prompts (list[str]): The translation prompts.
        Returns:
            list[str]: The generated texts. (Translations)
        """
        inputs = self.__tokenizer(prompts, return_tensors="pt", padding=True).to(self.__device)
        with inference_mode():
            outputs = self.__model.generate(**inputs, max_new_tokens=512, repetition_penalty=1.1, num_beams=2)

        translations = self.__tokenizer.batch_decode(outputs, skip_special_tokens=True)

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
