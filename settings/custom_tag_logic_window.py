import sqlite3

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

from main_window.filter_win import ChooseFilterWindow
from misc_files import common_vars, tag_checkboxes


class TagLogicWindow(ChooseFilterWindow):
	def __init__(self):
		super(TagLogicWindow, self).__init__()
		grid_v_ind = 0
		tag_logic_conn = sqlite3.connect(common_vars.video_db())

		self.tag_list_names = [tags[1] for tags in tag_logic_conn.execute('SELECT * FROM tags_lookup')]
		self.hLayoutBottom.setAlignment(QtCore.Qt.AlignRight)

		self.chooseFieldLabel.setText('If this field:')
		self.booleanLabel.setText('...is...')
		self.existsLabel.setText('...is...')

		self.checkTheseTagsLabel = QtWidgets.QLabel()
		self.checkTheseTagsLabel.setText('...then check the following tag(s):')

		self.gridLayout2.addWidget(self.checkTheseTagsLabel, grid_v_ind, 0, 1, 3)
		grid_v_ind += 1

		self.okButton.setText('Save')
		self.okButton.setDisabled(True)

		# Tags 1
		self.tags1Button = QtWidgets.QPushButton(self.tag_list_names[0])

		self.tags1Box = QtWidgets.QLineEdit()
		self.tags1Box.setPlaceholderText('<-- Click to select tags')
		self.tags1Box.setFixedWidth(390)
		self.tags1Box.setReadOnly(True)
		self.tags1X = QtWidgets.QPushButton('X')
		self.tags1X.setFixedWidth(20)
		self.tags1X.setToolTip('Clear tags')

		self.gridLayout2.addWidget(self.tags1Button, grid_v_ind, 0, 1, 2)
		self.gridLayout2.addWidget(self.tags1Box, grid_v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout2.addWidget(self.tags1X, grid_v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		grid_v_ind += 1

		# Tags 2
		self.tags2Button = QtWidgets.QPushButton(self.tag_list_names[1])
		self.tags2Box = QtWidgets.QLineEdit()
		self.tags2Box.setPlaceholderText('<-- Click to select tags')
		self.tags2Box.setFixedWidth(390)
		self.tags2Box.setReadOnly(True)
		self.tags2X = QtWidgets.QPushButton('X')
		self.tags2X.setFixedWidth(20)
		self.tags2X.setToolTip('Clear tags')

		self.gridLayout2.addWidget(self.tags2Button, grid_v_ind, 0, 1, 2)
		self.gridLayout2.addWidget(self.tags2Box, grid_v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout2.addWidget(self.tags2X, grid_v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		grid_v_ind += 1

		# Tags 3
		self.tags3Button = QtWidgets.QPushButton(self.tag_list_names[2])
		self.tags3Box = QtWidgets.QLineEdit()
		self.tags3Box.setPlaceholderText('<-- Click to select tags')
		self.tags3Box.setFixedWidth(390)
		self.tags3Box.setReadOnly(True)
		self.tags3X = QtWidgets.QPushButton('X')
		self.tags3X.setFixedWidth(20)
		self.tags3X.setToolTip('Clear tags')

		self.gridLayout2.addWidget(self.tags3Button, grid_v_ind, 0, 1, 2)
		self.gridLayout2.addWidget(self.tags3Box, grid_v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout2.addWidget(self.tags3X, grid_v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		grid_v_ind += 1

		# Tags 4
		self.tags4Button = QtWidgets.QPushButton(self.tag_list_names[3])
		self.tags4Box = QtWidgets.QLineEdit()
		self.tags4Box.setPlaceholderText('<-- Click to select tags')
		self.tags4Box.setFixedWidth(390)
		self.tags4Box.setReadOnly(True)
		self.tags4X = QtWidgets.QPushButton('X')
		self.tags4X.setFixedWidth(20)
		self.tags4X.setToolTip('Clear tags')

		self.gridLayout2.addWidget(self.tags4Button, grid_v_ind, 0, 1, 2)
		self.gridLayout2.addWidget(self.tags4Box, grid_v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout2.addWidget(self.tags4X, grid_v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		grid_v_ind += 1

		# Tags 5
		self.tags5Button = QtWidgets.QPushButton(self.tag_list_names[4])
		self.tags5Box = QtWidgets.QLineEdit()
		self.tags5Box.setPlaceholderText('<-- Click to select tags')
		self.tags5Box.setFixedWidth(390)
		self.tags5Box.setReadOnly(True)
		self.tags5X = QtWidgets.QPushButton('X')
		self.tags5X.setFixedWidth(20)
		self.tags5X.setToolTip('Clear tags')

		self.gridLayout2.addWidget(self.tags5Button, grid_v_ind, 0, 1, 2)
		self.gridLayout2.addWidget(self.tags5Box, grid_v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout2.addWidget(self.tags5X, grid_v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		grid_v_ind += 1

		# Tags 6
		self.tags6Button = QtWidgets.QPushButton(self.tag_list_names[5])
		self.tags6Box = QtWidgets.QLineEdit()
		self.tags6Box.setPlaceholderText('<-- Click to select tags')
		self.tags6Box.setFixedWidth(390)
		self.tags6Box.setReadOnly(True)
		self.tags6X = QtWidgets.QPushButton('X')
		self.tags6X.setFixedWidth(20)
		self.tags6X.setToolTip('Clear tags')

		self.gridLayout2.addWidget(self.tags6Button, grid_v_ind, 0, 1, 2)
		self.gridLayout2.addWidget(self.tags6Box, grid_v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout2.addWidget(self.tags6X, grid_v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		grid_v_ind += 1

		# Signals / slots
		self.tags1Button.clicked.connect(lambda: self.tag_button_clicked(self.tags1Box, self.tags1Button.text(), self.tags1Box.text()))
		self.tags2Button.clicked.connect(lambda: self.tag_button_clicked(self.tags2Box, self.tags2Button.text(), self.tags2Box.text()))
		self.tags3Button.clicked.connect(lambda: self.tag_button_clicked(self.tags3Box, self.tags3Button.text(), self.tags3Box.text()))
		self.tags4Button.clicked.connect(lambda: self.tag_button_clicked(self.tags4Box, self.tags4Button.text(), self.tags4Box.text()))
		self.tags5Button.clicked.connect(lambda: self.tag_button_clicked(self.tags5Box, self.tags5Button.text(), self.tags5Box.text()))
		self.tags6Button.clicked.connect(lambda: self.tag_button_clicked(self.tags6Box, self.tags6Button.text(), self.tags6Box.text()))

		self.tags1Box.textChanged.connect(self.en_dis_save_button)
		self.tags2Box.textChanged.connect(self.en_dis_save_button)
		self.tags3Box.textChanged.connect(self.en_dis_save_button)
		self.tags4Box.textChanged.connect(self.en_dis_save_button)
		self.tags5Box.textChanged.connect(self.en_dis_save_button)
		self.tags6Box.textChanged.connect(self.en_dis_save_button)

		self.tags1X.clicked.connect(self.tags1Box.clear)
		self.tags2X.clicked.connect(self.tags2Box.clear)
		self.tags3X.clicked.connect(self.tags3Box.clear)
		self.tags4X.clicked.connect(self.tags4Box.clear)
		self.tags5X.clicked.connect(self.tags5Box.clear)
		self.tags6X.clicked.connect(self.tags6Box.clear)

		self.okButton.clicked.connect(self.save_rule)

		self.setFixedSize(550, 400)

	def en_dis_save_button(self):
		if self.tags1Box.text() != '' or self.tags2Box.text() != '' or self.tags3Box.text() != '' or \
			self.tags4Box.text() != '' or self.tags5Box.text() != '' or self.tags6Box.text() != '':
			self.okButton.setEnabled(True)
		else:
			self.okButton.setDisabled(True)

	def tag_button_clicked(self, tag_box, tag_group, checked_tags):
		tag_win = tag_checkboxes.TagWindow(tag_group, checked_tags=checked_tags)
		if tag_win.exec_():
			tag_box.setText(tag_win.out_str[:-2])

	def save_rule(self):
		save_rule_conn = sqlite3.connect(common_vars.video_db())
		save_rule_cursor = save_rule_conn.cursor()

		rule_id = common_vars.id_generator('CTLR')
		if self.fieldNameDropdown.currentText() == 'Video length (sec)':
			field_int = common_vars.video_field_lookup()['Video length (min/sec)']
		else:
			field_int = common_vars.video_field_lookup()[self.fieldNameDropdown.currentText()]

		# Get operation
		operation = self.op.strip()
		value = self.value.strip()
		tags_1 = self.tags1Box.text()
		tags_2 = self.tags2Box.text()
		tags_3 = self.tags3Box.text()
		tags_4 = self.tags4Box.text()
		tags_5 = self.tags5Box.text()
		tags_6 = self.tags6Box.text()

		insert_tup = (rule_id, field_int, operation, value, tags_1, tags_2, tags_3, tags_4, tags_5, tags_6)
		save_rule_cursor.execute('INSERT OR IGNORE INTO custom_tag_logic VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', insert_tup)
		save_rule_conn.commit()

		rule_saved_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Rule saved', 'Rule has been saved.')
		rule_saved_win.exec_()

		save_rule_conn.close()
