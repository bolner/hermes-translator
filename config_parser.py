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

import yaml
from primitives.config_parser_interface import ConfigParserInterface

class ConfigParser(ConfigParserInterface):
    def __init__(self, yaml_file_path: str):
        self.__config_path = yaml_file_path

        with open(yaml_file_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def __to_bool(self, field: str, val) -> bool:
        if isinstance(val, bool):
            return val
        
        if isinstance(val, int):
            return val != 0

        normalized = str(val).lower().strip()
        truthy = ("true", "yes", "on", "1", "enable")
        falsy = ("false", "no", "off", "0", "disable")

        if normalized in truthy:
            return True
        if normalized in falsy:
            return False
    
        raise ValueError(f"Invalid boolean value '{val}' for field '{field}' "
                         f"in config file '{self.__config_path}'.")

    def get_model_name(self) -> str:
        return str(self.config['model']['name'])

    def get_model_type(self) -> str:
        return str(self.config['model']['type'])
    
    def get_prompt_prefix(self) -> str:
        return str(self.config['model']['prompt-prefix'])

    def get_sentinel_token_template(self) -> str:
        return str(self.config['model']['sentinel-token-template'])

    def get_inference_batch_size(self) -> int:
        return int(self.config['model']['inference-batch-size'])

    def get_max_chars_before(self) -> int:
        return int(self.config['context-window']['max-chars-before'])

    def get_max_segments_before(self) -> int:
        return int(self.config['context-window']['max-segments-before'])

    def get_max_chars_after(self) -> int:
        return int(self.config['context-window']['max-chars-after'])

    def get_max_segments_after(self) -> int:
        return int(self.config['context-window']['max-segments-after'])

    def get_target_language(self) -> str:
        return str(self.config['target-language'])

    def get_static_context(self) -> str:
        return str(self.config['document']['static-context'])

    def get_replace_rules(self) -> list:
        return list(self.config['document'].get('replace-rules', []))

    def get_reading_speed_chars_per_second(self) -> float:
        return float(self.config['subtitle-timing']['reading-speed-chars-per-second'])

    def get_min_duration_seconds(self) -> float:
        return float(self.config['subtitle-timing']['min-duration-seconds'])

    def get_max_duration_seconds(self) -> float:
        return float(self.config['subtitle-timing']['max-duration-seconds'])

    def get_allow_backwards_adjustment(self) -> bool:
        return self.__to_bool("subtitle-timing.allow-backwards-adjustment",
            self.config['subtitle-timing']['allow-backwards-adjustment'])

    def get_logging_path(self) -> str:
        return str(self.config['logging-path'])

    def get_offline_mode(self) -> bool:
        return self.__to_bool("model.offline-mode",
            self.config['model']['offline-mode'])
