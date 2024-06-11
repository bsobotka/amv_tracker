import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

from os import getcwd
from settings import settings_notifications


class NewCustomListWindow(QtWidgets.QDialog):
	def __init__(self, existing_cls):
		super(NewCustomListWindow, self).__init__()

		self.existing_cls = existing_cls

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayout1 = QtWidgets.QHBoxLayout()
		self.hLayout2 = QtWidgets.QHBoxLayout()

		self.clNameLabel = QtWidgets.QLabel()
		self.clNameLabel.setText('New Custom List Name:')
		self.clNameText = QtWidgets.QLineEdit()
		self.clNameText.setFixedWidth(160)

		self.clDescLabel = QtWidgets.QLabel()
		self.clDescLabel.setText('Custom List Description:')
		self.clDescText = QtWidgets.QTextEdit()
		self.clDescText.setFixedSize(278, 200)

		self.backButton = QtWidgets.QPushButton('Back')
		self.backButton.setFixedWidth(125)
		self.submitButton = QtWidgets.QPushButton('Submit')
		self.submitButton.setFixedWidth(125)
		self.submitButton.setDisabled(True)

		# Layout
		self.hLayout1.addWidget(self.clNameLabel)
		self.hLayout1.addWidget(self.clNameText)
		self.vLayoutMaster.addLayout(self.hLayout1)
		self.vLayoutMaster.addSpacing(10)

		self.vLayoutMaster.addWidget(self.clDescLabel, alignment=QtCore.Qt.AlignLeft)
		self.vLayoutMaster.addWidget(self.clDescText, alignment=QtCore.Qt.AlignLeft)
		self.vLayoutMaster.addSpacing(20)

		self.hLayout2.addWidget(self.backButton)
		self.hLayout2.addWidget(self.submitButton)
		self.vLayoutMaster.addLayout(self.hLayout2)

		# Signals / slots
		self.clNameText.textChanged.connect(self.check_name_exists)
		self.backButton.clicked.connect(self.reject)
		self.submitButton.clicked.connect(self.submit_clicked)

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setFixedSize(self.sizeHint())
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('New Custom List')
		self.show()

	def check_name_exists(self):
		if self.clNameText.text() != '':
			self.submitButton.setEnabled(True)
		else:
			self.submitButton.setDisabled(True)

	def submit_clicked(self):
		if self.clNameText.text().lower() in self.existing_cls:
			settings_notifications.SettingsNotificationWindow('cl duplicate', inp_str1=self.clNameText.text())
		else:
			self.accept()

