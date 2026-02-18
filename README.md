Hermes Translator for subtitles
===============================

Contextual translation on local GPUs. Supports the `.srt` subtitle
format and the following model:
- [https://huggingface.co/google/madlad400-3b-mt](https://huggingface.co/google/madlad400-3b-mt)

The `madlad400-3b-mt` model allocates around 11G VRAM by default. I've tested the application with it on an `RTX 3090 Ti`.

It allows high-quality translations that compete with professional applications.
And that was the main motivation behind this tool: There were mostly three kinds of free subtitle-translator applications: 
One provides accurate translations, but can't deal with the `.srt` structure. Others preserve
the structure properly, but do a bad job at the translation. (Mostly becase they translate the utterances without context.)
While the third kind is not really free, as it depends on access to paid APIs.

This solution works on your own GPU, using the multi-lingual `madlad400-3b-mt` model,
which was trained on around 400 languages. This application lets you specify the window size for including
texts in the translation, before and after the target segment. Making it possible to provide a
solid context even for the shortest utterance.

# Table of contents <!-- omit in toc -->

<!-- TOC tocDepth:1..3 chapterDepth:1..6 -->

- [Setup on Debian 13](#setup-on-debian-13)
- [Usage](#usage)
    - [Running the tests](#running-the-tests)

<!-- /TOC -->

# Setup on Debian 13

- Install the NVIDIA and CUDA drivers. My current (2026 January) versions are:
    - Driver version: 590.44.01
    - CUDA version: 13.1
    
    (If you install different driver versions, then some of the libraries
    might also need different versions. See: `requirements.txt`)
- Restart the machine and verify the drivers with the command: `nvidia-smi`
- Install these base packages as root if missing:
    ```bash
    apt update
    apt install make
    apt install python3-full  # For venv and other
    ```
- Execute the following (from the project directory, as a non-elevated user) to set up the `venv` for the project:
    
    (This will install dependencies as well.)
    ```bash
    make setup
    ```

- If you wish to configure the virtual environment (`venv`) then enter it with the following command:
    ```bash
    source .venv/bin/activate
    ```
    (Then exit it using the `deactivate` command.)

# Usage

Type `make help` to see available commands.

```
$ make help

Makefile commands:
  make setup  - Set up the Python virtual environment and install dependencies.
  make run    - Run the main Python application. Use cases:
      make run config=[config-file] input=[input-file] output=[output-file]
           Contextual translation of the input-file.
           The config-file is a '.yaml' file that defines the translation settings.
           The result is written to the output file.

      make run dry-run=1 config=[config-file] input=[input-file] output=[output-file]
           Executes only the regex replacements defined in the config-file,
           without loading the model.

  make clean  - Remove the Python virtual environment.
  make test   - Execute the unit tests.
```

## Translating an srt file

Example with a small srt file:
```
$ make run config=config-madlad.yaml input=my-sub-2.srt output=my-sub-2-en.srt

. .venv/bin/activate && python3 main.py --config config-madlad.yaml --input my-sub-2.srt --output my-sub-2-en.srt
- 2026-02-18 19:23:25: Config file: config-madlad.yaml
- 2026-02-18 19:23:25: Loading model: google/madlad400-3b-mt
- 2026-02-18 19:23:30: Model loaded on device: cuda:0
- 2026-02-18 19:23:30: Loading input file: my-sub-2.srt
- 2026-02-18 19:23:30: Starting translation...
- 2026-02-18 19:23:41: Progress: 43%
- 2026-02-18 19:23:51: Progress: 87%
- 2026-02-18 19:23:58: Writing results to: my-sub-2-en.srt
```

## Customizing the config file

We need a separate config file for each combinations of:
- Source language
- Target language
- GPU (Because of memory limitations and performance differences.)

Please send in your config files for new languages.
(Each source language requires different "replace-rules". See below.)

```yaml
model:
  # This can either be a local path or a model identifier from Hugging Face Model Hub.
  # If you set 'model.offline-mode' to 'false', then you can use "google/madlad400-3b-mt" here.
  name: google/madlad400-3b-mt

  # A "true" value will not allow the Transformer library to make calls to
  # Huggingface every time you load the model (run the app).
  # The offline mode will only work if 'model.name' contains a folder path instead of a name.
  # The "ture" value is recommended out of privacy concerns, but read the warning below:
  #
  # If the offline mode is forced, then you will not be able to use a model name
  # (like "google/madlad400-3b-mt") in the 'model.name' setting, but you have to use a path
  # to a local folder that contains all files.
  # You can set it to false first, pull the model, then turn it to offline mode.
  # Then the model will still be used from the cache dir: ~/.cache/huggingface/hub/...
  offline-mode: false

  # The only currently supported model type is "madlad".
  type: madlad

  # All prompts will start with this string.
  # {LANG} is a placeholder for the BCP-47 code of the target language,
  #   like "en", "de", "it", etc.
  # Example after substitution: "<2en>"
  prompt-prefix: "<2{LANG}>"

  # You must use a model that supports sentinel tokens.
  # These are used for separating parts of the source text, and keeping
  #   that separation in the translated text.
  # The {ID} placeholder is necessary, because each token needs to be unique.
  # Possible values for the ID: 0, 1, 2, 3, ..., 126, 127
  #  (But only 0 and 1 are used.)
  sentinel-token-template: "<extra_id_{ID}>"

  # How many inferences (prompts) to run in parallel.
  # If this is low, then the GPU will not be fully utilized.
  # If it is high, then it uses a lot of memory:
  #     - For 24 GB VRAM, use: inference-batch-size: 20 (If max context is 12 segments)
  #     - For 16 GB VRAM, use: inference-batch-size: 8 (If max context is 12 segments)
  inference-batch-size: 20

# The 2-3-letter BCP-47 code of the target language.
# (The source language is auto-detected by the model. To make sure the
#   source language is correctly detected, formulate the "document.static-context"
#   in a way that distinguishes it clearly from similar languages.)
target-language: en

# The context window tells the maximum number of characters or segments to use before
#   and after the current segment as a context for translation.
#   It doesn't split segments: If adding a segment would exceed the limit, it is skipped.
context-window:
  max-chars-before: 728
  max-segments-before: 6
  max-chars-after: 728
  max-segments-after: 6

document:
  # The static context is the secondary source of context. It is
  #   always appended before the first window segment in the translation
  #   prompt. You must use the source language. You can use the --one-shot
  #   option of the Hermes Translator app to translate this text alone
  #   to the source language.
  static-context:
    # "Subtitles for an Italian drama movie:"
    "Sottotitoli di un film drammatico italiano:"

  # Regular expression rules for text replacement before translation.
  # When a segment becomes empty after replacements, it will be skipped.
  # (This section is optional. You can remove it.)
  replace-rules:
    # Remove any text within square brackets (e.g., [MUSICA MISTERIOSA], [COLPI DI TOSSE])
    - pattern: "\\[[^\\]]*\\]"
      replacement: ""
    
    # In Italian, "ì" is a common shorthand for "sì"
    - pattern: "([^\\w]+|^)ì([^\\w]+|$)"
      replacement: "\\1sì\\2"
    
    # Same for a standalone "s" (also Italian-specific)
    - pattern: "([^\\w]+|^)s([^\\w]+|$)"
      replacement: "\\1sì\\2"
    
    # Remove any newline and whitespace characters, because those
    #   can make the madlad model behave erratically.
    - pattern: "\\s+"
      replacement: " "

# The start times are the same as in the source subtitles.
# The end times are adjusted based on reading speed.
# The start of the next subtitle limits the length of the current subtitle.
# In case there isn't enough space, the extra duration can be adjusted backwards
# if the previous subtitle allows it. For this, enable "allow-backwards-adjustment".
# (The numerical values are all floating-point.)
subtitle-timing:
  reading-speed-chars-per-second: 14.6
  min-duration-seconds: 0.5
  max-duration-seconds: 5.0
  allow-backwards-adjustment: true

# The path for the log files.
# Can be relative or absolute.
# Creates directories that don't exist.
# Use the {TIME} placeholder to insert the datetime.
# Leave it empty to disable logging.
logging-path: var/run-{TIME}.log
```

## Running the unit tests

```
$ make test
. .venv/bin/activate && python3 -m unittest discover -v -s test/
test_segment_processing (test_segment_processing.TestSegmentProcessing.test_segment_processing) ... ok
test_translation (test_translator.TestTranslator.test_translation) ... ok
test_char_overflow (test_window.TestWindow.test_char_overflow) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.001s

OK
```
