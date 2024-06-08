import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

from os import getcwd

from misc_files import generate_thumb


class Worker(QtCore.QObject):
	# TODO: Check on eliminating redundant ffprobe subprocess call to get video length
	finished = QtCore.pyqtSignal()
	progress = QtCore.pyqtSignal(str, int, int)

	def __init__(self, vidid_worker, fpath_worker):
		super(Worker, self).__init__()
		self.vidid_worker = vidid_worker
		self.fpath_worker = fpath_worker

	def run(self):
		thumb_ctr = 0

		for t_ind in range(1, 6):
			temp_img_path = getcwd() + '\\thumbnails\\temp\\' + self.vidid_worker + '-{}.jpg'.format(str(t_ind))
			generate_thumb.thumb_generator(self.fpath_worker, t_ind, temp_img_path)

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

