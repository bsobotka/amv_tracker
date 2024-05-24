import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import sqlite3

from os import getcwd
from misc_files import common_vars


class CLEditWindow(QtWidgets.QDialog):
	def __init__(self):
		super(CLEditWindow, self).__init__()

		# Widgets
		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayout1 = QtWidgets.QHBoxLayout()
		self.hLayout1.setAlignment(QtCore.Qt.AlignLeft)
		self.hLayout2 = QtWidgets.QHBoxLayout()
		self.hLayout2.setAlignment(QtCore.Qt.AlignLeft)
		self.hLayout3 = QtWidgets.QHBoxLayout()
		self.hLayout3.setAlignment(QtCore.Qt.AlignLeft)

		self.listNameLabel = QtWidgets.QLabel()
		self.listNameLabel.setText('Custom list to edit:')

		self.listDrop = QtWidgets.QComboBox()
		self.get_cl_names()

		self.newNameLabel = QtWidgets.QLabel()
		self.newNameLabel.setText('List name:')

		self.newNameTextBox = QtWidgets.QLineEdit()
		self.newNameTextBox.setFixedWidth(180)
		self.newNameTextBox.setMaxLength(30)
		self.newNameTextBox.setText(self.listDrop.currentText())
		self.populate_new_name_field()

		self.descrLabel = QtWidgets.QLabel()
		self.descrLabel.setText('Custom List description/comments:')

		self.descrTextEdit = QtWidgets.QTextEdit()
		self.descrTextEdit.setFixedSize(300, 300)
		self.populate_descr_field()

		self.closeButton = QtWidgets.QPushButton('Close')
		self.closeButton.setFixedWidth(150)
		self.submitButton = QtWidgets.QPushButton('Submit')
		self.submitButton.setFixedWidth(150)

		# Layouts
		self.hLayout1.addWidget(self.listNameLabel)
		self.hLayout1.addWidget(self.listDrop)
		self.vLayoutMaster.addLayout(self.hLayout1)

		self.vLayoutMaster.addSpacing(20)

		self.hLayout2.addWidget(self.newNameLabel)
		self.hLayout2.addWidget(self.newNameTextBox)
		self.hLayout2.addSpacing(70)
		self.vLayoutMaster.addLayout(self.hLayout2)

		self.vLayoutMaster.addSpacing(5)

		self.vLayoutMaster.addWidget(self.descrLabel)
		self.vLayoutMaster.addWidget(self.descrTextEdit)

		self.hLayout3.addWidget(self.closeButton)
		self.hLayout3.addWidget(self.submitButton)
		self.vLayoutMaster.addLayout(self.hLayout3)

		# Signals / slots
		self.listDrop.currentIndexChanged.connect(self.populate_new_name_field)
		self.listDrop.currentIndexChanged.connect(self.populate_descr_field)
		self.newNameTextBox.textChanged.connect(self.enable_disable_submit_btn)
		self.closeButton.clicked.connect(self.close)
		self.submitButton.clicked.connect(self.submit_btn_pressed)

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setFixedSize(self.sizeHint())
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Edit Custom List Name/Descr')
		self.show()

	def get_cl_names(self):
		self.listDrop.clear()
		cl_name_list = [k for k, v in common_vars.custom_list_lookup().items()]
		cl_name_list.sort(key=lambda x: x.casefold())
		for name in cl_name_list:
			self.listDrop.addItem(name)

	def populate_new_name_field(self):
		self.newNameTextBox.setText(self.listDrop.currentText())

	def populate_descr_field(self):
		self.descrTextEdit.clear()
		list_name = self.listDrop.currentText()

		pdf_conn = sqlite3.connect(common_vars.video_db())
		pdf_cursor = pdf_conn.cursor()
		cl_id_dict = common_vars.custom_list_lookup()

		if self.listDrop.count() > 0:
			pdf_cursor.execute('SELECT cl_desc FROM custom_lists WHERE cl_id = ?', (cl_id_dict[list_name],))
			cl_desc = pdf_cursor.fetchone()[0]

			if cl_desc:
				self.descrTextEdit.setText(cl_desc)

		pdf_conn.close()

	def enable_disable_submit_btn(self):
		if self.newNameTextBox.text() == '':
			self.submitButton.setDisabled(True)
			self.submitButton.setToolTip('Please ensure the "List name"\nfield is populated.')
		else:
			self.submitButton.setEnabled(True)
			self.submitButton.setToolTip('')

	def submit_btn_pressed(self):
		sbp_conn = sqlite3.connect(common_vars.video_db())
		sbp_cursor = sbp_conn.cursor()

		cl_dict = common_vars.custom_list_lookup()
		list_of_cl_names = [k.casefold() for k, v in cl_dict.items()]

		curr_drop_ind = self.listDrop.currentIndex()
		curr_cl_id = cl_dict[self.listDrop.currentText()]
		new_list_name = self.newNameTextBox.text()
		descr = self.descrTextEdit.toPlainText()

		# Ensure that Custom List name does not match that of another Custom List
		if new_list_name.casefold() in list_of_cl_names and new_list_name.casefold() != \
				self.listDrop.currentText().casefold():
			same_name_error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
															 'This list name is already in use. Please name this list\n'
															 'something else.')
			same_name_error.exec_()

		else:
			sbp_cursor.execute('UPDATE custom_lists SET list_name = ?, cl_desc = ? WHERE cl_id = ?', (new_list_name,
																									  descr,
																									  curr_cl_id))
			sbp_conn.commit()
			self.get_cl_names()
			self.listDrop.setCurrentIndex(curr_drop_ind)
			update_success = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Success',
												   'Custom list has been updated.')
			update_success.exec_()

		sbp_conn.close()

