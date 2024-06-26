import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

import os
import sqlite3
import subprocess
import time

from random import randint
from shutil import which
from urllib import error, parse, request

from fetch_video_info import fetch_vid_info
from misc_files import common_vars, check_for_internet_conn
from video_entry import update_video_entry


def get_video_length(file_path):
	ffprobe_path = common_vars.get_ffprobe_path()
	startupinfo = subprocess.STARTUPINFO()
	startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	startupinfo.wShowWindow = subprocess.SW_HIDE
	vid_length = subprocess.run([ffprobe_path, '-v', 'error', '-show_entries', 'format=duration', '-of',
								 'default=noprint_wrappers=1:nokey=1', file_path], stdout=subprocess.PIPE,
											  stderr=subprocess.STDOUT, startupinfo=startupinfo)
	return float(vid_length.stdout)


class ThumbWorker(QtCore.QObject):
	finished = QtCore.pyqtSignal()
	progress = QtCore.pyqtSignal(str, int, int, dict)

	def __init__(self, worker_type, overwrite=False, vidids=None, subdb=None):
		super(ThumbWorker, self).__init__()
		self.worker_type = worker_type
		self.overwrite = overwrite
		self.vidids = vidids
		self.subdb = [subdb]

	def run(self):
		db_conn = sqlite3.connect(common_vars.video_db())
		db_cursor = db_conn.cursor()
		cwd = os.getcwd()
		if self.vidids:
			sub_dbs = self.subdb
		else:
			sub_dbs = [k for k, v in common_vars.sub_db_lookup(reverse=True).items()]
		unable_to_dl = {sub_dbs[i]: [] for i in range(len(sub_dbs))}

		if self.worker_type == 'download':
			for subdb in sub_dbs:
				if self.vidids:
					vids_w_yt = []
					for v_id in self.vidids:
						db_cursor.execute('SELECT video_id, video_youtube_url, vid_thumb_path, primary_editor_username, '
										  'video_title FROM {} WHERE video_youtube_url != "" AND video_youtube_url '
										  'IS NOT NULL AND video_id = ?'.format(subdb), (v_id,))
						vids_tup = db_cursor.fetchone()
						if vids_tup:
							vids_w_yt.append(vids_tup)
				else:
					db_cursor.execute('SELECT video_id, video_youtube_url, vid_thumb_path, primary_editor_username, '
												'video_title FROM {} WHERE video_youtube_url != "" AND video_youtube_url '
												'IS NOT NULL'.format(subdb))
					vids_w_yt = db_cursor.fetchall()
				vid_ctr = 0

				for vid_tup in vids_w_yt:
					if 'yout' in vid_tup[1] and 'watch?v=' in vid_tup[1]:
						url_data = parse.urlparse(vid_tup[1])
						query = parse.parse_qs(url_data.query)
						yt_id = query['v'][0]

						if self.overwrite is False and (vid_tup[2] != '' and vid_tup[2] is not None):
							pass
						else:
							downloaded = True

							try:
								request.urlretrieve('https://img.youtube.com/vi/{}/maxresdefault.jpg'.format(yt_id),
													os.getcwd() + common_vars.thumb_path() + '\\{}.jpg'
													.format(vid_tup[0]))

							except error.HTTPError:
								try:
									request.urlretrieve('https://img.youtube.com/vi/{}/0.jpg'.format(yt_id),
														os.getcwd() + common_vars.thumb_path() + '\\{}.jpg'.
														format(vid_tup[0]))

								except:
									unable_to_dl[subdb].append((vid_tup[3] + ' - ' + vid_tup[4]))
									downloaded = False

							if downloaded:
								db_cursor.execute('UPDATE {} SET vid_thumb_path = ? WHERE video_id = ?'.format(subdb),
															(common_vars.thumb_path() + '\\{}.jpg'.format(vid_tup[0]), vid_tup[0]))
					vid_ctr += 1

					prog_bar_label = common_vars.sub_db_lookup(reverse=True)[subdb] + ': ' + vid_tup[3] + ' - ' + vid_tup[4]
					self.progress.emit(prog_bar_label, vid_ctr, len(vids_w_yt), {})

			self.progress.emit('Done!', 1, 2, unable_to_dl)

			# TODO: Create window showing which thumbnail downloads failed

		elif self.worker_type == 'generate':
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			startupinfo.wShowWindow = subprocess.SW_HIDE

			for subdb in sub_dbs:
				db_cursor.execute('SELECT video_id, local_file, vid_thumb_path, primary_editor_username,'
										 'video_title FROM {} WHERE local_file != "" AND local_file IS NOT NULL'
										 .format(subdb))
				vids_w_local = db_cursor.fetchall()
				vid_ctr = 0

				for vid_tup in vids_w_local:
					video_file_path = vid_tup[1]
					img_output_path = cwd + common_vars.thumb_path() + '\\' + vid_tup[0] + '.jpg'
					vid_length = int(get_video_length(video_file_path))
					time_str = time.strftime('%H:%M:%S', time.gmtime(vid_length / randint(1, 5)))
					subprocess.call([common_vars.get_ffmpeg_path(), '-y', '-i', video_file_path, '-ss', time_str,
									 '-vframes', '1', img_output_path], stdin=subprocess.DEVNULL,
									stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=startupinfo)

					db_cursor.execute('UPDATE {} SET vid_thumb_path = ? WHERE video_id = ?'.format(subdb),
											 (img_output_path, vid_tup[0]))
					vid_ctr += 1

					prog_bar_label = common_vars.sub_db_lookup(reverse=True)[subdb] + ': ' + vid_tup[3] + ' - ' + vid_tup[4]
					self.progress.emit(prog_bar_label, vid_ctr, len(vids_w_local), {})

			self.progress.emit('Done!', 1, 2, {})
		
		elif self.worker_type == 'fetch':
			if check_for_internet_conn.internet_check('https://www.animemusicvideos.org'):
				for subdb in sub_dbs:
					ctr = 0
					db_cursor.execute('SELECT video_id, primary_editor_username, video_title, video_org_url FROM {} '
									  'WHERE video_org_url != "" AND video_org_url IS NOT NULL'.format(subdb))
					db_extract = db_cursor.fetchall()

					for tup in db_extract:
						if 'members_videoinfo' in tup[3]:
							org_info = fetch_vid_info.download_data(tup[3], 'org')

							# Release date
							if org_info['release_date'] != ['', 0, 0]:
								date_list_str = ['0' + str(x) if len(str(x)) == 1 else str(x) for x in
												 org_info['release_date']]
								org_info['release_date'] = '/'.join(date_list_str)
								org_info['release_date_unknown'] = 0
							else:
								org_info['release_date'] = ''
								org_info['release_date_unknown'] = 1

							# Video footage
							org_info['video_footage'] = '; '.join(org_info['video_footage'])

							# Video duration
							if org_info['video_length'] == [-1, -1]:
								org_info['video_length'] = ''
							else:
								org_info['video_length'] = str((org_info['video_length'][0] * 60) +
															   org_info['video_length'][1])

							update_video_entry.update_video_entry(org_info, common_vars.sub_db_lookup(reverse=True)[subdb],
																  vid_id=tup[0])
							ctr += 1
							prog_bar_label = common_vars.sub_db_lookup(reverse=True)[subdb] + ': ' + tup[1] + ' - ' + tup[2]
							self.progress.emit(prog_bar_label, ctr, len(db_extract), {})

			else:
				unresolved_host_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'No response',
															'AnimeMusicVideos.org is currently unresponsive. Check your\n'
															'internet connection or try again later.')
				unresolved_host_win.exec_()

			self.progress.emit('Done!', 1, 2, {})
			self.finished.emit()

		else:
			print('check the code my dude')

		db_conn.commit()
		db_conn.close()


class DataImport(QtWidgets.QMainWindow):
	def __init__(self, screen_size=None):
		super(DataImport, self).__init__()

		# Misc variables
		grid_vert_ind = 0

		# DB connections/cursors
		self.settings_conn = sqlite3.connect(common_vars.settings_db())
		self.settings_cursor = self.settings_conn.cursor()
		self.db_conn = sqlite3.connect(common_vars.video_db())
		self.db_cursor = self.db_conn.cursor()

		# Layouts
		self.gridLayout = QtWidgets.QGridLayout()
		self.gridLayout.setAlignment(QtCore.Qt.AlignTop)

		# Progress bar
		self.pBar = QtWidgets.QProgressBar()
		self.pBar.setGeometry(30, 40, 450, 25)
		self.pBar.setInvertedAppearance(False)
		self.pBar.setTextVisible(True)
		self.pBar.setAlignment(QtCore.Qt.AlignCenter)

		if screen_size is not None:
			self.pBar.move(int((screen_size[0] / 2) - 225), int((screen_size[1] / 2) - 12))
		else:
			self.pBar.move(1000, 600)

		# Widgets
		self.gridLayout.setRowMinimumHeight(grid_vert_ind, 10)
		grid_vert_ind += 1

		# yt-dlp
		self.ytdlpHeader = QtWidgets.QLabel()
		self.ytdlpHeader.setText('<p style="font-size:14px"><b><u>yt-dlp</u></b></p>'
								 'AMV Tracker uses <b>yt-dlp</b> to allow you to download videos from YouTube. If you wish to '
								 'use this function, the<br>'
								 'easiest option is to open PowerShell and type the following, and then restart AMV '
								 'Tracker:<br><br><font face="Courier New">winget install yt-dlp</font><br><br>'
								 'Otherwise, you can download the .exe from '
								 '<a href="https://github.com/yt-dlp/yt-dlp/releases">here</a>. (You will also need to '
								 'download ffmpeg; see below<br>section.) Once downloaded, put the .exe anywhere on '
								 'your computer, and then locate it using the button<br>below.<br><br>'
								 'If you already happen to have yt-dlp installed and available in your Windows PATH '
								 'environment variables,<br>the below box will already be populated and nothing more '
								 'is needed from you.')
		self.ytdlpHeader.setOpenExternalLinks(True)
		self.gridLayout.addWidget(self.ytdlpHeader, grid_vert_ind, 0, 1, 3)
		grid_vert_ind += 1

		self.gridLayout.setRowMinimumHeight(grid_vert_ind, 10)
		grid_vert_ind += 1

		self.ytdlpButton = QtWidgets.QPushButton('Find yt-dlp.exe')
		self.ytdlpTextBox = QtWidgets.QLineEdit()
		self.ytdlpTextBox.setFixedWidth(350)
		self.ytdlpTextBox.setReadOnly(True)
		self.ytdlpTextBox.setText(common_vars.get_ytdlp_path())
		self.gridLayout.addWidget(self.ytdlpButton, grid_vert_ind, 0)
		self.gridLayout.addWidget(self.ytdlpTextBox, grid_vert_ind, 1, 1, 2)
		grid_vert_ind += 1

		self.gridLayout.setRowMinimumHeight(grid_vert_ind, 15)
		grid_vert_ind += 1

		self.frame1 = QtWidgets.QFrame()
		self.frame1.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Sunken)
		self.frame1.setLineWidth(0)
		self.frame1.setMidLineWidth(1)
		self.gridLayout.addWidget(self.frame1, grid_vert_ind, 0, 1, 3)
		grid_vert_ind += 1

		# ffmpeg / ffprobe
		self.ffmpegHeader = QtWidgets.QLabel()
		self.ffmpegHeader.setText('<p style="font-size:14px"><b><u>ffmpeg / ffprobe</u></b></p>'
								  'AMV Tracker uses <b>ffmpeg</b> to both (a) mux video and audio streams downloaded from '
								  'YouTube using yt-dlp,<br>and (b) generate thumbnails from locally-stored video files. '
								  'In order to use these functions, you will need both<br>ffmpeg.exe and ffprobe.exe. '
								  'The easiest way to do this is to open PowerShell and type the following, and then<br>'
								  'restart AMV Tracker:<br><br>'
								  '<font face="Courier New">winget install Gyan.FFmpeg</font><br><br>'
								  'If you\'d rather download ffmpeg from your browser, follow these steps:<br>'
								  '1. Get the latest "Essentials" build from '
								  '<a href="https://www.gyan.dev/ffmpeg/builds/">here</a><br>'
								  '2. Extract all three executables from the /bin folder to some location on your computer '
								  '(if you also plan on using<br>AMV Tracker to download YouTube videos, <b>you must put '
								  'these files in the same folder as yt-dlp.exe</b>).<br>'
								  '3. Use the below buttons to locate ffmpeg.exe and ffprobe.exe.<br><br>'
								  'If you already happen to have ffmpeg installed and available in your Windows PATH '
								  'environment variables,<br>the below boxes will already be populated and nothing more '
								  'is needed from you.')
		self.ffmpegHeader.setOpenExternalLinks(True)
		self.gridLayout.addWidget(self.ffmpegHeader, grid_vert_ind, 0, 1, 3)
		grid_vert_ind += 1

		self.gridLayout.setRowMinimumHeight(grid_vert_ind, 10)
		grid_vert_ind += 1

		self.ffmpegButton = QtWidgets.QPushButton('Find ffmpeg.exe')
		self.ffmpegTextBox = QtWidgets.QLineEdit()
		self.ffmpegTextBox.setFixedWidth(350)
		self.ffmpegTextBox.setReadOnly(True)
		self.ffmpegTextBox.setText(common_vars.get_ffmpeg_path())
		self.gridLayout.addWidget(self.ffmpegButton, grid_vert_ind, 0)
		self.gridLayout.addWidget(self.ffmpegTextBox, grid_vert_ind, 1, 1, 2)
		grid_vert_ind += 1

		self.ffprobeButton = QtWidgets.QPushButton('Find ffprobe.exe')
		self.ffprobeTextBox = QtWidgets.QLineEdit()
		self.ffprobeTextBox.setFixedWidth(350)
		self.ffprobeTextBox.setReadOnly(True)
		self.ffprobeTextBox.setText(common_vars.get_ffprobe_path())
		self.gridLayout.addWidget(self.ffprobeButton, grid_vert_ind, 0)
		self.gridLayout.addWidget(self.ffprobeTextBox, grid_vert_ind, 1, 1, 2)
		grid_vert_ind += 1

		self.gridLayout.setRowMinimumHeight(grid_vert_ind, 15)
		grid_vert_ind += 1

		self.frame2 = QtWidgets.QFrame()
		self.frame2.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Sunken)
		self.frame2.setLineWidth(0)
		self.frame2.setMidLineWidth(1)
		self.gridLayout.addWidget(self.frame2, grid_vert_ind, 0, 1, 3)
		grid_vert_ind += 1

		self.gridLayout.setRowMinimumHeight(grid_vert_ind, 10)
		grid_vert_ind += 1

		# Data fetch / thumb generator
		self.headerLabel = QtWidgets.QLabel()
		self.headerLabel.setText('The below functions allow you to mass import data for entries already in your '
								 'database. If you are looking to\nmass add new video entries to your database, please see '
								 'the "Download video data" buttons in the top-left\nof the main window.')
		self.gridLayout.addWidget(self.headerLabel, grid_vert_ind, 0, 1, 0)
		grid_vert_ind += 1

		self.gridLayout.setRowMinimumHeight(grid_vert_ind, 10)
		grid_vert_ind += 1

		self.fetchOrgDataBtn = QtWidgets.QPushButton('Fetch amv.org data')
		self.fetchOrgDataBtn.setFixedWidth(150)
		self.fetchOrgDataBtn.setToolTip('For all videos in the database which have an AnimeMusicVideos.org video\n'
										'profile URL, this function will update those entries with the data from\n'
										'the .org.')
		self.overwriteDataCheck = QtWidgets.QCheckBox('Overwrite existing data')
		self.overwriteDataCheck.setToolTip('If checked, any data which is found on AnimeMusicVideos.org will over-\n'
										   'write what is in each video entry (fields which do not have a corres-\n'
										   'ponding field on the .org, such as tags, will be untouched).')
		self.gridLayout.addWidget(self.fetchOrgDataBtn, grid_vert_ind, 0)
		# self.gridLayout.addWidget(self.overwriteDataCheck, grid_vert_ind, 1)
		grid_vert_ind += 1

		self.downloadThumbsBtn = QtWidgets.QPushButton('DL thumbs from YouTube')
		self.downloadThumbsBtn.setFixedWidth(150)
		self.downloadThumbsBtn.setToolTip('For all videos which have a YouTube link specified, AMV Tracker will\n'
										  'automatically locate and download the thumbnails.')
		self.gridLayout.addWidget(self.downloadThumbsBtn, grid_vert_ind, 0)

		self.createThumbsBtn = QtWidgets.QPushButton('Generate thumbs from files')
		self.createThumbsBtn.setFixedWidth(150)
		self.createThumbsBtn.setToolTip('For all videos which are stored locally on your machine, AMV Tracker will\n'
										'generate a thumbnail from the video file.')
		self.gridLayout.addWidget(self.createThumbsBtn, grid_vert_ind, 1)

		self.overwriteExistThumbsChk = QtWidgets.QCheckBox('Overwrite existing thumbnails')
		self.overwriteExistThumbsChk.setToolTip('If checked, AMV Tracker will replace any existing thumbnails\n'
												'with those imported/generated; if unchecked, it will skip any\n'
												'videos that already have a thumbnail file specified.')
		self.gridLayout.addWidget(self.overwriteExistThumbsChk, grid_vert_ind, 2)
		grid_vert_ind += 1

		# Signals/slots
		self.ytdlpButton.clicked.connect(lambda: self.find_exe(self.ytdlpButton, self.ytdlpTextBox))
		self.ffmpegButton.clicked.connect(lambda: self.find_exe(self.ffmpegButton, self.ffmpegTextBox))
		self.ffprobeButton.clicked.connect(lambda: self.find_exe(self.ffprobeButton, self.ffprobeTextBox))
		self.fetchOrgDataBtn.clicked.connect(lambda: self.warning_window('fetch'))
		self.downloadThumbsBtn.clicked.connect(lambda: self.get_data('download'))
		self.createThumbsBtn.clicked.connect(lambda: self.warning_window('generate'))

	def check_for_ytdlp(self):
		# Not used here; this check has moved to mainwindow.py (see method exe_check)
		settings_conn = sqlite3.connect(common_vars.settings_db())
		settings_cursor = settings_conn.cursor()
		curr_ytdlp_path = common_vars.get_ytdlp_path()

		if curr_ytdlp_path != '':  # If yt-dlp executable has been moved/deleted since last time it was set
			if not os.path.isfile(curr_ytdlp_path):
				curr_ytdlp_path = ''
				settings_cursor.execute('UPDATE general_settings SET value = "" WHERE setting_name = "yt_dlp_path"')
				settings_conn.commit()

		if curr_ytdlp_path == '':
			if which('yt-dlp'):
				self.ytdlpTextBox.setText(which('yt-dlp'))
				settings_cursor.execute('UPDATE general_settings SET value = ? WHERE setting_name = "yt_dlp_path"',
										(which('yt-dlp'),))

		settings_conn.commit()
		settings_conn.close()

	def find_exe(self, btn_pressed, text_box):
		settings_conn = sqlite3.connect(common_vars.settings_db())
		settings_cursor = settings_conn.cursor()

		exe_name = btn_pressed.text().split(' ')[1]

		if text_box.text() == '':
			open_file_path = os.getcwd()
		else:
			open_file_path = text_box.text()

		fpath = QtWidgets.QFileDialog.getOpenFileName(self, 'Find {}'.format(exe_name), open_file_path,
																'.exe files (*.exe)')[0]

		if not fpath:  # User cancels getOpenFileName window
			pass

		elif exe_name not in fpath:
			err_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
											'It appears that the file you chose is not {}. No action has been\n'
											'taken. Please try again and select the correct executable.'.format(exe_name))
			err_win.exec_()

		else:
			if exe_name == 'yt-dlp.exe':
				self.ytdlpTextBox.setText(fpath)
				setting_name = 'yt_dlp_path'
			elif exe_name == 'ffmpeg.exe':
				self.ffmpegTextBox.setText(fpath)
				setting_name = 'ffmpeg_path'
			else:
				self.ffprobeTextBox.setText(fpath)
				setting_name = 'ffprobe_path'

			settings_cursor.execute('UPDATE general_settings SET value = ? WHERE setting_name = "{}"'.format(setting_name),
									(fpath,))

		settings_conn.commit()
		settings_conn.close()

	def warning_window(self, btn_pressed):
		if btn_pressed == 'generate':
			msg = 'Warning: For databases that have a large number of videos with\n' \
				  'local file paths (200+), this operation will likely take a while to\n' \
				  'complete. Ok to proceed?'

		elif btn_pressed == 'fetch':
			msg = 'Warning: For databases that have a large number of videos with\n' \
				  'AnimeMusicVideos.org video profile URLs (500+), this operation\n' \
				  'will likely take a while to complete. Ok to proceed?'

		else:
			msg = 'Press "No", check the code.'

		warning_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Warning', msg,
											QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
		result = warning_win.exec_()
		if result == QtWidgets.QMessageBox.Yes:
			self.get_data(btn_pressed)

	def get_data(self, btn_pressed, vidids=None, subdb=None):
		self.thrd = QtCore.QThread()
		self.worker = ThumbWorker(btn_pressed, overwrite=self.overwriteExistThumbsChk.isChecked(), vidids=vidids,
								  subdb=subdb)
		self.worker.moveToThread(self.thrd)

		if btn_pressed == 'download':
			self.pBar.setWindowTitle('Downloading...')
		elif btn_pressed == 'fetch':
			self.pBar.setWindowTitle('Fetching...')
		else:
			self.pBar.setWindowTitle('Generating...')
		self.pBar.show()

		self.thrd.start()
		self.thrd.started.connect(self.worker.run)
		self.worker.finished.connect(self.thrd.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.worker.progress.connect(self.show_thumb_progress)
		self.thrd.finished.connect(self.thrd.deleteLater)
		self.thrd.finished.connect(self.pBar.close)

	def show_thumb_progress(self, label, n, total, un_dl_dict):
		if label == 'Done!':
			# self.not_downloaded_win = unable_to_dl_thumb.UndownloadedThumbsWin(un_dl_dict)
			# self.not_downloaded_win.exec_()

			self.pBar.setFormat(label)
			self.thrd.quit()

		else:
			self.pBar.setFormat(label + ' (' + str(n) + '/' + str(total) + ')')

		self.pBar.setMaximum(total - 1)
		self.pBar.setValue(n)
