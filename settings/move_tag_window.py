import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import sqlite3

from os import getcwd

from misc_files import common_vars


class MoveTagWindow(QtWidgets.QDialog):
	def __init__(self, tag_name, origin_table, table_list):
		super(MoveTagWindow, self).__init__()

		self.tag_db_conn = sqlite3.connect(common_vars.tag_db())
		self.tag_name = tag_name
		self.origin_table = origin_table
		self.table_list = table_list

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.vLayoutMaster.setAlignment(QtCore.Qt.AlignCenter)
		self.hLayout = QtWidgets.QHBoxLayout()

		self.labelText = QtWidgets.QLabel()
		self.labelText.setText(
			'Move <b>{}</b> tag<br><br>from<br><br><b>{}</b> tag group<br><br>to:<br><br>'.format(self.tag_name,
																								  self.origin_table))
		self.labelText.setAlignment(QtCore.Qt.AlignCenter)

		self.cantMoveLabel = QtWidgets.QLabel()
		self.cantMoveLabel.setText('<font color="red">This tag already exists in the chosen<br>'
								   'tag group. Please choose a different<br>group.</font>')
		self.cantMoveLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.cantMoveLabel.hide()

		self.tempSpacer = QtWidgets.QLabel()

		self.tableDropdown = QtWidgets.QComboBox()
		for table in self.table_list:
			self.tableDropdown.addItem(table)

		self.backButton = QtWidgets.QPushButton('Back')
		self.backButton.setFixedWidth(100)
		self.submitButton = QtWidgets.QPushButton('Move tag')
		self.submitButton.setFixedWidth(100)

		# Slots/signals
		self.tableDropdown.currentIndexChanged.connect(self.tag_check)
		self.backButton.clicked.connect(self.reject)
		self.submitButton.clicked.connect(self.accept)

		# Layouts
		self.vLayoutMaster.addWidget(self.labelText, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addWidget(self.tableDropdown, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addSpacing(10)
		self.vLayoutMaster.addWidget(self.tempSpacer)
		self.vLayoutMaster.addWidget(self.cantMoveLabel)
		self.hLayout.addWidget(self.backButton)
		self.hLayout.addWidget(self.submitButton)
		self.vLayoutMaster.addLayout(self.hLayout)

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Move tag')
		self.setFixedSize(self.sizeHint() + QtCore.QSize(20, 0))
		self.show()

	def tag_check(self):
		int_list_name = common_vars.tag_table_lookup()[self.tableDropdown.currentText()]
		dest_tag_list = [tag[0].lower() for tag in
						 self.tag_db_conn.execute('SELECT tag_name FROM {}'.format(int_list_name))]

		if self.tag_name.lower() in dest_tag_list:
			self.submitButton.setDisabled(True)
			self.cantMoveLabel.show()
			self.tempSpacer.hide()
		else:
			self.submitButton.setEnabled(True)
			self.cantMoveLabel.hide()
			self.tempSpacer.show()
