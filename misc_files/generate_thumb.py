import sqlite3
import subprocess
import time

from random import uniform

from misc_files import common_vars


def thumb_generator(video_fpath, output_fpath, ind, vid_length):
	settings_conn = sqlite3.connect(common_vars.settings_db())
	settings_cursor = settings_conn.cursor()
	settings_cursor.execute('SELECT * FROM entry_settings WHERE setting_name = "num_of_thumbs"')
	num_thumbs = int(settings_cursor.fetchone()[1])

	ffmpeg_path = common_vars.get_ffmpeg_path()
	rand_num = round(uniform(0.02, 0.19), 2)
	startupinfo = subprocess.STARTUPINFO()
	startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	startupinfo.wShowWindow = subprocess.SW_HIDE

	num = vid_length * ((ind * (1/num_thumbs)) - rand_num)
	timecode = time.strftime('%H:%M:%S', time.gmtime(num))
	subprocess.call([ffmpeg_path, '-y', '-i', video_fpath, '-ss', timecode, '-vframes', '1', output_fpath],
					stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
					startupinfo=startupinfo)

	settings_conn.close()
