import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

from os import getcwd


class FailedFetchesWin(QtWidgets.QDialog):
	def __init__(self, inp_list):
		super(FailedFetchesWin, self).__init__()
		self.listText = ''
		for item in inp_list:
			self.listText += '{}\n'.format(item)

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayout = QtWidgets.QHBoxLayout()
		self.hLayout.setAlignment(QtCore.Qt.AlignRight)

		self.label = QtWidgets.QLabel()
		self.label.setText('Due to YouTube occasionally rate-limiting IP addresses that make too\n'
						   'many consecutive API calls, AMV Tracker was not able to download all\n'
						   'the videos from the provided YouTube channel or playlist. The following\n'
						   'videos were NOT imported.\n\n'
						   'You can click Retry to have AMV Tracker attempt to import the videos\n'
						   'below which failed to import. Please note that this may result in another\n'
						   'rate-limit error. Alternatively, you can copy/paste the below list into\n'
						   'e.g. Notepad, and then manually add them to AMV Tracker (and you can use\n'
						   'the fetch function on the entry screen to quickly grab the data using the\n'
						   'provided video URLs).')

		self.listBox = QtWidgets.QTextEdit()
		self.listBox.setFixedSize(350, 250)
		self.listBox.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
		self.listBox.setText(self.listText)

		self.retryButton = QtWidgets.QPushButton('Retry')
		self.retryButton.setFixedWidth(75)
		self.okButton = QtWidgets.QPushButton('OK')
		self.okButton.setFixedWidth(75)

		# Layout
		self.vLayoutMaster.addWidget(self.label)
		self.vLayoutMaster.addSpacing(10)
		self.vLayoutMaster.addWidget(self.listBox)
		self.vLayoutMaster.addSpacing(10)
		self.hLayout.addWidget(self.retryButton)
		self.hLayout.addWidget(self.okButton)
		self.vLayoutMaster.addLayout(self.hLayout)

		# Signals / slots
		self.okButton.clicked.connect(self.reject)
		self.retryButton.clicked.connect(self.accept)

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setFixedSize(self.sizeHint())
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Failed to import')
		self.show()

