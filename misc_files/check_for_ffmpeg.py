from os import path, getcwd
from shutil import which


def check():
    if which("ffmpeg") and which("ffprobe"):
        return True
    elif path.isfile(getcwd() + "\\ffmpeg.exe") and path.isfile(getcwd() + "\\ffprobe.exe"):
        return True
    else:
        return False
