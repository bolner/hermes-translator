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
from argparse import ArgumentParser

class CliParser:
    def __init__(self):
        parser = ArgumentParser()

        parser.add_argument("-c", "--config", dest="config",
                    help="Path to the config file.")
        parser.add_argument("-i", "--input", dest="input",
                    help="Path to the input file.")
        parser.add_argument("-o", "--output", dest="output",
                    help="Path to the output file.")
        parser.add_argument("--dry-run", action="store_true", default=False,
                            dest="dryrun")

        self.__args = parser.parse_args()

    def get_config_path(self) -> str:
        return self.__args.config

    def get_input_path(self) -> str:
        return self.__args.input

    def get_output_path(self) -> str:
        return self.__args.output

    def is_dry_run(self) -> bool:
        return self.__args.dryrun
