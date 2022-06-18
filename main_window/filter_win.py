import sqlite3

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

from misc_files import common_vars, tag_checkboxes


class ChooseFilterWindow(QtWidgets.QDialog):
	def __init__(self, custom_logic=True):
		super(ChooseFilterWindow, self).__init__()
		self.customLogic = custom_logic
		filterWindowConn = sqlite3.connect(common_vars.settings_db())
		filterWindowCursor = filterWindowConn.cursor()

		filterWindowCursor.execute('SELECT field_name_display FROM search_field_lookup WHERE in_use = 1')
		if self.customLogic:
			self.fieldNames = [x[0] for x in filterWindowCursor.fetchall() if x[0] != 'Video length (min/sec)' and
							   'Tags' not in x[0] and x[0] != 'Sequence' and x[0] != 'Play Count' and x[0] !=
							   'Date entered']
		else:
			self.fieldNames = [x[0] for x in filterWindowCursor.fetchall() if x[0] != 'Video length (min/sec)']
		self.fieldNames.append('Video length (sec)')
		self.fieldNames.sort(key=lambda x: x.casefold())
		filterWindowConn.close()
		
		self.out_str = ''

		self.fieldAssoc = {'TEXT':
							   ['primary_editor_username',
								'primary_editor_pseudonyms',
								'addl_editors',
								'studio',
								'video_title',
								'video_footage',
								'song_artist',
								'song_title',
								'song_genre',
								'contests_entered',
								'awards_won',
								'video_description',
								'comments'],

						   'NUMBER':
							   ['star_rating',
								'video_length',
								'my_rating',
								'play_count',
								'sequence'],

						   'DATE':
							   ['release_date',
								'date_entered'],

						   'BOOLEAN':
							   ['release_date_unknown',
								'notable',
								'favorite'],

						   'TAGS':
							   ['tags_1', 'tags_2', 'tags_3', 'tags_4', 'tags_5', 'tags_6'],

						   'EXISTS':
							   ['video_youtube_url',
								'video_org_url',
								'video_amvnews_url',
								'video_other_url',
								'local_file',
								'editor_youtube_channel_url',
								'editor_org_profile_url',
								'editor_amvnews_profile_url',
								'editor_other_profile_url',
								'vid_thumb_path']
						   }

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.vLayoutMaster.setAlignment(QtCore.Qt.AlignTop)
		self.hLayout1 = QtWidgets.QHBoxLayout()
		self.hLayout1.setAlignment(QtCore.Qt.AlignLeft)
		self.gridLayout = QtWidgets.QGridLayout()
		self.gridLayout2 = QtWidgets.QGridLayout()
		self.hLayoutBottom = QtWidgets.QHBoxLayout()

		self.chooseFieldLabel = QtWidgets.QLabel()
		self.chooseFieldLabel.setText('Select the field to filter:')

		self.fieldNameDropdown = QtWidgets.QComboBox()
		self.fieldNameDropdown.setFixedWidth(180)
		self.fieldNameDropdown.setMaxVisibleItems(20)
		for field in self.fieldNames:
			self.fieldNameDropdown.addItem(field)

		self.hLayout1.addWidget(self.chooseFieldLabel)
		self.hLayout1.addWidget(self.fieldNameDropdown)

		self.closeButton = QtWidgets.QPushButton('Close')
		self.closeButton.setFixedWidth(125)

		self.okButton = QtWidgets.QPushButton('OK')
		self.okButton.setFixedWidth(125)

		# Text widgets
		v_ind = 0
		self.textEquals = QtWidgets.QRadioButton('Equals...')
		self.textEquals.setChecked(True)
		self.startsWith = QtWidgets.QRadioButton('Starts with...')
		self.contains = QtWidgets.QRadioButton('Contains...')
		self.textFilterBtnGroup = QtWidgets.QButtonGroup()
		self.textFilterBtnGroup.setExclusive(True)
		self.textFilterBtnGroup.addButton(self.textEquals)
		self.textFilterBtnGroup.addButton(self.startsWith)
		self.textFilterBtnGroup.addButton(self.contains)
		self.textFilterTextBox = QtWidgets.QLineEdit()
		self.textFilterTextBox.setFixedWidth(320)

		self.listOfTextWid = [self.textEquals, self.startsWith, self.contains, self.textFilterTextBox]

		self.gridLayout.addWidget(self.textEquals, v_ind, 0)
		self.gridLayout.addWidget(self.startsWith, v_ind, 1)
		self.gridLayout.addWidget(self.contains, v_ind, 2)
		v_ind += 1
		self.gridLayout.addWidget(self.textFilterTextBox, v_ind, 0, 1, 5)

		# Number widgets
		v_ind = 0
		self.numEquals = QtWidgets.QRadioButton('Equals...')
		self.numEquals.setChecked(True)
		self.lessThan = QtWidgets.QRadioButton('Less than...')
		self.lessThan.setDisabled(True)
		self.greaterThan = QtWidgets.QRadioButton('Greater than...')
		self.greaterThan.setDisabled(True)
		self.numberBtnGroup = QtWidgets.QButtonGroup()
		self.numberBtnGroup.setExclusive(True)
		self.numberBtnGroup.addButton(self.lessThan)
		self.numberBtnGroup.addButton(self.numEquals)
		self.numberBtnGroup.addButton(self.greaterThan)
		self.numberText = QtWidgets.QLineEdit()
		self.numberText.setFixedWidth(50)

		self.listOfNumberWid = [self.lessThan, self.numEquals, self.greaterThan, self.numberText]
		for wid in self.listOfNumberWid:
			wid.hide()

		self.gridLayout.addWidget(self.numEquals, v_ind, 0)
		self.gridLayout.addWidget(self.lessThan, v_ind, 1)
		self.gridLayout.addWidget(self.greaterThan, v_ind, 2)
		v_ind += 2
		self.gridLayout.addWidget(self.numberText, v_ind, 0)

		# Date widgets
		v_ind = 0
		self.month_dict = {'01 (Jan)': 31,
						   '02 (Feb)': 28,
						   '03 (Mar)': 31,
						   '04 (Apr)': 30,
						   '05 (May)': 31,
						   '06 (Jun)': 30,
						   '07 (Jul)': 31,
						   '08 (Aug)': 31,
						   '09 (Sep)': 30,
						   '10 (Oct)': 31,
						   '11 (Nov)': 30,
						   '12 (Dec)': 31}

		self.dateLabel = QtWidgets.QLabel()
		self.before = QtWidgets.QRadioButton('Before...')
		self.before.setChecked(True)
		self.after = QtWidgets.QRadioButton('After...')
		self.between = QtWidgets.QRadioButton('Between...')
		self.dateBtnGroup = QtWidgets.QButtonGroup()
		self.dateBtnGroup.setExclusive(True)
		self.dateBtnGroup.addButton(self.before)
		self.dateBtnGroup.addButton(self.after)
		self.dateBtnGroup.addButton(self.between)

		self.yearDrop1 = QtWidgets.QComboBox()
		self.monthDrop1 = QtWidgets.QComboBox()
		self.dayDrop1 = QtWidgets.QComboBox()
		self.dayDrop1.setFixedWidth(50)

		self.andLabel = QtWidgets.QLabel()
		self.andLabel.setText('and')
		self.andLabel.setDisabled(True)

		self.yearDrop2 = QtWidgets.QComboBox()
		self.yearDrop2.setDisabled(True)
		self.monthDrop2 = QtWidgets.QComboBox()
		self.monthDrop2.setDisabled(True)
		self.dayDrop2 = QtWidgets.QComboBox()
		self.dayDrop2.setDisabled(True)
		self.dayDrop2.setFixedWidth(50)

		self.listOfDateWid = [self.dateLabel, self.before, self.after, self.between, self.yearDrop1, self.monthDrop1,
							  self.dayDrop1, self.andLabel, self.yearDrop2, self.monthDrop2, self.dayDrop2]
		for wid in self.listOfDateWid:
			wid.hide()

		self.gridLayout.addWidget(self.dateLabel, v_ind, 0)
		v_ind += 1
		self.gridLayout.addWidget(self.before, v_ind, 0)
		self.gridLayout.addWidget(self.after, v_ind, 1)
		self.gridLayout.addWidget(self.between, v_ind, 2)
		v_ind += 1
		self.gridLayout.addWidget(self.yearDrop1, v_ind, 0)
		self.gridLayout.addWidget(self.monthDrop1, v_ind, 1)
		self.gridLayout.addWidget(self.dayDrop1, v_ind, 2)
		self.populate_date_dropdown(self.yearDrop1, self.monthDrop1, self.dayDrop1)
		v_ind += 1
		self.gridLayout.addWidget(self.andLabel, v_ind, 1)
		v_ind += 1
		self.gridLayout.addWidget(self.yearDrop2, v_ind, 0)
		self.gridLayout.addWidget(self.monthDrop2, v_ind, 1)
		self.gridLayout.addWidget(self.dayDrop2, v_ind, 2)
		self.populate_date_dropdown(self.yearDrop2, self.monthDrop2, self.dayDrop2)

		# Boolean widgets
		v_ind = 0
		self.booleanLabel = QtWidgets.QLabel()
		self.checked = QtWidgets.QRadioButton('Checked')
		self.checked.setChecked(True)
		self.unchecked = QtWidgets.QRadioButton('Unchecked')
		self.booleanBtnGroup = QtWidgets.QButtonGroup()
		self.booleanBtnGroup.setExclusive(True)
		self.booleanBtnGroup.addButton(self.checked)
		self.booleanBtnGroup.addButton(self.unchecked)

		self.listOfBooleanWid = [self.booleanLabel, self.checked, self.unchecked]
		for wid in self.listOfBooleanWid:
			wid.hide()

		self.gridLayout.addWidget(self.booleanLabel, v_ind, 0, 1, 5)
		v_ind += 2
		self.gridLayout.addWidget(self.checked, v_ind, 0)
		self.gridLayout.addWidget(self.unchecked, v_ind, 1)

		# Tag widgets
		v_ind = 0
		self.tagsAny = QtWidgets.QRadioButton('Contains ANY tags...')
		self.tagsAny.setChecked(True)
		self.tagsAll = QtWidgets.QRadioButton('Contains ALL tags...')
		self.tagsBtnGroup = QtWidgets.QButtonGroup()
		self.tagsBtnGroup.setExclusive(True)
		self.tagsBtnGroup.addButton(self.tagsAny)
		self.tagsBtnGroup.addButton(self.tagsAll)
		self.selectTagsBtn = QtWidgets.QPushButton('+')
		self.selectTagsBtn.setToolTip('Select tag(s)')
		self.selectTagsBtn.setFixedWidth(30)
		self.tagsText = QtWidgets.QLineEdit()
		self.tagsText.setFixedWidth(220)
		self.tagsText.setReadOnly(True)

		self.listOfTagsWid = [self.tagsAny, self.tagsAll, self.selectTagsBtn, self.tagsText]
		for wid in self.listOfTagsWid:
			wid.hide()

		self.gridLayout.addWidget(self.tagsAny, v_ind, 0, 1, 3)
		self.gridLayout.addWidget(self.tagsAll, v_ind, 3, 1, 3)
		v_ind += 1
		self.gridLayout.addWidget(self.tagsText, v_ind, 1, 1, 6)
		self.gridLayout.addWidget(self.selectTagsBtn, v_ind, 0)

		# Exists widgets
		v_ind = 0
		self.existsLabel = QtWidgets.QLabel()
		self.exists = QtWidgets.QRadioButton('Populated')
		self.exists.setChecked(True)
		self.doesNotExist = QtWidgets.QRadioButton('Not populated')
		self.existsBtnGroup = QtWidgets.QButtonGroup()
		self.existsBtnGroup.setExclusive(True)
		self.existsBtnGroup.addButton(self.exists)
		self.existsBtnGroup.addButton(self.doesNotExist)

		self.listOfExistsWid = [self.existsLabel, self.exists, self.doesNotExist]
		for wid in self.listOfExistsWid:
			wid.hide()

		self.gridLayout.addWidget(self.existsLabel, v_ind, 0, 1, 4)
		v_ind += 1
		self.gridLayout.addWidget(self.exists, v_ind, 0)
		self.gridLayout.addWidget(self.doesNotExist, v_ind, 1)

		self.dictOfWidLists = {'TEXT': self.listOfTextWid,
							   'NUMBER': self.listOfNumberWid,
							   'DATE': self.listOfDateWid,
							   'BOOLEAN': self.listOfBooleanWid,
							   'TAGS': self.listOfTagsWid,
							   'EXISTS': self.listOfExistsWid}

		# Layouts
		self.vLayoutMaster.addLayout(self.hLayout1)
		self.vLayoutMaster.addSpacing(10)
		self.vLayoutMaster.addLayout(self.gridLayout)
		self.vLayoutMaster.addSpacing(5)
		self.vLayoutMaster.addLayout(self.gridLayout2)
		self.vLayoutMaster.addSpacing(5)
		self.hLayoutBottom.addWidget(self.closeButton)
		self.hLayoutBottom.addWidget(self.okButton)
		self.vLayoutMaster.addLayout(self.hLayoutBottom)

		# Signals / slots
		self.fieldNameDropdown.currentIndexChanged.connect(self.show_hide_widgets)
		self.dateBtnGroup.buttonClicked.connect(self.en_dis_date_drops)
		self.yearDrop1.currentIndexChanged.connect(
			lambda: self.populate_day(self.yearDrop1, self.monthDrop1, self.dayDrop1))
		self.monthDrop1.currentIndexChanged.connect(
			lambda: self.populate_day(self.yearDrop1, self.monthDrop1, self.dayDrop1))
		self.yearDrop2.currentIndexChanged.connect(
			lambda: self.populate_day(self.yearDrop2, self.monthDrop2, self.dayDrop2))
		self.monthDrop2.currentIndexChanged.connect(
			lambda: self.populate_day(self.yearDrop2, self.monthDrop2, self.dayDrop2))
		self.numberText.textChanged.connect(self.check_num_integrity)
		self.selectTagsBtn.clicked.connect(self.get_tags)
		self.closeButton.clicked.connect(self.reject)
		self.okButton.clicked.connect(self.ok_clicked)

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setWindowTitle('Select filter')
		self.setFixedSize(350, 200)
		self.show()

	def en_dis_date_drops(self):
		if self.between.isChecked():
			self.andLabel.setEnabled(True)
			self.yearDrop2.setEnabled(True)
			self.monthDrop2.setEnabled(True)
			self.dayDrop2.setEnabled(True)
		else:
			self.andLabel.setDisabled(True)
			self.yearDrop2.setDisabled(True)
			self.monthDrop2.setDisabled(True)
			self.dayDrop2.setDisabled(True)

	def populate_date_dropdown(self, year_wid, month_wid, day_wid):
		year_list = [str(yr) for yr in range(common_vars.year_plus_one(), 1981, -1)]

		for year in year_list:
			year_wid.addItem(year)
		year_wid.setCurrentIndex(1)

		for k, v in self.month_dict.items():
			month_wid.addItem(k)

		for daynum in range(1, 32):
			day_wid.addItem(str(daynum))

	def populate_day(self, year_wid, month_wid, day_wid):
		day_wid.clear()

		if int(year_wid.currentText()) % 4 == 0:
			self.month_dict['02 (Feb)'] = 29
		else:
			self.month_dict['02 (Feb)'] = 28

		for x in range(1, self.month_dict[month_wid.currentText()] + 1):
			day_wid.addItem(str(x))

	def show_hide_widgets(self):
		if self.fieldNameDropdown.currentText() == 'Video length (sec)':
			field_name = 'Video length (min/sec)'
		else:
			field_name = self.fieldNameDropdown.currentText()
		show_hide_conn = sqlite3.connect(common_vars.settings_db())
		show_hide_cursor = show_hide_conn.cursor()
		show_hide_cursor.execute('SELECT field_name_internal FROM search_field_lookup WHERE field_name_display = ?',
								 (field_name,))
		field_name_int = show_hide_cursor.fetchone()[0]

		field_type = [k for k, v in self.fieldAssoc.items() if field_name_int in v][0]

		for key, val in self.dictOfWidLists.items():
			for wid in val:
				if field_type == key:
					wid.show()
				else:
					wid.hide()

		if self.customLogic:
			self.booleanLabel.setText('...is...')
			self.existsLabel.setText('...is...')
			self.dateLabel.setText('...is...')
		else:
			self.booleanLabel.setText('<b>{}</b> box is...'.format(self.fieldNameDropdown.currentText()))
			self.existsLabel.setText('<b>{}</b> field is...'.format(self.fieldNameDropdown.currentText()))

		self.tagsText.clear()

		show_hide_conn.close()

	def check_num_integrity(self):
		num_err = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
										'You must enter a non-negative number into this box, or leave it blank')
		is_number = True
		is_blank = False
		is_positive = True

		try:
			float(self.numberText.text())
		except:
			is_number = False

		if is_number and float(self.numberText.text()) >= 0:
			is_positive = True
		elif self.numberText.text() == '':
			is_blank = True
		else:
			is_positive = False

		if is_blank:
			self.numEquals.setChecked(True)
			self.okButton.setEnabled(True)
			self.lessThan.setDisabled(True)
			self.greaterThan.setDisabled(True)
		elif not is_number or not is_positive:
			self.okButton.setDisabled(True)
			num_err.exec_()
		else:
			self.okButton.setEnabled(True)
			self.lessThan.setEnabled(True)
			self.greaterThan.setEnabled(True)

	def get_tags(self):
		tag_field = self.fieldNameDropdown.currentText().split(' - ')[1]
		tag_win = tag_checkboxes.TagWindow(tag_field, ignore_mut_excl=True)
		if tag_win.exec_():
			self.tagsText.setText(tag_win.out_str[:-2])

	def ok_clicked(self):
		if self.fieldNameDropdown.currentText() == 'Video length (sec)':
			field_name = 'Video length (min/sec)'
		else:
			field_name = self.fieldNameDropdown.currentText()
		ok_clicked_conn = sqlite3.connect(common_vars.settings_db())
		ok_clicked_cursor = ok_clicked_conn.cursor()
		ok_clicked_cursor.execute('SELECT field_name_internal FROM search_field_lookup WHERE field_name_display = ?',
								  (field_name,))
		field_name_int = ok_clicked_cursor.fetchone()[0]
		curr_field_type = [k for k, v in self.fieldAssoc.items() if field_name_int in v][0]

		field = self.fieldNameDropdown.currentText()
		if curr_field_type == 'TEXT':
			if self.textEquals.isChecked():
				op = ' = '
			elif self.startsWith.isChecked():
				op = ' STARTS WITH '
			else:
				op = ' CONTAINS '

			self.out_str = field + op + self.textFilterTextBox.text()

		elif curr_field_type == 'NUMBER':
			if self.numEquals.isChecked():
				op = ' = '
			elif self.lessThan.isChecked():
				op = ' < '
			else:
				op = ' > '

			self.out_str = field + op + self.numberText.text()

		elif curr_field_type == 'DATE':
			if self.before.isChecked():
				op = ' BEFORE '
			elif self.after.isChecked():
				op = ' AFTER '
			else:
				op = ' BETWEEN '
			
			date_1_sum = (int(self.yearDrop1.currentText()) * 365) + (int(self.monthDrop1.currentText()[:2]) * 30) + \
						 int(self.dayDrop1.currentText())
			date_2_sum = (int(self.yearDrop2.currentText()) * 365) + (int(self.monthDrop2.currentText()[:2]) * 30) + \
						 int(self.dayDrop2.currentText())

			if len(self.dayDrop1.currentText()) == 1:
				day1 = '0' + self.dayDrop1.currentText()
			else:
				day1 = self.dayDrop1.currentText()

			if len(self.dayDrop2.currentText()) == 1:
				day2 = '0' + self.dayDrop2.currentText()
			else:
				day2 = self.dayDrop2.currentText()

			if self.between.isChecked() and date_1_sum <= date_2_sum:
				date_str = self.yearDrop1.currentText() + '/' + self.monthDrop1.currentText()[:2] + '/' + day1 + \
						   ' AND ' + self.yearDrop2.currentText() + '/' + self.monthDrop2.currentText()[:2] + '/' + day2
			elif self.between.isChecked() and date_2_sum < date_1_sum:
				date_str = self.yearDrop2.currentText() + '/' + self.monthDrop2.currentText()[:2] + '/' + day2 + \
						   ' AND ' + self.yearDrop1.currentText() + '/' + self.monthDrop1.currentText()[:2] + '/' + day1
			else:
				date_str = self.yearDrop1.currentText() + '/' + self.monthDrop1.currentText()[:2] + '/' + day1

			self.out_str = field + op + date_str

		elif curr_field_type == 'BOOLEAN':
			if self.checked.isChecked():
				op = ' IS CHECKED '
			else:
				op = ' IS UNCHECKED '

			self.out_str = field + op

		elif curr_field_type == 'TAGS':
			if self.tagsAny.isChecked():
				op = ' INCLUDES ANY: '
			else:
				op = ' INCLUDES ALL: '

			self.out_str = field + op + self.tagsText.text()

		else:  # EXISTS
			if self.exists.isChecked():
				op = ' IS POPULATED '
			else:
				op = ' IS NOT POPULATED '

			self.out_str = field + op

		self.op = op
		self.value = self.out_str.split(op)[1]

		ok_clicked_conn.close()
		self.accept()
