import subprocess
import time

from random import uniform


def thumb_generator(video_fpath, ind, output_fpath):
	rand_num = round(uniform(0.02, 0.19), 2)
	startupinfo = subprocess.STARTUPINFO()
	startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	startupinfo.wShowWindow = subprocess.SW_HIDE

	vid_length = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
									   'default=noprint_wrappers=1:nokey=1', video_fpath],
									  stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
									  stderr=subprocess.DEVNULL, startupinfo=startupinfo).stdout)

	num = vid_length * ((ind * (1/5)) - rand_num)
	timecode = time.strftime('%H:%M:%S', time.gmtime(num))
	subprocess.call(['ffmpeg', '-y', '-i', video_fpath, '-ss', timecode, '-vframes', '1', output_fpath],
					stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
					startupinfo=startupinfo)

