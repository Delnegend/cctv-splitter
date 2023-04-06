# CCTV splitter

## Introduction
I have a script that merge multiple 1-minute segments into multiple 1-day surveillance videos that I forgot to sort the listed files by filename/date. This script is for splitting them back into 1-minute.

## Usage
### Requirements
- Python 3.10+
- [ffmpeg](https://ffmpeg.org/download.html)
- [tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html)

### Preparation
This repository uses [pipenv](https://pipenv.pypa.io/en/latest/) for dependency management. Install it first.

```bash
pip install pipenv
```

Then install the dependencies.

```bash
pipenv install
```

After that, you can check the help message by:

```bash
py .\split_video.py -h
```

```bash
usage: split_video.py [-h] -i INPUT_VIDEO [-s START_FRAME] [-e END_FRAME] [-o OUTPUT_DIR]

Split a video into multiple videos based on the difference between specific regions of each frame

options:
  -h, --help            show this help message and exit
  -i INPUT_VIDEO, --input_video INPUT_VIDEO
                        The video file to split
  -s START_FRAME, --start_frame START_FRAME
                        The frame number to start splitting from
  -e END_FRAME, --end_frame END_FRAME
                        The frame number to stop splitting at, if 0, it will split until the end of the video, if larger than the total number of frames, it will split until the end
                        of the video
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        The directory to output the split videos