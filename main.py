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
from primitives.segment import Segment
from window import Window
from logger import Logger
from segment_processing import SegmentProcessing

config = ConfigParser("config-madlad.yaml")
if config.get_offline_mode():
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_OFFLINE"] = "1"

processing = SegmentProcessing(config)
logger = Logger(config)
model = MadladModel(config, logger, device = "cuda:0")

print("- Model loaded on device:", model.get_device())

# SRT lib doc
# https://srt.readthedocs.io/en/latest/api.html

segments = [
    Segment(1, "Ez az első mondat.\nVagy nem.", 0, 0),
    Segment(2, "Ez a mondat lesz a végső.\nDe lehet, hogy mégsem, mert sok "
        "mondatból könnyebb interpolálni egy releváns jelentést.", 0, 0),
    Segment(3, "Utolsó mondathoz képest, ez nem is rossz!", 0, 0)
]

window = Window(config, segments)
translator = Translator(model, config, window, logger)
processing.process(segments)
translator.run()

for segment in segments:
    print(segment.get_target_text())
