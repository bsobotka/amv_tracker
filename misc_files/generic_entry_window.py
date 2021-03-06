import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

from os import getcwd

from settings import settings_notifications


class GenericEntryWindow(QtWidgets.QDialog):
	def __init__(self, win_type, inp_1=None, inp_2=None, inp_3=None, dupe_check_list=None, max_item_length=30):
		super(GenericEntryWindow, self).__init__()

		self.win_type = win_type
		self.inp_1 = inp_1
		self.inp_2 = inp_2
		self.inp_3 = inp_3

		self.notif_label = QtWidgets.QLabel()

		self.textBox = QtWidgets.QLineEdit()
		self.textBox.setMaxLength(max_item_length)

		if dupe_check_list is not None:
			self.dupe_check_list = [tag.lower() for tag in dupe_check_list]
		else:
			self.dupe_check_list = []

		vLayoutMaster = QtWidgets.QVBoxLayout()
		hLayout = QtWidgets.QHBoxLayout()

		if win_type == 'rename':
			label_text = 'Rename {} <b>{}</b> to:'.format(inp_2, inp_3)
			win_text = 'Rename {}'.format(inp_1)
			self.textBox.setText(inp_3)
		elif win_type == 'new':
			label_text = 'New {} name:'.format(inp_1)
			win_text = label_text
		elif win_type == 'name_db':
			label_text = '<b>Folder:</b><br>' + inp_1 + '<p><b>File name:</b>'
			win_text = 'Name database'
		elif win_type == 'new_subdb':
			label_text = 'Name your new sub-database:'
			win_text = 'Name sub-database'
		elif win_type == 'new_cl':
			label_text = 'Name your new Custom List:'
			win_text = 'Name Custom List'
		else:
			label_text = 'Check the code, something went wrong'
			win_text = ''

		self.notif_label.setText(label_text)

		self.backButton = QtWidgets.QPushButton('Back')
		self.backButton.setFixedWidth(100)
		self.submitButton = QtWidgets.QPushButton('Submit')
		self.submitButton.setFixedWidth(100)
		self.submitButton.setDisabled(True)

		# Signals/slots
		self.backButton.clicked.connect(self.reject)
		self.submitButton.clicked.connect(self.check_for_error)
		self.textBox.textChanged.connect(self.check_text_exists)

		# Layout
		vLayoutMaster.addWidget(self.notif_label)
		vLayoutMaster.addWidget(self.textBox)
		hLayout.addWidget(self.backButton)
		hLayout.addWidget(self.submitButton)
		vLayoutMaster.addSpacing(20)
		vLayoutMaster.addLayout(hLayout)

		# Widget
		self.setLayout(vLayoutMaster)
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle(win_text)
		self.setFixedSize(self.sizeHint())
		self.show()

	def check_text_exists(self):
		if self.textBox.text() != '':
			self.submitButton.setEnabled(True)
			self.submitButton.setDefault(True)
		else:
			self.submitButton.setDisabled(True)

	def check_for_error(self):
		if self.win_type == 'new' and (',' in self.textBox.text() or ';' in self.textBox.text()):
			settings_notifications.SettingsNotificationWindow('chars')

		elif self.win_type == 'new' and self.textBox.text().lower() in self.dupe_check_list:
			settings_notifications.SettingsNotificationWindow('tag duplicate', inp_str1=self.textBox.text(),
			                                                  inp_str2='tag')
		elif self.win_type == 'new' and self.textBox.text().lower() == 'temp':
			settings_notifications.SettingsNotificationWindow('restricted')

		elif self.win_type == 'name_db' and (self.textBox.text().lower() + '.db') in self.dupe_check_list:
			settings_notifications.SettingsNotificationWindow('db duplicate', inp_str1=self.textBox.text())

		elif self.win_type == 'new_subdb' and self.textBox.text().lower() in self.dupe_check_list:
			settings_notifications.SettingsNotificationWindow('subdb duplicate', inp_str1=self.textBox.text())

		elif self.win_type == 'new_cl' and self.textBox.text().lower() in self.dupe_check_list:
			settings_notifications.SettingsNotificationWindow('cl duplicate', inp_str1=self.textBox.text())
		else:
			self.accept()


class GenericEntryWindowWithDrop(QtWidgets.QDialog):
	def __init__(self, win_type, drop_list, inp_str1=None, dupe_list=None, max_item_length=30):
		super(GenericEntryWindowWithDrop, self).__init__()

		self.win_type = win_type
		self.drop_list = drop_list
		self.inp_str1 = inp_str1
		if dupe_list:
			self.dupe_list = [x.casefold() for x in dupe_list]
		self.max_item_length = max_item_length

		# Initialize layouts and widgets
		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayoutBottom = QtWidgets.QHBoxLayout()
		self.hLayout1 = QtWidgets.QHBoxLayout()
		self.hLayout2 = QtWidgets.QHBoxLayout()

		self.label_1 = QtWidgets.QLabel()
		self.drop = QtWidgets.QComboBox()
		self.drop.setMaxVisibleItems(15)
		self.label_2 = QtWidgets.QLabel()

		self.textBox = QtWidgets.QLineEdit()
		self.textBox.setFixedWidth(150)
		self.textBox.setMaxLength(self.max_item_length)

		self.win_title = ''

		self.backButton = QtWidgets.QPushButton('Back')
		self.submitButton = QtWidgets.QPushButton('Submit')
		self.submitButton.setDisabled(True)

		# Conditionals
		if self.win_type == 'rename':
			self.label_1.setText('{} to rename:'.format(self.inp_str1))
			for item in self.drop_list:
				self.drop.addItem(item)
			self.label_2.setText('New name:')
			self.win_title = 'Rename {}'.format(self.inp_str1)

		else:
			self.label_1.setText('Check what went wrong dingus')
			self.textBox.setDisabled(True)
			self.submitButton.setDisabled(True)

		# Layout
		self.hLayout1.addWidget(self.label_1)
		self.hLayout1.addWidget(self.drop)
		self.hLayout2.addWidget(self.label_2)
		self.hLayout2.addWidget(self.textBox)

		self.hLayoutBottom.addWidget(self.backButton)
		self.hLayoutBottom.addWidget(self.submitButton)

		self.vLayoutMaster.addLayout(self.hLayout1)
		self.vLayoutMaster.addSpacing(15)
		self.vLayoutMaster.addLayout(self.hLayout2)
		self.vLayoutMaster.addSpacing(15)
		self.vLayoutMaster.addLayout(self.hLayoutBottom)

		# Signals / slots
		self.textBox.textChanged.connect(self.check_for_text)
		self.submitButton.clicked.connect(self.check_for_dupes)
		self.backButton.clicked.connect(self.reject)

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setFixedSize(self.sizeHint())
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle(self.win_title)
		self.show()

	def check_for_text(self):
		if self.textBox.text() == '':
			self.submitButton.setDisabled(True)
		else:
			self.submitButton.setEnabled(True)

	def check_for_dupes(self):
		if self.win_type == 'rename' and (self.textBox.text().casefold() in self.dupe_list or
		                                  self.textBox.text().casefold() == 'main database' or
										  self.textBox.text().casefold() == 'temp'):
			invalid_subdb_name = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Invalid name',
			                                           'A {} with this name already exists, or this\n'
			                                           'name is restricted. Please choose a different name.'
			                                           .format(self.inp_str1))
			invalid_subdb_name.exec_()
		else:
			self.accept()


class GenericDropWindow(QtWidgets.QDialog):
	def __init__(self, win_type, drop_list, label_2_text=None):
		super(GenericDropWindow, self).__init__()

		self.win_type = win_type
		self.drop_list = drop_list
		self.label_2_text = label_2_text

		# Initialize layouts and widgets
		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayoutBottom = QtWidgets.QHBoxLayout()

		self.label1 = QtWidgets.QLabel()
		self.label2 = QtWidgets.QLabel()
		self.drop = QtWidgets.QComboBox()
		self.drop.setMaxVisibleItems(15)
		for item in self.drop_list:
			self.drop.addItem(item)
		self.win_title = ''

		self.backButton = QtWidgets.QPushButton('Back')
		self.submitButton = QtWidgets.QPushButton()

		# Conditionals
		if self.win_type == 'restore backup':
			self.label1.setText('PLEASE NOTE: Restoring a backup will overwrite <u>all</u> data<br>'
			                    'in the current working database with whatever is in the<br>'
			                    'backup. It is <u>strongly recommended</u> that you create a<br>'
			                    'current backup before reverting to an older one.<p>'
			                    'Please select the backup to restore:')
			self.label2.setText('Current database: {}'.format(self.label_2_text))
			self.drop.setFixedWidth(250)
			self.submitButton.setText('Restore')
			self.win_title = 'Restore backup'

		else:
			self.label1.setText('Ya done screwed up bro, check the code.')

		# Layout
		if self.label_2_text:
			self.vLayoutMaster.addWidget(self.label2)
			self.vLayoutMaster.addSpacing(15)
		self.vLayoutMaster.addWidget(self.label1)
		self.vLayoutMaster.addWidget(self.drop)
		self.vLayoutMaster.addSpacing(20)

		self.hLayoutBottom.addWidget(self.backButton)
		self.hLayoutBottom.addWidget(self.submitButton)
		self.vLayoutMaster.addLayout(self.hLayoutBottom)

		# Signals / slots
		self.backButton.clicked.connect(self.reject)
		self.submitButton.clicked.connect(self.accept)

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setFixedSize(self.sizeHint())
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle(self.win_title)
		self.show()
