import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

from os import getcwd


class ErrorLoggingWindow(QtWidgets.QDialog):
	def __init__(self, traceback_text):
		super(ErrorLoggingWindow, self).__init__()
		self.tracebackText = traceback_text

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayout = QtWidgets.QHBoxLayout()
		self.hLayout.setAlignment(QtCore.Qt.AlignRight)

		self.headerLabel = QtWidgets.QLabel()
		self.headerLabel.setText('An error has occurred. Please raise an issue '
								 '<a href="https://github.com/bsobotka/amv_tracker/issues">here</a> and provide a copy '
								 'of your  errors.log file,<br>found in the AMV Tracker directory.')

		self.boldFont = QtGui.QFont()
		self.boldFont.setBold(True)

		self.tracebackLabel = QtWidgets.QLabel()
		self.tracebackLabel.setText('Error traceback:')
		self.tracebackLabel.setFont(self.boldFont)

		self.tracebackTextEdit = QtWidgets.QTextEdit()
		self.tracebackTextEdit.setFixedSize(450, 150)
		self.tracebackTextEdit.setText(self.tracebackText)

		self.okButton = QtWidgets.QPushButton('OK')
		self.okButton.setFixedWidth(100)

		# Layout
		self.vLayoutMaster.addWidget(self.headerLabel)
		self.vLayoutMaster.addSpacing(20)
		self.vLayoutMaster.addWidget(self.tracebackLabel)
		self.vLayoutMaster.addWidget(self.tracebackTextEdit)
		self.hLayout.addWidget(self.okButton)
		self.vLayoutMaster.addLayout(self.hLayout)

		# Signals / slots
		self.okButton.clicked.connect(self.accept)

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setFixedSize(self.sizeHint())
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Error')
		self.show()
