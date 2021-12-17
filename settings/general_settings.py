import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

#import ffmpeg
import os
import sqlite3
import subprocess

from urllib import error, parse, request

from misc_files import common_vars


def get_video_length(file_path):
	vid_length = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
								 'default=noprint_wrappers=1:nokey=1', file_path],
								stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	return float(vid_length.stdout)


class ThumbWorker(QtCore.QObject):
	finished = QtCore.pyqtSignal()
	progress = QtCore.pyqtSignal(str, int, int)

	def __init__(self, worker_type, overwrite=False):
		super(ThumbWorker, self).__init__()
		self.worker_type = worker_type
		self.overwrite = overwrite

	def run(self):
		thumbs_db_conn = sqlite3.connect(common_vars.video_db())
		thumbs_db_cursor = thumbs_db_conn.cursor()
		cwd = os.getcwd()
		sub_dbs = [k for k, v in common_vars.sub_db_lookup(reverse=True).items()]
		update_thumb_path = []
		unable_to_dl = {sub_dbs[i]: [] for i in range(len(sub_dbs))}

		if self.worker_type == 'download':
			for subdb in sub_dbs:
				thumbs_db_cursor.execute('SELECT video_id, video_youtube_url, vid_thumb_path, primary_editor_username, '
											'video_title FROM {} WHERE video_youtube_url != "" AND video_youtube_url '
											'IS NOT NULL'.format(subdb))
				vids_w_yt = thumbs_db_cursor.fetchall()
				vid_ctr = 0

				for vid_tup in vids_w_yt:
					url_data = parse.urlparse(vid_tup[1])
					query = parse.parse_qs(url_data.query)
					yt_id = query['v'][0]
					if self.overwrite is False and (vid_tup[2] != '' and vid_tup[2] is not None):
						pass
					else:
						try:
							request.urlretrieve('https://img.youtube.com/vi/{}/maxresdefault.jpg'.format(yt_id),
												cwd + '/thumbnails/{}.jpg'.format(vid_tup[0]))
							update_thumb_path.append((vid_tup[0], cwd + '/thumbnails/{}.jpg'.format(vid_tup[0])))

						except error.HTTPError:
							try:
								request.urlretrieve('https://img.youtube.com/vi/{}/0.jpg'.format(yt_id),
													cwd + '/thumbnails/{}.jpg'.format(vid_tup[0]))
								update_thumb_path.append((vid_tup[0], cwd + '/thumbnails/{}.jpg'.format(vid_tup[0])))
							except:
								unable_to_dl[subdb].append(vid_tup[0])

					thumbs_db_cursor.execute('UPDATE {} SET vid_thumb_path = ? WHERE video_id = ?'.format(subdb),
												(cwd + '/thumbnails/{}.jpg'.format(vid_tup[0]), vid_tup[0]))
					vid_ctr += 1

					prog_bar_label = common_vars.sub_db_lookup(reverse=True)[subdb] + ': ' + vid_tup[3] + ' - ' + vid_tup[4]
					self.progress.emit(prog_bar_label, vid_ctr, len(vids_w_yt))

			# TODO: Create window showing which thumbnail downloads failed

		elif self.worker_type == 'generate':
			for subdb in sub_dbs:
				thumbs_db_cursor.execute('SELECT video_id, local_file, vid_thumb_path, primary_editor_username,'
										 'video_title FROM {} WHERE local_file != "" AND local_file IS NOT NULL'
										 .format(subdb))
				vids_w_local = thumbs_db_cursor.fetchall()
				vid_ctr = 0

				for vid_tup in vids_w_local:
					video_file_path = vid_tup[1]
					img_output_path = cwd + '/thumbnails/test/' + vid_tup[0] + '.jpg'
					vid_length = get_video_length(video_file_path)
					vid_ctr += 1

					self.progress.emit(vid_tup[0], vid_ctr, len(vids_w_local))

		else:
			print('check the code my dude')

		thumbs_db_conn.commit()
		thumbs_db_conn.close()


class GeneralSettings(QtWidgets.QMainWindow):
	def __init__(self):
		super(GeneralSettings, self).__init__()

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
		self.pBar.setGeometry(30, 40, 300, 25)
		self.pBar.setInvertedAppearance(False)
		self.pBar.setTextVisible(True)
		self.pBar.setAlignment(QtCore.Qt.AlignCenter)
		self.pBar.move(1000, 600)

		# Widgets
		self.downloadThumbsBtn = QtWidgets.QPushButton('Download thumbnails from YouTube')
		self.downloadThumbsBtn.setFixedWidth(200)
		self.downloadThumbsBtn.setToolTip('For all videos which have a YouTube link specified, AMV Tracker will\n'
										  'automatically locate and download the thumbnails.')
		self.gridLayout.addWidget(self.downloadThumbsBtn, grid_vert_ind, 0)

		self.createThumbsBtn = QtWidgets.QPushButton('Generate thumbnails from video files')
		self.createThumbsBtn.setFixedWidth(200)
		self.createThumbsBtn.setToolTip('For all videos which are stored locally on your machine, AMV Tracker will\n'
										'generate a thumbnail from the video file.')
		self.gridLayout.addWidget(self.createThumbsBtn, grid_vert_ind, 1)
		grid_vert_ind += 1

		self.overwriteExistThumbsChk = QtWidgets.QCheckBox('Overwrite existing thumbnails')
		self.overwriteExistThumbsChk.setToolTip('If checked, AMV Tracker will replace any existing thumbnails\n'
												'with those imported/generated; if unchecked, it will skip any\n'
												'videos that already have a thumbnail file specified.')
		self.gridLayout.addWidget(self.overwriteExistThumbsChk, grid_vert_ind, 0)
		grid_vert_ind += 1

		# Signals/slots
		self.downloadThumbsBtn.clicked.connect(lambda: self.get_thumbs('download'))
		self.createThumbsBtn.clicked.connect(lambda: self.get_thumbs('generate'))

	def get_thumbs(self, btn_pressed):
		self.thrd = QtCore.QThread()
		self.worker = ThumbWorker(btn_pressed, overwrite=self.overwriteExistThumbsChk.isChecked())
		self.worker.moveToThread(self.thrd)

		if btn_pressed == 'download':
			self.pBar.setWindowTitle('Downloading...')
		else:
			self.pBar.setWindowTitle('Generating...')
		self.pBar.show()

		self.thrd.started.connect(self.worker.run)
		self.worker.finished.connect(self.thrd.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thrd.finished.connect(self.thrd.deleteLater)
		self.worker.progress.connect(self.show_thumb_progress)
		self.thrd.finished.connect(self.pBar.close)

		self.thrd.start()

	def show_thumb_progress(self, label, n, total):
		self.pBar.setFormat(label + ' (' + str(n) + '/' + str(total) + ')')
		self.pBar.setMaximum(total - 1)
		self.pBar.setValue(n)
