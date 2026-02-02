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

- [Setup on Debian](#setup-on-debian)
- [Usage](#usage)

<!-- /TOC -->

# Setup on Debian 13

- Install the NVIDIA and CUDA drivers. My current (2026 January) versions are:
    - Driver version: 590.44.01
    - CUDA version: 13.1
    
    (If you install newer versions, then some libraries might not work.)
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
      make run [config-file] [document-file] > [output-file]
           Contextual translation of the document-file.
           The config-file is a '.yaml' file that defines the translation settings.
           The result is written to the standard output,
           which can be redirected to an output-file.

      make run --dry-run [config-file] [document-file] > [output-file]
           Executes only the regex replacements defined in the config-file,
           without loading the model.

      make run --one-shot [target-language-code] "text-segment"
           Translates a single text segment without context and config file.
           Outputs the translated text segment to standard output.
           You can use this for translating the 'static context' for the config file.
           The target-language-code is in BCP-47 format (e.g., 'en' for English).

  make clean  - Remove the Python virtual environment.
  make test   - Execute the unit tests.
```
