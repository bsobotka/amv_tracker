import subprocess


def return_duration(fpath):
	startupinfo = subprocess.STARTUPINFO()
	startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	startupinfo.wShowWindow = subprocess.SW_HIDE

	vid_length = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
									   'default=noprint_wrappers=1:nokey=1', fpath],
									  stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
									  stderr=subprocess.DEVNULL, startupinfo=startupinfo).stdout)
	return vid_length

