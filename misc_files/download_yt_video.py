import ctypes
import pytube
import sqlite3

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

from os import getcwd, path, remove

from misc_files import common_vars

CP_console = f"cp{ctypes.cdll.kernel32.GetConsoleOutputCP()}"


class DownloadFromYouTube(QtWidgets.QDialog):
	# TODO: Allow user to select default directory to save videos to
	def __init__(self, url, vid_editor, vid_title):
		super(DownloadFromYouTube, self).__init__()
		width = 540
		self.url = url
		self.vidEditor = vid_editor
		self.vidTitle = vid_title
		self.path = ''
		self.format_list = []

		self.hLayout1 = QtWidgets.QHBoxLayout()
		self.hLayout2 = QtWidgets.QHBoxLayout()
		self.hLayout3 = QtWidgets.QHBoxLayout()
		self.hLayout4 = QtWidgets.QHBoxLayout()
		self.vLayoutMaster = QtWidgets.QVBoxLayout()

		self.savePathButton = QtWidgets.QPushButton('Save video to...')
		self.savePathButton.setFixedWidth(125)
		self.savePathButton.setDisabled(True)
		self.savePathBox = QtWidgets.QLineEdit()
		self.savePathBox.setFixedWidth(480)
		self.savePathBox.setReadOnly(True)
		self.savePathBox.setDisabled(True)

		self.videoFormatLabel = QtWidgets.QLabel()
		self.videoFormatLabel.setText('Video format:')
		self.videoFormatDrop = QtWidgets.QComboBox()
		self.videoFormatDrop.setFixedWidth(width)

		self.audioFormatLabel = QtWidgets.QLabel()
		self.audioFormatLabel.setText('Audio format:')
		self.audioFormatDrop = QtWidgets.QComboBox()
		self.audioFormatDrop.setFixedWidth(width)
		
		self.statusBox = QtWidgets.QTextEdit()
		self.statusBox.setReadOnly(True)
		self.statusBox.setFixedSize(300, 80)

		self.closeButton = QtWidgets.QPushButton('Close')
		self.closeButton.setDisabled(True)
		self.downloadButton = QtWidgets.QPushButton('Download selected')
		self.downloadButton.setDisabled(True)
		self.downloadButton.setToolTip('Downloads and merges the selected audio and video formats specified above.')
		self.download720Button = QtWidgets.QPushButton('Download 720p')
		self.download720Button.setDisabled(True)
		self.download720Button.setToolTip('Finds the best 720p format and downloads it (ignoring whatever is selected\n'
										  'above). If 720p is not available, will download the next-highest resolution.')
		self.download1080Button = QtWidgets.QPushButton('Download 1080p')
		self.download1080Button.setDisabled(True)
		self.download1080Button.setToolTip('Finds the best 1080p format and downloads it (ignoring whatever is selected\n'
										  'above). If 1080p is not available, will download the next-highest resolution.')

		# Layout
		self.hLayout1.addWidget(self.savePathButton, alignment=QtCore.Qt.AlignLeft)
		self.hLayout1.addWidget(self.savePathBox, alignment=QtCore.Qt.AlignLeft)
		self.vLayoutMaster.addLayout(self.hLayout1)

		self.hLayout2.addWidget(self.videoFormatLabel)
		self.hLayout2.addWidget(self.videoFormatDrop, alignment=QtCore.Qt.AlignLeft)
		self.vLayoutMaster.addLayout(self.hLayout2)

		self.hLayout3.addWidget(self.audioFormatLabel)
		self.hLayout3.addWidget(self.audioFormatDrop, alignment=QtCore.Qt.AlignLeft)
		self.vLayoutMaster.addLayout(self.hLayout3)
		self.vLayoutMaster.addSpacing(15)

		self.vLayoutMaster.addWidget(self.statusBox, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addSpacing(15)

		self.hLayout4.addWidget(self.closeButton)
		self.hLayout4.addWidget(self.downloadButton)
		self.hLayout4.addWidget(self.download720Button)
		self.hLayout4.addWidget(self.download1080Button)
		self.vLayoutMaster.addLayout(self.hLayout4)

		# Signals / slots
		self.savePathButton.clicked.connect(self.get_path)
		self.savePathBox.textChanged.connect(self.enable_disable_dl_buttons)
		self.closeButton.clicked.connect(self.reject)
		self.downloadButton.clicked.connect(lambda: self.dl_start(self.path))
		self.download720Button.clicked.connect(lambda: self.dl_start(self.path, format_720=True))
		self.download1080Button.clicked.connect(lambda: self.dl_start(self.path, format_1080=True))

		# Run
		self.format_start()

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setFixedSize(self.sizeHint())
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Download from YouTube')
		self.show()

	def enable_disable_dl_buttons(self):
		if self.savePathBox.text() != '':
			self.downloadButton.setEnabled(True)
			self.download720Button.setEnabled(True)
			self.download1080Button.setEnabled(True)
		else:
			self.downloadButton.setDisabled(True)
			self.download720Button.setDisabled(True)
			self.download1080Button.setDisabled(True)

	def get_path(self):
		settings_conn = sqlite3.connect(common_vars.settings_db())
		settings_cursor = settings_conn.cursor()
		settings_cursor.execute('SELECT value FROM entry_settings WHERE setting_name = "default_yt_dl_path"')
		save_dir = settings_cursor.fetchone()[0]
		full_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '{}/{} - {}'
														  .format(save_dir, self.vidEditor, self.vidTitle))
		self.path = full_path[0].replace('\\', '/')
		if self.path:
			self.savePathBox.setText(self.path)

	def dl_output_ready(self):
		self.statusBox.clear()
		output = str(self.dl_process.readAll().data().decode('mbcs'))
		self.statusBox.setText(output)

	def dl_output_finished(self):
		self.statusBox.clear()
		self.statusBox.setText('Done!')
		compl_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Download finished',
										  'Video download complete.')
		if compl_win.exec_():
			self.accept()

	def format_output_ready(self):
		output = str(self.format_process.readAll(), encoding='utf8').rstrip()
		if 'mp4' in output or 'mkv' in output:
			self.format_list.append(output)

	def show_formats(self):
		QtWidgets.QApplication.restoreOverrideCursor()
		final_video_output_list = []
		final_audio_output_list = []
		out = ','.join(self.format_list)
		out = out.partition('\n')[2]
		mylist = out.rsplit('\n')
		for item in mylist:
			if 'mp4' in item and 'audio only' not in item:
				final_video_output_list.append(' '.join(item.split()))

		for item in mylist:
			if 'audio only' in item:
				final_audio_output_list.append(' '.join(item.split()))

		self.videoFormatDrop.clear()
		self.videoFormatDrop.addItems(final_video_output_list)
		self.audioFormatDrop.clear()
		self.audioFormatDrop.addItems(final_audio_output_list)
		self.savePathButton.setEnabled(True)
		self.savePathBox.setEnabled(True)
		self.savePathBox.setPlaceholderText('You must select a place to save before you can download the video')
		self.closeButton.setEnabled(True)
	
	def format_start(self):
		QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
		self.format_process = QtCore.QProcess()
		self.format_process.start('yt-dlp', ['-F', self.url])
		self.format_process.readyRead.connect(self.format_output_ready)
		self.format_process.finished.connect(self.show_formats)

	def dl_start(self, fpath, format_720=False, format_1080=False):
		# yt-dlp does not overwrite existing files with the same name by default, so they must be manually removed first
		if path.isfile(fpath + '.mp4'):
			remove(fpath + '.mp4')

		vid_quality = self.videoFormatDrop.currentText().partition(' ')[0]
		audio_quality = self.audioFormatDrop.currentText().partition(' ')[0]
		if format_720:
			args = ['--format',
					'bestvideo[height<=720][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best',
					'-o',
					'{}.%(ext)s'.format(fpath),
					'{}'.format(self.url)]
		elif format_1080:
			args = ['--format',
					'bestvideo[height<=1080][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best',
					'-o',
					'{}.%(ext)s'.format(fpath),
					'{}'.format(self.url)]
		else:
			args = ['--format',
					'{}+{}'.format(vid_quality, audio_quality),
					'-o',
					'{}.%(ext)s'.format(fpath),
					'--merge-output-format',
					'mp4',
					'{}'.format(self.url)]
		self.dl_process = QtCore.QProcess()
		self.dl_process.start(common_vars.get_ytdlp_path(), args)
		self.dl_process.readyRead.connect(self.dl_output_ready)
		self.dl_process.finished.connect(self.dl_output_finished)

		#self.dl_process.start('yt-dlp', ['--format', '"bestvideo[height<=720][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best"',
		#							  '-o', '"{}.%(ext)s" {}'.format(self.path, self.url)])

		# subprocess.run(
		#	'yt-dlp --format "bestvideo[height<=1080][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best" '
		#	'-o "{}.%(ext)s" {}'.format(path, url))

		# subprocess.run('yt-dlp -S res:1080 -o "{}.%(ext)s" {}'.format(path, url))
		# with yt_dlp.YoutubeDL() as ydl:
		#	ydl.download([url])


## ALL BELOW CODE IS OUTDATED. It makes use of broken PyTube functions, and no longer works. I am keeping the code
## in AMV Tracker just in case, but it is no longer referenced anywhere throughout the program. The above method
## (which uses yt-dlp) is the one now used to download videos from YouTube.

class Worker(QtCore.QObject):
	finished = QtCore.pyqtSignal()
	progress = QtCore.pyqtSignal(str, int, int)

	def __init__(self, url, save_path, fname):
		super(Worker, self).__init__()
		self.url = url
		self.save_path = save_path
		self.fname = fname
		self.perc_dl = 0

	def run(self):
		try:
			self.download_video()

		except:
			err_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
											'PyTube (library which supports this functionality) needs to be updated.<br>'
											'Please raise an issue <a href="https://github.com/bsobotka/amv_tracker/issues">here</a>. In '
											'the meantime, please use one of these tools<br>'
											'to download the video from YouTube:<br>'
											'<p>'
											'<a href="https://yt1s.io/en49">YT1s.io</a><br>'
											'<a href="https://github.com/ytdl-org/youtube-dl/">youtube-dl</a><br>'
											'<a href="https://www.4kdownload.com/welcome-1">4K Video Downloader</a>')
			err_win.exec_()

	def download_video(self):
		yt = pytube.YouTube(self.url, on_progress_callback=self.progress_function)
		stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
		stream.download(output_path=self.save_path, filename=self.fname, skip_existing=False)

	def progress_function(self, stream, chunk, bytes_remaining):
		curr = stream.filesize - bytes_remaining
		per_downloaded = round((curr / stream.filesize) * 100, 1)
		self.perc_dl = per_downloaded

		if self.perc_dl < 100:
			self.progress.emit('Downloading: {}%'.format(str(self.perc_dl)), int(self.perc_dl), 100)

		else:
			self.progress.emit('Done!', 100, 100)
			self.finished.emit()


class DownloadFromYT(QtWidgets.QDialog):
	def __init__(self, url, save_path, fname):
		super(DownloadFromYT, self).__init__()
		self.url = url
		self.save_path = save_path
		self.fname = fname

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayout = QtWidgets.QHBoxLayout()
		self.hLayout.setAlignment(QtCore.Qt.AlignRight)

		self.label = QtWidgets.QLabel()
		self.label.setText('Downloading video')

		self.pBar = QtWidgets.QProgressBar()
		self.pBar.setTextVisible(True)
		self.pBar.setFixedWidth(200)
		self.pBar.setAlignment(QtCore.Qt.AlignCenter)
		self.pBar.setMaximum(100)
		self.pBar.setFormat('Downloading: 0%')

		self.noButton = QtWidgets.QPushButton('No')
		self.noButton.setFixedWidth(50)
		self.noButton.hide()
		self.yesButton = QtWidgets.QPushButton('Yes')
		self.yesButton.setFixedWidth(50)
		self.yesButton.hide()

		self.vLayoutMaster.addWidget(self.pBar, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addSpacing(10)
		self.hLayout.addWidget(self.noButton)
		self.hLayout.addWidget(self.yesButton)
		self.vLayoutMaster.addLayout(self.hLayout)

		# Signals / slots
		self.noButton.clicked.connect(self.reject)
		self.yesButton.clicked.connect(self.accept)

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setWindowTitle('Downloading')
		self.setFixedSize(255, 150)
		self.show()

		# Init download
		self.run_thread(url, save_path, fname)

	def run_thread(self, url, save_path, fname):
		self.thrd = QtCore.QThread()
		self.worker = Worker(url, save_path, fname)
		self.worker.moveToThread(self.thrd)

		self.thrd.started.connect(self.worker.run)
		self.worker.finished.connect(self.thrd.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.worker.progress.connect(self.show_progress)
		self.thrd.finished.connect(self.thrd.deleteLater)
		self.thrd.start()

	def show_progress(self, label, n, total):
		self.pBar.setFormat(label)
		self.pBar.setMaximum(total)
		self.pBar.setValue(n)

		if n == 100:
			self.thrd.quit()
			self.noButton.show()
			self.yesButton.show()
			self.yesButton.setFocus()
			self.label.setText('Video has been downloaded. Would you like to\n'
							   'set the chosen file path as the "Local file" path?')

	"""def download_video(self):
		yt = pytube.YouTube(self.url, on_progress_callback=self.run_thread)
		stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
		stream.download(output_path=self.save_path, filename=self.fname)

		try:
			stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
			stream.download(output_path=self.save_path, filename=self.fname)

		except:
			err = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
										'There was an error downloading the video. Please report the<br>'
										'issue <a href="https://github.com/bsobotka/amv_tracker/issues">here</a>.')
			err.exec_()"""

