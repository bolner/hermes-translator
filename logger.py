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
import datetime
import os
from primitives.logger_interface import LoggerInterface
from primitives.config_parser_interface import ConfigParserInterface

class Logger(LoggerInterface):
    """
    Handles the Madlad model.
    """
    def __init__(self, config: ConfigParserInterface):
        self.__config: ConfigParserInterface = config
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self._path = self.__config.get_logging_path().replace("{TIME}", ts)
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        self._log_file_handler = open(self._path, "a", encoding="utf-8")

    def log(self, text: str):
        """
        Writes the entry into the log file.
        """
        if self._log_file_handler is None:
            raise RuntimeError("Log file was closed already before a write attempt: "
                f"'{text}'")

        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log_file_handler.write(ts + "\n\n" + text + "\n")
        self._log_file_handler.write("-------------------------\n")
        self._log_file_handler.flush()
    
    def log_print(self, text: str):
        """
        Not only writes into the log file,
        but also prints to STDOUT.
        """
        self.log(text)
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"- {ts}: {text}")

    def close(self):
        """
        Close the log file.
        """
        self._log_file_handler.close()
        self._log_file_handler = None
