import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import sqlite3

from misc_files import common_vars, check_for_db


class MutuallyExclTagsWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(MutuallyExclTagsWindow, self).__init__()

		# Initialize SQLite connections
		tag_conn = sqlite3.connect(common_vars.video_db())
		tag_cursor = tag_conn.cursor()

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayout1 = QtWidgets.QHBoxLayout()
		self.hLayout2 = QtWidgets.QHBoxLayout()
		self.hLayout3 = QtWidgets.QHBoxLayout()
		self.hLayoutBottom = QtWidgets.QHBoxLayout()

		self.label1 = QtWidgets.QLabel()
		self.label1.setText('From here you can set tags within a single tag group to be\n'
		                    '"mutually exclusive", meaning that when a given tag is\n'
		                    'checked on data entry, any tags you identify here will be\n'
		                    'disabled automatically so that you cannot check them. This\n'
		                    'is useful to keep tag choices and data consistent as you\n'
		                    'enter videos into AMV Tracker.')

		self.label2 = QtWidgets.QLabel()
		self.label2.setText('Select the tag group:')
		self.tagGroupDrop = QtWidgets.QComboBox()
		self.tagGroupDrop.setFixedWidth(150)
		tag_cursor.execute('SELECT user_field_name FROM tags_lookup WHERE in_use = ?', ('1',))
		self.tagGroupList = [t[0] for t in tag_cursor.fetchall()]
		for tag in self.tagGroupList:
			self.tagGroupDrop.addItem(tag)
		
		self.label3 = QtWidgets.QLabel()
		self.label3.setText('If this tag is checked -->')
		self.tagNameDrop = QtWidgets.QComboBox()
		self.tagNameDrop.setFixedWidth(150)
		self.populate_tag_name_drop()
		
		self.label4 = QtWidgets.QLabel()
		self.label4.setText('...then prevent the following tag(s) from being checkable:')
		# Checkboxes go here
	
		self.saveButton = QtWidgets.QPushButton('Save changes')
		self.closeButton = QtWidgets.QPushButton('Close')
		
		# Layouts
		self.vLayoutMaster.addWidget(self.label1)
		self.vLayoutMaster.addSpacing(20)
		
		self.hLayout1.addWidget(self.label2)
		self.hLayout1.addWidget(self.tagGroupDrop)
		self.vLayoutMaster.addLayout(self.hLayout1)
		
		self.hLayout2.addWidget(self.label3)
		self.hLayout2.addWidget(self.tagNameDrop)
		self.vLayoutMaster.addLayout(self.hLayout2)
		self.vLayoutMaster.addSpacing(200)
		
		self.hLayoutBottom.addWidget(self.closeButton)
		self.hLayoutBottom.addWidget(self.saveButton)
		self.vLayoutMaster.addLayout(self.hLayoutBottom)
		
		# Signals / slots
		self.closeButton.clicked.connect(self.close)
		self.tagGroupDrop.currentIndexChanged.connect(self.populate_tag_name_drop)

		# Close db conn
		tag_conn.close()
		
		# Widget
		self.wid = QtWidgets.QWidget()
		self.wid.setLayout(self.vLayoutMaster)
		self.setCentralWidget(self.wid)
		self.setFixedSize(self.sizeHint())
		self.setWindowTitle('Mutually exclusive tags')
		self.show()

	def populate_tag_name_drop(self):
		self.tagNameDrop.clear()
		group_w_name = common_vars.tag_group_w_tag_names('user')
		for group, tags in group_w_name.items():
			if group.casefold() == self.tagGroupDrop.currentText().casefold():
				for t in tags:
					self.tagNameDrop.addItem(t)