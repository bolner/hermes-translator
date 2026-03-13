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
import os
from madlad_model import MadladModel
from translator import Translator
from config_parser import ConfigParser
from window import Window
from logger import Logger
from segment_processing import SegmentProcessing
from srt_writer import SrtWriter
from test.mock.mock_model1 import MockModel1
from cli_parser import CliParser
from primitives.segment import Segment
from srt_reader import SrtReader

cli = CliParser()

config = ConfigParser(cli.get_config_path())
if config.get_offline_mode():
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_OFFLINE"] = "1"

logger = Logger(config)
logger.log_print(f"Config file: {cli.get_config_path()}")

input_reader = SrtReader(cli.get_input_path(), config)
if cli.get_retry_path() is not None:
    retry_reader = SrtReader(cli.get_retry_path(), config)
else:
    retry_reader = None

processing = SegmentProcessing(config, input_reader,
                               retry_reader, logger)
segments: list[Segment] = processing.process()
logger.log_print(f"Segment count: {len(segments)}")
window = Window(config, segments)

if cli.is_dry_run():
    for segment in segments:
        segment.set_target_text(segment.get_source_text())
else:
    logger.log_print(f"Loading model: {config.get_model_name()}")
    model = MadladModel(config, logger, device = "cuda:0") # MockModel1()
    logger.log_print(f"Model loaded on device: {model.get_device()}")

    translator = Translator(model, config, window, logger)
    logger.log_print(f"Starting translation...")
    translator.run()

logger.log_print(f"Failed segments: {translator.get_failure_count()}")
logger.log_print(f"Writing results to: {cli.get_output_path()}")
logger.log_print(f"Segment count: {len(segments)}")
SrtWriter(cli.get_output_path(), segments, config)

logger.close()
