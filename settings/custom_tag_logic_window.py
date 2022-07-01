import sqlite3

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

from os import getcwd

from main_window.filter_win import ChooseFilterWindow
from misc_files import common_vars, tag_checkboxes


"""class RuleDeleted(QtWidgets.QDialog):
	ok_pushed = QtCore.pyqtSignal()

	def __init__(self):
		super(RuleDeleted, self).__init__()"""


class TagLogicMgmt(QtWidgets.QMainWindow):
	def __init__(self):
		super(TagLogicMgmt, self).__init__()
		self.init_window()

	def init_window(self):
		tag_log_win_conn = sqlite3.connect(common_vars.video_db())
		tag_log_win_cursor = tag_log_win_conn.cursor()

		self.fieldLookup = common_vars.video_field_lookup(reverse=False, filt='in_use', filt_val=1)

		tag_log_win_cursor.execute('SELECT * FROM custom_tag_logic')
		self.tagRules = tag_log_win_cursor.fetchall()
		self.tagRules.sort(key=lambda x: self.fieldLookup[x[1]])
		self.rulesToDeleteList = []

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayoutHeader = QtWidgets.QHBoxLayout()
		self.hLayoutHeader.setAlignment(QtCore.Qt.AlignLeft)
		self.gridLayout = QtWidgets.QGridLayout()
		self.hLayoutBottom = QtWidgets.QHBoxLayout()
		self.scrollWidget = QtWidgets.QWidget()
		self.scrollArea = QtWidgets.QScrollArea()

		# Header
		self.headerFont = QtGui.QFont()
		self.headerFont.setBold(True)
		self.headerFont.setUnderline(True)

		self.editLabel = QtWidgets.QLabel()
		self.editLabel.setText('Edit')
		self.editLabel.setFixedWidth(30)
		self.editLabel.setFont(self.headerFont)

		self.deleteLabel = QtWidgets.QLabel()
		self.deleteLabel.setText('Delete')
		self.deleteLabel.setFixedWidth(200)
		self.deleteLabel.setFont(self.headerFont)

		self.ruleLabel = QtWidgets.QLabel()
		self.ruleLabel.setText('Rule')
		self.ruleLabel.setFixedWidth(400)
		self.ruleLabel.setFont(self.headerFont)

		self.enableLabel = QtWidgets.QLabel()
		self.enableLabel.setText('Enabled')
		self.enableLabel.setFixedWidth(60)
		self.enableLabel.setFont(self.headerFont)

		self.hLayoutHeader.addWidget(self.editLabel)
		self.hLayoutHeader.addWidget(self.deleteLabel)
		self.hLayoutHeader.addWidget(self.ruleLabel)
		self.hLayoutHeader.addWidget(self.enableLabel)

		# Rules
		grid_v_ind = 0
		self.editMapper = QtCore.QSignalMapper()
		self.deleteMapper = QtCore.QSignalMapper()
		self.checkMapper = QtCore.QSignalMapper()
		self.editIcon = QtGui.QIcon(getcwd() + '/icons/edit-icon.png')
		self.deleteIcon = QtGui.QIcon(getcwd() + '/icons/delete_icon.png')

		for rule in self.tagRules:
			rule_id = rule[0]
			if rule[1] == 'video_length':
				field = 'Video length (sec)'
			else:
				field = self.fieldLookup[rule[1]]
			oper = rule[2].replace('<', '&lt;').replace('>', '&gt;')
			if oper == 'CONTAINS' or oper == 'STARTS WITH' or ((oper == '=' or oper == '!=') and field != 'My rating'
															   and field != 'Star rating'):
				value = '"' + rule[3] + '"'
			else:
				value = rule[3]
			tg1 = self.fieldLookup['tags_1'][7:]
			tg2 = self.fieldLookup['tags_2'][7:]
			tg3 = self.fieldLookup['tags_3'][7:]
			tg4 = self.fieldLookup['tags_4'][7:]
			tg5 = self.fieldLookup['tags_5'][7:]
			tg6 = self.fieldLookup['tags_6'][7:]
			tags_1 = rule[4]
			tags_2 = rule[5]
			tags_3 = rule[6]
			tags_4 = rule[7]
			tags_5 = rule[8]
			tags_6 = rule[9]
			enabled = rule[10]
			text_string = 'If <b>{} {} {}</b> then check tag(s):<br><u>{}</u>: {}<br><u>{}</u>: {}<br><u>{}' \
						  '</u>: {}<br><u>{}</u>: {}<br><u>{}</u>: {}<br><u>{}</u>: {}'.format(
				field, oper, value, tg1, tags_1, tg2, tags_2, tg3, tags_3, tg4, tags_4, tg5, tags_5, tg6, tags_6)
			temp_wid_list = [QtWidgets.QPushButton(), QtWidgets.QPushButton(), QtWidgets.QTextEdit(),
							 QtWidgets.QCheckBox(), QtWidgets.QLabel()]

			temp_wid_list[0].setIcon(self.editIcon)
			temp_wid_list[0].setFixedSize(22, 22)
			temp_wid_list[0].setIconSize(QtCore.QSize(14, 14))
			self.gridLayout.addWidget(temp_wid_list[0], grid_v_ind, 0, alignment=QtCore.Qt.AlignTop)
			self.editMapper.setMapping(temp_wid_list[0], grid_v_ind)
			temp_wid_list[0].clicked.connect(self.editMapper.map)

			temp_wid_list[1].setIcon(self.deleteIcon)
			temp_wid_list[1].setFixedSize(22, 22)
			temp_wid_list[1].setIconSize(QtCore.QSize(14, 14))
			self.gridLayout.addWidget(temp_wid_list[1], grid_v_ind, 1, alignment=QtCore.Qt.AlignTop)
			self.deleteMapper.setMapping(temp_wid_list[1], grid_v_ind)
			temp_wid_list[1].clicked.connect(self.deleteMapper.map)

			temp_wid_list[2].setFixedSize(400, 110)
			temp_wid_list[2].setText(text_string)
			temp_wid_list[2].setReadOnly(True)
			self.gridLayout.addWidget(temp_wid_list[2], grid_v_ind, 2, alignment=QtCore.Qt.AlignTop)

			self.gridLayout.addWidget(temp_wid_list[3], grid_v_ind, 3, alignment=QtCore.Qt.AlignTop)
			if enabled == 1:
				temp_wid_list[3].setChecked(True)
			else:
				temp_wid_list[3].setChecked(False)
			self.checkMapper.setMapping(temp_wid_list[3], grid_v_ind)
			temp_wid_list[3].clicked.connect(self.checkMapper.map)

			temp_wid_list[4].setText(rule_id)
			temp_wid_list[4].hide()
			self.gridLayout.addWidget(temp_wid_list[4], grid_v_ind, 4)

			grid_v_ind += 1

		# Bottom
		self.bottomFont = QtGui.QFont()
		self.bottomFont.setBold(True)
		self.bottomFont.setPixelSize(20)
		self.newRuleButton = QtWidgets.QPushButton('+')
		self.newRuleButton.setToolTip('Add new rule')
		self.newRuleButton.setFont(self.bottomFont)
		self.newRuleButton.setFixedSize(30, 30)
		self.hLayoutBottom.addWidget(self.newRuleButton, alignment=QtCore.Qt.AlignLeft)

		self.closeButton = QtWidgets.QPushButton('Close')
		self.closeButton.setFixedSize(125, 30)
		self.hLayoutBottom.addWidget(self.closeButton, alignment=QtCore.Qt.AlignRight)

		# Layouts
		self.vLayoutMaster.addLayout(self.hLayoutHeader)
		self.scrollWidget.setLayout(self.gridLayout)
		self.scrollArea.setWidget(self.scrollWidget)
		self.vLayoutMaster.addWidget(self.scrollArea)
		self.vLayoutMaster.addLayout(self.hLayoutBottom)

		# Signals / slots
		self.editMapper.mapped.connect(self.edit_rule)
		self.deleteMapper.mapped.connect(self.clear_rule)
		self.checkMapper.mapped.connect(self.en_dis_rule)
		self.newRuleButton.clicked.connect(self.add_rule)
		self.closeButton.clicked.connect(self.close)

		# Widget
		self.wid = QtWidgets.QWidget()
		self.wid.setLayout(self.vLayoutMaster)
		self.setCentralWidget(self.wid)
		self.setFixedSize(540, 540)
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Manage custom tag logic')

		tag_log_win_conn.close()

	"""def clear_layout(self, layout):
		if layout is not None:
			while layout.count():
				item = layout.takeAt(0)
				widget = item.widget()
				if widget is not None:
					widget.deleteLater()
				else:
					self.clear_layout(item.layout())"""

	def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
		self.del_rules()

	def edit_rule(self, ind):
		edit_rule_id = self.gridLayout.itemAtPosition(ind, 4).widget().text()
		self.logic_win = TagLogicWindow(rule_id=edit_rule_id)
		self.logic_win.win_closed.connect(self.init_window)

	def clear_rule(self, ind):
		del_rule_id = self.gridLayout.itemAtPosition(ind, 4).widget().text()
		self.gridLayout.itemAtPosition(ind, 0).widget().setDisabled(True)
		self.gridLayout.itemAtPosition(ind, 1).widget().setDisabled(True)
		self.gridLayout.itemAtPosition(ind, 2).widget().setText('')
		self.gridLayout.itemAtPosition(ind, 3).widget().setDisabled(True)
		self.rulesToDeleteList.append(del_rule_id)

		rule_deleted_msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Rule deleted',
												 'This rule has been deleted.')
		rule_deleted_msg.exec_()

		"""for i in reversed(range(self.gridLayout.count())):
			if self.gridLayout is not None:
				wid = self.gridLayout.itemAt(i).widget()
				self.gridLayout.removeWidget(wid)
				wid.setParent(None)
		self.clear_layout(self.vLayoutMaster)

		self.test()"""

	def del_rules(self):
		if self.rulesToDeleteList:
			del_rule_conn = sqlite3.connect(common_vars.video_db())
			del_rule_cursor = del_rule_conn.cursor()

			for rule_id in self.rulesToDeleteList:
				del_rule_cursor.execute('DELETE FROM custom_tag_logic WHERE ctlr_id = ?', (rule_id,))

			del_rule_conn.commit()
			del_rule_conn.close()

	def en_dis_rule(self, ind):
		en_dis_conn = sqlite3.connect(common_vars.video_db())
		en_dis_cursor = en_dis_conn.cursor()
		en_dis_rule_id = self.gridLayout.itemAtPosition(ind, 4).widget().text()

		if self.gridLayout.itemAtPosition(ind, 3).widget().isChecked():
			val = 1
		else:
			val = 0

		en_dis_cursor.execute('UPDATE custom_tag_logic SET in_use = ? WHERE ctlr_id = ?', (val, en_dis_rule_id))
		en_dis_conn.commit()
		en_dis_conn.close()

	def add_rule(self):
		self.del_rules()
		self.new_rule_win = TagLogicWindow()
		self.new_rule_win.win_closed.connect(self.init_window)


class TagLogicWindow(ChooseFilterWindow):
	win_closed = QtCore.pyqtSignal()

	def __init__(self, rule_id=None):
		super(TagLogicWindow, self).__init__()
		grid_v_ind = 0
		tag_logic_conn = sqlite3.connect(common_vars.video_db())

		self.rule_id = rule_id
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

		if self.rule_id:
			self.pop_edit_win(self.rule_id)

	def pop_edit_win(self, rule_id):
		pew_conn = sqlite3.connect(common_vars.video_db())
		pew_cursor = pew_conn.cursor()
		phrase_dict = {'STARTS WITH': 'Starts with...',
					   'CONTAINS': 'Contains...',
					   '=': 'Equals...',
					   '<': 'Less than...',
					   '>': 'Greater than...',
					   'BEFORE': 'Before...',
					   'AFTER': 'After...',
					   'BETWEEN': 'Between...',
					   'IS CHECKED': 'Checked',
					   'IS UNCHECKED': 'Unchecked',
					   'IS POPULATED': 'Populated',
					   'IS NOT POPULATED': 'Not populated'}
		field_lookup = common_vars.video_field_lookup(reverse=False)

		pew_cursor.execute('SELECT * FROM custom_tag_logic WHERE ctlr_id = ?', (rule_id,))
		rule_data = pew_cursor.fetchone()

		if rule_data[1] == 'video_length':
			field = 'Video length (sec)'
		else:
			field = field_lookup[rule_data[1]]

		self.fieldNameDropdown.setCurrentText(field)

		for k, v in self.dictOfWidLists.items():
			for wid in v:
				if isinstance(wid, QtWidgets.QRadioButton):
					if wid.text() == phrase_dict[rule_data[2]]:
						wid.setChecked(True)

		if rule_data[2] == 'STARTS WITH' or rule_data[2] == 'CONTAINS' or (rule_data[2] == '=' and
																		   'rating' not in rule_data[1]):
			self.textFilterTextBox.setText(rule_data[3])

		elif (rule_data[2] == '=' and 'rating' in rule_data[1]) or rule_data[2] == '<' or rule_data[2] == '>':
			self.numberText.setText(rule_data[3])

		elif rule_data[2] == 'BEFORE' or rule_data[2] == 'AFTER' or rule_data[2] == 'BETWEEN':
			self.yearDrop1.setCurrentText(str(rule_data[3][:4]))
			self.monthDrop1.setCurrentIndex(int(rule_data[3][5:7]) - 1)
			self.dayDrop1.setCurrentIndex(int(rule_data[3][8:10]) - 1)

			if rule_data[2] == 'BETWEEN':
				self.yearDrop2.setCurrentText(str(rule_data[3][15:19]))
				self.yearDrop2.setEnabled(True)
				self.monthDrop2.setCurrentIndex(int(rule_data[3][20:22]) - 1)
				self.monthDrop2.setEnabled(True)
				self.dayDrop2.setCurrentIndex(int(rule_data[3][-2:]) - 1)
				self.dayDrop2.setEnabled(True)

		elif rule_data[2] == 'IS CHECKED':
			self.checked.setChecked(True)

		elif rule_data[2] == 'UNCHECKED':
			self.unchecked.setChecked(True)

		elif rule_data[2] == 'IS POPULATED':
			self.exists.setChecked(True)

		elif rule_data[2] == 'IS NOT POPULATED':
			self.doesNotExist.setChecked(True)

		else:
			print('Uh oh...check the code man')

		self.tags1Box.setText(rule_data[4])
		self.tags2Box.setText(rule_data[5])
		self.tags3Box.setText(rule_data[6])
		self.tags4Box.setText(rule_data[7])
		self.tags5Box.setText(rule_data[8])
		self.tags6Box.setText(rule_data[9])

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

		if self.rule_id:
			rule_id = self.rule_id
		else:
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

		insert_tup = (rule_id, field_int, operation, value, tags_1, tags_2, tags_3, tags_4, tags_5, tags_6, 1)
		if self.rule_id:
			save_rule_cursor.execute('UPDATE custom_tag_logic SET field = ?, operation = ?, value = ?, tags_1 = ?, '
									 'tags_2 = ?, tags_3 = ?, tags_4 = ?, tags_5 = ?, tags_6 = ? WHERE ctlr_id = ?',
									 (field_int, operation, value, tags_1, tags_2, tags_3, tags_4, tags_5, tags_6,
									  self.rule_id))
		else:
			save_rule_cursor.execute('INSERT OR IGNORE INTO custom_tag_logic VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', insert_tup)
		save_rule_conn.commit()

		rule_saved_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Rule saved', 'Rule has been saved.')
		rule_saved_win.exec_()

		self.win_closed.emit()
		save_rule_conn.close()
