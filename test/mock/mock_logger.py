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

from primitives.logger_interface import LoggerInterface

class MockLogger1(LoggerInterface):
    def __init__(self):
        self.__entries: list[str] = []
    
    def log(self, text: str):
        self.__entries.append(text)
    
    def get_entries(self) -> list[str]:
        return self.__entries
