import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import subprocess
import time

from os import getcwd
from random import uniform


class Worker(QtCore.QObject):
	finished = QtCore.pyqtSignal()
	progress = QtCore.pyqtSignal(str, int, int)

	def __init__(self, vidid_worker, fpath_worker):
		super(Worker, self).__init__()
		self.vidid_worker = vidid_worker
		self.fpath_worker = fpath_worker

	def run(self):
		thumb_ctr = 0

		for t_ind in range(1, 6):
			rand_num = round(uniform(0.02, 0.19), 2)
			temp_img_path = getcwd() + '\\thumbnails\\temp\\' + self.vidid_worker + '-{}.jpg'.format(str(t_ind))
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			startupinfo.wShowWindow = subprocess.SW_HIDE
			vid_length = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
										 'default=noprint_wrappers=1:nokey=1', self.fpath_worker], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
											  stderr=subprocess.DEVNULL, startupinfo=startupinfo).stdout)
			# vid_length = 120.0
			timecode = time.strftime('%H:%M:%S', time.gmtime(vid_length * ((t_ind * (1/5)) - rand_num)))
			subprocess.call(['ffmpeg', '-y', '-i', self.fpath_worker, '-ss', timecode, '-vframes', '1', temp_img_path],
							stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
							startupinfo=startupinfo)

			thumb_ctr += 1
			prog_bar_label = '{} of 5 thumbnails generated'.format(thumb_ctr)
			self.progress.emit(prog_bar_label, thumb_ctr, 5)

		self.progress.emit('Done!', 1, 2)


class ThumbnailDialog(QtWidgets.QDialog):
	def __init__(self, vid_fpath, vidid):
		super(ThumbnailDialog, self).__init__()

		self.filePath = vid_fpath
		self.vidid = vidid

		self.hLayout = QtWidgets.QHBoxLayout()
		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.vLayoutMaster.setAlignment(QtCore.Qt.AlignCenter)
		
		self.headerFont = QtGui.QFont()
		self.headerFont.setBold(True)
		self.headerFont.setPixelSize(16)
		
		self.headerLabel = QtWidgets.QLabel()
		self.headerLabel.setText('Please select the thumbnail to use:\n')
		self.headerLabel.setFont(self.headerFont)

		self.thumb = QtWidgets.QLabel()
		self.thumb.setFixedSize(512, 288)

		self.slider = QtWidgets.QSlider()
		self.slider.setDisabled(True)
		self.slider.setFixedWidth(500)
		self.slider.setOrientation(QtCore.Qt.Horizontal)
		self.slider.setMinimum(1)
		self.slider.setMaximum(5)
		self.slider.setTickInterval(1)

		self.regenThumbsButton = QtWidgets.QPushButton('Generate new thumbnails')
		self.regenThumbsButton.setFixedWidth(170)
		self.regenThumbsButton.setToolTip('Click to get a new set of thumbnails if you don\'t like\n'
										  'the ones provided.')

		self.backButton = QtWidgets.QPushButton('Back')
		self.backButton.setFixedWidth(125)

		self.submitButton = QtWidgets.QPushButton('Select')
		self.submitButton.setFixedWidth(125)

		# Progress bar
		self.pBar = QtWidgets.QProgressBar()
		self.pBar.setInvertedAppearance(False)
		self.pBar.setTextVisible(True)
		self.pBar.setFixedWidth(300)
		self.pBar.setAlignment(QtCore.Qt.AlignCenter)

		self.vLayoutMaster.addWidget(self.headerLabel, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addWidget(self.thumb, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addWidget(self.slider, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addWidget(self.pBar, alignment=QtCore.Qt.AlignCenter)
		self.hLayout.addWidget(self.regenThumbsButton, alignment=QtCore.Qt.AlignLeft)
		self.hLayout.addSpacing(50)
		self.hLayout.addWidget(self.backButton, alignment=QtCore.Qt.AlignRight)
		self.hLayout.addWidget(self.submitButton, alignment=QtCore.Qt.AlignRight)
		self.vLayoutMaster.addSpacing(20)
		self.vLayoutMaster.addLayout(self.hLayout)

		self.generate_thumbs()

		# Signals / slots
		self.slider.sliderMoved.connect(lambda: self.change_image(self.slider.sliderPosition()))
		self.regenThumbsButton.clicked.connect(self.generate_thumbs)
		self.backButton.clicked.connect(self.reject)
		self.submitButton.clicked.connect(self.accept)

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setWindowTitle('Select thumbnail')
		self.setFixedSize(540, 500)

	def generate_thumbs(self):
		self.slider.setDisabled(True)
		self.regenThumbsButton.setDisabled(True)
		self.backButton.setDisabled(True)
		self.submitButton.setDisabled(True)

		self.thrd = QtCore.QThread()
		self.worker = Worker(self.vidid, self.filePath)
		self.worker.moveToThread(self.thrd)

		self.pBar.show()

		self.thrd.start()
		self.thrd.started.connect(self.worker.run)
		self.worker.finished.connect(self.thrd.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.worker.progress.connect(self.show_pbar_progress)
		self.thrd.finished.connect(self.thrd.deleteLater)
		self.thrd.finished.connect(self.pBar.close)

	def show_pbar_progress(self, label, n, total):
		self.pBar.setFormat(label)

		if label == 'Done!':
			self.thrd.quit()

			self.slider.setSliderPosition(0)
			self.slider.setEnabled(True)
			self.regenThumbsButton.setEnabled(True)
			self.backButton.setEnabled(True)
			self.submitButton.setEnabled(True)

			self.change_image(1)

		self.pBar.setMaximum(total)
		self.pBar.setValue(n)

	def change_image(self, ind):
		self.thumbPixmap = QtGui.QPixmap(getcwd() + '\\thumbnails\\temp\\{}-{}.jpg'.format(self.vidid, ind))
		self.thumb.setPixmap(self.thumbPixmap.scaled(self.thumb.size(), QtCore.Qt.KeepAspectRatio))

