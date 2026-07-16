import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import sqlite3

from os import getcwd

from misc_files import common_vars


class QuickSearchFieldsWindow(QtWidgets.QDialog):
	def __init__(self):
		super(QuickSearchFieldsWindow, self).__init__()

		self.fieldNames = common_vars.settings_field_return('search_field_lookup', 'field_name_display')
		self.fieldNames.sort()
		self.fieldNames.insert(0, 'Select all')
		self.fieldNamesChecked = common_vars.settings_field_return('search_field_lookup', 'field_name_display',
															query_parameter='avail_in_txt_search = 1')
		self.checkGroup = QtWidgets.QButtonGroup()
		self.checkGroup.setExclusive(False)
		self.signalMapper = QtCore.QSignalMapper()

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.vLayout = QtWidgets.QVBoxLayout()
		self.hLayout = QtWidgets.QHBoxLayout()

		self.scrollWidget = QtWidgets.QWidget()
		self.scrollArea = QtWidgets.QScrollArea()

		self.windowLabel = QtWidgets.QLabel()
		self.windowLabel.setText('Select the fields you would like to search through\n'
								 'when using the Quick Search function.')

		self.listChecks = [QtWidgets.QCheckBox(field) for field in self.fieldNames]
		for cbox in self.listChecks:
			self.checkGroup.addButton(cbox)

		# Checkboxes
		ind = 0
		for ckbox in self.listChecks:
			self.vLayout.addWidget(ckbox)
			if ckbox.text() in self.fieldNamesChecked:
				ckbox.setChecked(True)

			self.signalMapper.setMapping(ckbox, ind)
			ind += 1
			ckbox.clicked.connect(self.signalMapper.map)

		# Back / Submit buttons
		self.backButton = QtWidgets.QPushButton('Back')
		self.submitButton = QtWidgets.QPushButton('Submit')

		# Layouts
		self.vLayoutMaster.addWidget(self.windowLabel)
		self.vLayoutMaster.addSpacing(10)
		self.scrollWidget.setLayout(self.vLayout)
		self.scrollArea.setWidget(self.scrollWidget)
		self.vLayoutMaster.addWidget(self.scrollArea)

		self.hLayout.addWidget(self.backButton)
		self.hLayout.addWidget(self.submitButton)
		self.vLayoutMaster.addLayout(self.hLayout)

		# Signals / slots
		self.checkGroup.buttons()[0].clicked.connect(self.select_all_clicked)
		self.checkGroup.buttonClicked.connect(self.en_dis_submit_button)
		self.backButton.clicked.connect(self.close)
		self.submitButton.clicked.connect(self.submit_clicked)

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Quick Search settings')
		self.setFixedSize(260, 520)

	def select_all_clicked(self):
		if self.checkGroup.buttons()[0].isChecked():
			for cbox in self.listChecks:
				cbox.setChecked(True)
		else:
			for cbox in self.listChecks:
				cbox.setChecked(False)

	def en_dis_submit_button(self):
		checked_ctr = 0
		for cbox in self.listChecks:
			if cbox.isChecked():
				checked_ctr += 1

		if checked_ctr == 0:
			self.submitButton.setDisabled(True)
			self.submitButton.setToolTip('You must select at least one field.')
		else:
			self.submitButton.setEnabled(True)
			self.submitButton.setToolTip('')

	def submit_clicked(self):
		settings_conn = sqlite3.connect(common_vars.settings_db())
		settings_cursor = settings_conn.cursor()

		for cbox in self.listChecks:
			if cbox.text() == 'Select all':
				pass
			elif cbox.isChecked():
				settings_cursor.execute('UPDATE search_field_lookup SET avail_in_txt_search = 1 WHERE '
										'field_name_display = ?', (cbox.text(),))
			else:
				settings_cursor.execute('UPDATE search_field_lookup SET avail_in_txt_search = 0 WHERE '
										'field_name_display = ?', (cbox.text(),))

		settings_conn.commit()
		settings_conn.close()

		self.close()

