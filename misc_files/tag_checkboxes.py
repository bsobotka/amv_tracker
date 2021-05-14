import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import sqlite3

from misc_files import common_vars


class TagWindow(QtWidgets.QDialog):
	def __init__(self, tag_table, checked_tags=None):
		super(TagWindow, self).__init__()

		self.out_str = ''
		self.tag_table_friendly = tag_table
		self.tag_table_internal = common_vars.tag_table_lookup()[self.tag_table_friendly]
		self.signalMapper = QtCore.QSignalMapper()
		self.conn = sqlite3.connect(common_vars.tag_db())

		self.listOfTagData = [[tag[0], tag[1], tag[2]] for tag in self.conn.execute('SELECT * FROM {}'
		                                                                    .format(self.tag_table_internal))]
		self.listOfTagData.sort(key=lambda x: x[2])
		self.listChecks = [QtWidgets.QCheckBox(tag[0]) for tag in self.listOfTagData]

		if checked_tags is not None:
			self.checked_tag_names_list = checked_tags.split(';')
			self.checked_tag_num_list = []
			for tn in self.checked_tag_names_list:
				for ind in range(0, len(self.listOfTagData)):
					if tn.lower() == self.listOfTagData[ind][0].lower():
						self.checked_tag_num_list.append(self.listOfTagData[ind][2] - 1)
		else:
			self.checked_tag_num_list = []

		self.check_lst = [] + self.checked_tag_num_list

		vLayoutMaster = QtWidgets.QVBoxLayout()
		vLayout = QtWidgets.QVBoxLayout()
		hLayout = QtWidgets.QHBoxLayout()
		scrollWidget = QtWidgets.QWidget()
		scrollArea = QtWidgets.QScrollArea()

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
			vLayout.addWidget(check)

			if check.text().lower() in self.checked_tag_names_list:
				check.setChecked(True)
			if self.listOfTagData[ind][1] is not None:
				check.setToolTip('<font color=black>' + self.listOfTagData[ind][1] + '</font>')
			self.signalMapper.setMapping(check, ind)
			ind += 1
			check.clicked.connect(self.signalMapper.map)

		# Back/Submit buttons
		self.backButton = QtWidgets.QPushButton('Back')
		self.backButton.setFixedWidth(100)
		
		self.submitButton = QtWidgets.QPushButton('Submit')
		self.submitButton.setFixedWidth(100)

		hLayout.addWidget(self.backButton)
		hLayout.addWidget(self.submitButton)

		vLayoutMaster.addWidget(self.tagLabel, alignment=QtCore.Qt.AlignCenter)
		vLayoutMaster.addSpacing(10)
		scrollWidget.setLayout(vLayout)
		scrollArea.setWidget(scrollWidget)
		vLayoutMaster.addWidget(scrollArea)
		vLayoutMaster.addLayout(hLayout)

		# Signals/slots
		self.backButton.clicked.connect(self.reject)
		self.submitButton.clicked.connect(self.accept)
		self.signalMapper.mapped.connect(self.update_tag_list)

		## Widget ##
		self.setLayout(vLayoutMaster)
		self.setWindowTitle('Tags - ' + tag_table)
		self.setFixedSize(240, 520)

	def update_tag_list(self, check_num):
		if check_num not in self.check_lst:
			self.check_lst.append(check_num)
		else:
			self.check_lst.remove(check_num)

		self.check_lst.sort()

		self.out_lst = [self.listOfTagData[tag_ind][0] for tag_ind in self.check_lst]
		self.out_str = ''

		for tag in self.out_lst:
			self.out_str += (tag.lower() + '; ')
