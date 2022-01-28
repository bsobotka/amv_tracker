from os import path, getcwd


def check():
	if path.isfile(getcwd() + '\\ffmpeg.exe') and path.isfile(getcwd() + '\\ffprobe.exe'):
		return True
	else:
		return False
