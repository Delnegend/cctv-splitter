def frame_to_timecode(frame: int, framerate: float) -> str:
    """From frame number to timecode"""

    # convert frame to seconds
    seconds = frame / framerate

    # convert seconds to hh:mm:ss.ms
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"