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

class LoggerInterface(ABC):
    @abstractmethod
    def log(self, text: str):
        """
        Writes the entry into the log file.
        """
        pass

    @abstractmethod
    def log_print(self, text: str):
        """
        Not only writes into the log file,
        but also prints to STDOUT.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Close the log file.
        """
        pass
