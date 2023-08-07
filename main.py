# Usage: python split_video.py <video_file>
# Description: Split a video into multiple videos based on the difference between specific regions of each frame

import argparse
import multiprocessing
import os
import shutil
import subprocess as sp
import sys

import cv2
import numpy as np

from pkg import OCR_to_int, frame_to_timecode, is_similar, path


class COORDS:
    minute = [[353, 0], [405, 45]]  # for differentiating frames + file naming
    hour = [[286, 0], [338, 45]]  # for file naming only


SENSITIVITY = 0.85  # how sensitive the difference between frames (hour/minute region) should be

ALWAYS_USING_OCR = True  # if True, it will always use OCR to get the minute and hour values, if False, it will use the difference between the frames to get the minute and hour values


def read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split a video into multiple videos based on the difference between specific regions of each frame"
    )
    parser.add_argument("-i", "--input_video", required=True, help="The video file to split")
    parser.add_argument("-s", "--start_frame", default=0, type=int, help="The frame number to start splitting from")
    parser.add_argument(
        "-e",
        "--end_frame",
        default=0,
        type=int,
        help="The frame number to stop splitting at, if 0, it will split until the end of the video, if larger than the total number of frames, it will split until the end of the video",
    )
    parser.add_argument("-o", "--output_dir", default=".", help="The directory to output the split videos")
    return parser.parse_args()


def main(input_video: str, start_frame: int, end_frame: int, output_dir: str):
    # list of frame numbers where the video should be split, this data is just for ffmpeg
    marker_list: list[int] = [0]

    # open the video file
    video = cv2.VideoCapture(input_video)

    # set the frame counter to the start_from_frame
    if start_frame > 0:
        video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # get the framerate of the video for converting frame number to timecode later
    framerate = video.get(cv2.CAP_PROP_FPS)

    # store the previous frame data for comparison
    previous_frame_data: dict[str, np.ndarray] = {"minute": np.array([]), "hour": np.array([])}

    previous_actual: dict[str, int] = {"minute": -1, "hour": -1}

    # frame_count and total_frames are purely for determining when to stop the loop
    frame_count: int = 0
    total_frames: int = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    if end_frame > 0 and end_frame < total_frames:
        total_frames = end_frame

    while frame_count < total_frames - 1:
        frame_count += 1
        if frame_count == 1:
            # read current frame, there's an "invisible frame counter" where it increments by 1 each time we call video.read()
            ret, frame = video.read()
            if not ret:
                break

            # "crop" the numpy array to get the minute and hour regions and store them as previous frame data
            y1 = COORDS.minute[0][1]
            y2 = COORDS.minute[1][1] + 1
            x1 = COORDS.minute[0][0]
            x2 = COORDS.minute[1][0] + 1
            previous_frame_data["minute"] = frame[y1:y2, x1:x2]

            if ALWAYS_USING_OCR:
                previous_actual["minute"] = OCR_to_int(previous_frame_data["minute"])

            y1 = COORDS.hour[0][1]
            y2 = COORDS.hour[1][1] + 1
            x1 = COORDS.hour[0][0]
            x2 = COORDS.hour[1][0] + 1
            previous_frame_data["hour"] = frame[y1:y2, x1:x2]

            if ALWAYS_USING_OCR:
                previous_actual["hour"] = OCR_to_int(previous_frame_data["hour"])

            continue

        # read current frame and get the crop section image of the frame as a numpy array
        ret, frame = video.read()
        if not ret:
            break

        current_frame_data = {}

        # "crop" the numpy array to get the minute and hour regions
        y1 = COORDS.minute[0][1]
        y2 = COORDS.minute[1][1] + 1
        x1 = COORDS.minute[0][0]
        x2 = COORDS.minute[1][0] + 1
        current_frame_data["minute"] = frame[y1:y2, x1:x2]
        y1 = COORDS.hour[0][1]
        y2 = COORDS.hour[1][1] + 1
        x1 = COORDS.hour[0][0]
        x2 = COORDS.hour[1][0] + 1
        current_frame_data["hour"] = frame[y1:y2, x1:x2]

        current_actual: dict[str, int] = {"minute": 0, "hour": 0}

        # check if the minute or hour changes
        if not ALWAYS_USING_OCR:
            minute_changes = not is_similar(current_frame_data["minute"], previous_frame_data["minute"])
            hour_changes = not is_similar(current_frame_data["hour"], previous_frame_data["hour"])
        else:
            # current_actual["hour"] = OCR_to_int(current_frame_data["hour"])
            # hour_changes = current_actual["hour"] != previous_actual["hour"]

            # current_actual["minute"] = OCR_to_int(current_frame_data["minute"])
            # minute_changes = current_actual["minute"] != previous_actual["minute"]

            # parallelize the OCR
            with multiprocessing.Pool(2) as p:
                current_actual["hour"], current_actual["minute"] = p.map(
                    OCR_to_int, [current_frame_data["hour"], current_frame_data["minute"]]
                )
            hour_changes = current_actual["hour"] != previous_actual["hour"]
            minute_changes = current_actual["minute"] != previous_actual["minute"]

        if minute_changes or hour_changes:
            marker_list.append(frame_count)

            # <input file name> <actual time> (<start_frame>).mp4
            file_name = os.path.splitext(input_video)[0]
            if not ALWAYS_USING_OCR:
                actual_hour = OCR_to_int(previous_frame_data["hour"])
                actual_minute = OCR_to_int(previous_frame_data["minute"])
            else:
                actual_hour = previous_actual["hour"]
                actual_minute = previous_actual["minute"]
            start_frame = marker_list[-2]

            frame_count_length = len(str(total_frames))
            output_file = f"{file_name} {actual_hour:02d}.{actual_minute:02d} ({start_frame:0{frame_count_length}}).mp4"
            output_file = path.norm(os.path.join(path.norm(output_dir), path.norm(output_file)))

            print(output_file)

            # convert frame number to timecode to feed into ffmpeg and run
            begin_time = frame_to_timecode(marker_list[-2], framerate)
            end_time = frame_to_timecode(marker_list[-1] - 1, framerate)  # -1 because we want the frame before the marker
            sp.run(
                [
                    "ffmpeg",
                    "-i",
                    input_video,
                    "-ss",
                    begin_time,
                    "-to",
                    end_time,
                    "-c:v",
                    "copy",
                    "-c:a",
                    "libopus",
                    "-y",
                    output_file,
                ],
                stdout=sp.DEVNULL,
                stderr=sp.DEVNULL,
            )

        # store the current frame as previous frame
        previous_frame_data = current_frame_data
        if ALWAYS_USING_OCR:
            previous_actual = current_actual


if __name__ == "__main__":
    not_installed = [app for app in ["ffmpeg", "tesseract"] if shutil.which(app) is None]
    if not_installed:
        print(f"{', '.join(not_installed)} not found in PATH")
        sys.exit(1)

    try:
        args = read_args()

        if not os.path.isfile(args.input_video):
            print("Input video file does not exist")
            sys.exit(1)

        if not os.path.isdir(args.output_dir):
            os.mkdir(args.output_dir)

        main(args.input_video, args.start_frame, args.end_frame, args.output_dir)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
        sys.exit(1)
