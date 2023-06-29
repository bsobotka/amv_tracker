import pytube

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore


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

