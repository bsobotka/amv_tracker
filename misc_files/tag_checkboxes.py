import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import sqlite3

from os import getcwd

from misc_files import common_vars


class TagWindow(QtWidgets.QDialog):
	def __init__(self, tag_table, checked_tags=None, ignore_mut_excl=False):
		super(TagWindow, self).__init__()

		self.out_str = ''
		self.tag_table_friendly = tag_table
		self.tag_table_internal = common_vars.tag_table_lookup()[self.tag_table_friendly]
		self.checked_tags = checked_tags
		self.signalMapper = QtCore.QSignalMapper()
		self.conn = sqlite3.connect(common_vars.tag_db())
		self.checkGroup = QtWidgets.QButtonGroup()

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.vLayout = QtWidgets.QVBoxLayout()
		hLayout = QtWidgets.QHBoxLayout()
		scrollWidget = QtWidgets.QWidget()
		scrollArea = QtWidgets.QScrollArea()

		self.listOfTagData = [[tag[0], tag[1], tag[2]] for tag in self.conn.execute('SELECT * FROM {}'
		                                                                    .format(self.tag_table_internal))]
		self.listOfTagData.sort(key=lambda x: x[2])
		self.listChecks = [QtWidgets.QCheckBox(tag[0]) for tag in self.listOfTagData]
		for check in self.listChecks:
			self.checkGroup.addButton(check)
		self.checkGroup.setExclusive(False)

		if self.checked_tags is not None:
			self.checked_tag_names_list = self.checked_tags.split('; ')
			self.checked_tag_num_list = []
			for tn in self.checked_tag_names_list:
				for ind in range(0, len(self.listOfTagData)):
					if tn.lower() == self.listOfTagData[ind][0].lower():
						self.checked_tag_num_list.append(self.listOfTagData[ind][2] - 1)
		else:
			self.checked_tag_num_list = []
			self.checked_tag_names_list = []

		self.check_lst = [] + self.checked_tag_num_list

		# Header
		self.headerFont = QtGui.QFont()
		self.headerFont.setBold(True)
		self.headerFont.setUnderline(True)
		self.headerFont.setPixelSize(14)

		self.tagLabel = QtWidgets.QLabel()
		self.tagLabel.setText(self.tag_table_friendly)
		self.tagLabel.setFont(self.headerFont)

		# Checkboxes
		ind = 0
		for check in self.listChecks:
			self.vLayout.addWidget(check)

			if check.text().lower() in self.checked_tag_names_list:
				check.setChecked(True)
			if self.listOfTagData[ind][1] is not None:
				check.setToolTip('<font color=black>' + self.listOfTagData[ind][1] + '</font>')
			self.signalMapper.setMapping(check, ind)
			ind += 1
			check.clicked.connect(self.signalMapper.map)

		if self.check_lst:
			self.tags_exist()

		# Back/Submit buttons
		self.backButton = QtWidgets.QPushButton('Back')
		self.backButton.setFixedWidth(100)
		
		self.submitButton = QtWidgets.QPushButton('Submit')
		self.submitButton.setFixedWidth(100)
		self.submitButton.setDisabled(True)

		hLayout.addWidget(self.backButton)
		hLayout.addWidget(self.submitButton)

		self.vLayoutMaster.addWidget(self.tagLabel, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addSpacing(10)
		scrollWidget.setLayout(self.vLayout)
		scrollArea.setWidget(scrollWidget)
		self.vLayoutMaster.addWidget(scrollArea)
		self.vLayoutMaster.addLayout(hLayout)

		# Signals/slots
		self.backButton.clicked.connect(self.reject)
		self.submitButton.clicked.connect(self.accept)
		self.signalMapper.mapped.connect(self.update_tag_list)
		if not ignore_mut_excl:
			self.signalMapper.mapped.connect(self.mut_excl_tags)

		## Widget ##
		self.setLayout(self.vLayoutMaster)
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Tags - ' + tag_table)
		self.setFixedSize(240, 520)

	def tags_exist(self):
		# Method for disabling tag checkboxes if user clicks into tag window with some checkboxes already checked which
		# themselves have mutually exclusive tags associated with them

		tags_exist_conn = sqlite3.connect(common_vars.video_db())
		tags_exist_cursor = tags_exist_conn.cursor()

		for tag in self.checked_tags:
			tags_exist_cursor.execute('SELECT tag_name, disable_tags FROM {}'.format(self.tag_table_internal))
		disable_dict = {x[0]: x[1].split('; ') for x in tags_exist_cursor.fetchall() if x[1] is not None}
		all_tags_to_dis = list(set([item for sublist in [v for k, v in disable_dict.items() if k.lower() in self.checked_tags]
		                            for item in sublist]))
		if '' in all_tags_to_dis:
			all_tags_to_dis.remove('')

		for cbox_ind in range(0, self.vLayout.count()):
			cbox_wid = self.vLayout.itemAt(cbox_ind).widget()
			if cbox_wid.text() in all_tags_to_dis:
				cbox_wid.setDisabled(True)
				cbox_wid.setChecked(False)

	def mut_excl_tags(self, check_ind):
		# Method for enabling/disabling mutually exclusive tag checkboxes based on which tags are checked
		mut_excl_tag_conn = sqlite3.connect(common_vars.video_db())
		mut_excl_tag_cursor = mut_excl_tag_conn.cursor()
		tags_to_disable = []

		list_of_checked = [self.vLayout.itemAt(i).widget().text() for i in range(0, self.vLayout.count()) if
		                   self.vLayout.itemAt(i).widget().isChecked()]

		if len(list_of_checked) > 0:
			for cbox in list_of_checked:
				mut_excl_tag_cursor.execute('SELECT disable_tags FROM {} WHERE tag_name = ?'
				                            .format(self.tag_table_internal), (cbox,))
				tags = mut_excl_tag_cursor.fetchone()[0].split('; ')
				for t in tags:
					if t not in tags_to_disable:
						tags_to_disable.append(t)

			for cbox_ind in range(0, self.vLayout.count()):
				cbox_wid = self.vLayout.itemAt(cbox_ind).widget()
				if cbox_wid.text() in tags_to_disable:
					cbox_wid.setDisabled(True)
					cbox_wid.setChecked(False)
				else:
					cbox_wid.setEnabled(True)

		else:
			for cbox_ind in range(0, self.vLayout.count()):
				self.vLayout.itemAt(cbox_ind).widget().setEnabled(True)

		mut_excl_tag_conn.close()

	def update_tag_list(self, check_num):
		# Method for providing ;-delimited string of labels from any checked boxes

		self.submitButton.setEnabled(True)

		if check_num not in self.check_lst:
			self.check_lst.append(check_num)
		else:
			self.check_lst.remove(check_num)

		self.check_lst.sort()

		self.out_lst = [self.listOfTagData[tag_ind][0] for tag_ind in self.check_lst]
		self.out_str = ''

		for tag in self.out_lst:
			self.out_str += (tag.lower() + '; ')		
