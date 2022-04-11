import PyQt5.QtWidgets as QtWidgets


class SettingsNotificationWindow(QtWidgets.QWidget):
	def __init__(self, msg_type, inp_str1=None, inp_str2=None):
		super(SettingsNotificationWindow, self).__init__()

		self.msgBox = QtWidgets.QMessageBox()
		if msg_type == 'desc updated':
			self.msgBox.information(self, 'Description updated', 'The description for the [{}] tag\nhas been updated.'.format(inp_str1))

		elif msg_type == 'tag duplicate':
			self.msgBox.warning(self, 'Duplicate', '[{}] {} already exists, please choose\na different {} name.'.format(
				inp_str1.capitalize(), inp_str2.lower(), inp_str2.lower()))

		elif msg_type == 'db duplicate':
			self.msgBox.warning(self, 'File exists', 'There is already a file in this directory named {}. Please\n'
			                                         'choose a different file name.'.format(inp_str1))

		elif msg_type == 'restricted':
			self.msgBox.warning(self, 'Restricted name', 'This name is unable to be used as a database name. Please\n'
														 'choose a different file name.')

		elif msg_type == 'subdb duplicate':
			self.msgBox.warning(self, 'Sub-database already exists', 'A sub-database by this name already exists. Please\n'
			                                                         'choose a different sub-db name.')

		elif msg_type == 'cl duplicate':
			self.msgBox.warning(self, 'Custom List already exists', 'There is already a Custom List with this name. '
			                                                        'Please choose\na different name.')

		elif msg_type == 'chars':
			self.msgBox.warning(self, 'Error', 'The following characters are not permitted when\nnaming your tags:\n\n'
			                                   ',   ;\n\nPlease choose a different tag name.')
