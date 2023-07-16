import sqlite3
import os

from misc_files import common_vars


def check_for_thumb_path():
	"""
	Checks to ensure that the thumbnail path exists in the current DB's misc_settings table. If it doesn't, it checks
	to ensure that the thumbnail directory exists, creates it if it doesn't, and sets the value in misc_settings to the
	correct thumb_path.
	"""
	cwd = os.getcwd()
	db_conn = sqlite3.connect(common_vars.video_db())
	db_cursor = db_conn.cursor()

	db_cursor.execute('SELECT value FROM misc_settings WHERE setting_name = "thumbnail_path"')
	thumb_path = db_cursor.fetchone()[0]
	thumb_dir_name = thumb_path.replace('\\', '/').split('/')[-1]
	db_path = common_vars.video_db()
	db_name = db_path.replace('\\', '/').split('/')[-1]
	new_thumb_path = cwd + '\\thumbnails\\{}'.format(db_name)[:-3]

	if thumb_path == '' or thumb_dir_name != db_name:
		if not os.path.isdir(new_thumb_path):
			os.makedirs(new_thumb_path)

		db_cursor.execute('UPDATE misc_settings SET value = ? WHERE setting_name = "thumbnail_path"',
						  (new_thumb_path,))
		db_conn.commit()

	else:  # Thumbnail path is correctly identified in misc_settings -- nothing to do
		pass

	db_conn.close()
