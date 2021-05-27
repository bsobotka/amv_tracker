import PyQt5.QtWidgets as QtWidgets

from settings import settings_notifications


class GenericEntryWindow(QtWidgets.QDialog):
	def __init__(self, win_type, item_type=None, item_parent=None, item_name=None,
	             dupe_check_list=None, max_item_length=30):
		super(GenericEntryWindow, self).__init__()

		self.win_type = win_type

		vLayoutMaster = QtWidgets.QVBoxLayout()
		hLayout = QtWidgets.QHBoxLayout()

		if dupe_check_list is not None:
			self.dupe_check_list = [tag.lower() for tag in dupe_check_list]
		else:
			self.dupe_check_list = []

		if win_type == 'rename':
			label_text = 'Rename {} [{}] to:'.format(item_parent, item_name)
			win_text = 'Rename {}'.format(item_type)
		elif win_type == 'new':
			label_text = 'New {} name:'.format(item_type)
			win_text = label_text
		elif win_type == 'name_db':
			label_text = '<b>Folder:</b><br>' + item_type + '<p><b>File name:</b>'
			win_text = 'Name database'
		else:
			label_text = 'Check the code, something went wrong'
			win_text = ''

		self.notif_label = QtWidgets.QLabel()
		self.notif_label.setText(label_text)

		self.textBox = QtWidgets.QLineEdit()
		self.textBox.setMaxLength(max_item_length)

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

		elif self.textBox.text().lower() in self.dupe_check_list:
			settings_notifications.SettingsNotificationWindow('tag duplicate', inp_str1=self.textBox.text(),
			                                                  inp_str2='tag')
		else:
			self.accept()
