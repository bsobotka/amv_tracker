import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

from os import getcwd


class CheckboxListWindow(QtWidgets.QDialog):
	def __init__(self, win_type, cbox_item_list, drop_list=None):
		super(CheckboxListWindow, self).__init__()

		self.win_type = win_type
		self.cbox_items_list = sorted(cbox_item_list, key=lambda x: x.casefold())
		self.cbox_list = [QtWidgets.QCheckBox(item) for item in self.cbox_items_list]
		self.drop_list = drop_list

		vLayoutMaster = QtWidgets.QVBoxLayout()
		scrollVLayout = QtWidgets.QVBoxLayout()
		hLayoutBottom = QtWidgets.QHBoxLayout()
		scrollWidget = QtWidgets.QWidget()
		scrollArea = QtWidgets.QScrollArea()

		self.label1 = QtWidgets.QLabel()
		self.label2 = QtWidgets.QLabel()
		self.drop = QtWidgets.QComboBox()
		self.backButton = QtWidgets.QPushButton('Back')
		self.backButton.setFixedWidth(100)
		self.submitButton = QtWidgets.QPushButton()
		self.submitButton.setFixedWidth(100)

		if self.win_type == 'del sub db':
			self.label1.setText('<b>PLEASE NOTE: Deleting a sub-DB removes all video entries in it</b><br>'
			                    '<b>from your database and cannot be undone. Proceed with caution.</b><br>'
			                    '<p>Select the sub-DB(s) to delete:')
			self.win_title = 'Delete sub-DBs'
			self.submitButton.setText('Delete')

		elif self.win_type == 'clear all':
			self.label1.setText('<b>PLEASE NOTE: <u>All</u> data will be removed from the selected sub-</b><br>'
			                    '<b>DBs, and this cannot be undone. Proceed with caution.</b><p>Select the sub-DB(s) to clear:')
			self.win_title = 'Clear all data'
			self.submitButton.setText('Clear')

		elif self.win_type == 'clear selected':
			self.label1.setText('<b>PLEASE NOTE: All data will be removed from the chosen field(s)</b><br>'
			                    '<b>in the selected sub-DB. This cannot be undone. Proceed with</b><br>'
								'<b>caution.</b><br>'
			                    '<p>Select the sub-DB to clear:')
			self.label2.setText('Select the field(s) to clear:')
			self.win_title = 'Clear selected data'
			self.submitButton.setText('Clear')

			for subdb in self.drop_list:
				self.drop.addItem(subdb)

		elif self.win_type == 'del cust lists':
			self.label1.setText('<b>PLEASE NOTE: Deleting a Custom List <u>will not</u> remove any videos</b><br>'
			                    '<b>from your database, however it will remove the selected list(s)</b><br>'
			                    '<b>from your database. Proceed with caution.</b><p>'
			                    'Select the Custom List(s) to remove:')
			self.win_title = 'Delete Custom Lists'
			self.submitButton.setText('Delete')

		elif self.win_type == 'del backups':
			self.label1.setText('Please select the backup files you wish to delete:')
			self.win_title = 'Delete backups'
			self.submitButton.setText('Delete')

		else:
			self.label1.setText('Check the code dingus')

		# CBox widgets
		for cbox in self.cbox_list:
			scrollVLayout.addWidget(cbox)

		# Scroll area
		scrollWidget.setLayout(scrollVLayout)
		scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		scrollArea.setFixedHeight(200)
		scrollArea.setFixedWidth(350)
		scrollArea.setWidget(scrollWidget)

		# Layout
		vLayoutMaster.addWidget(self.label1)
		if self.win_type == 'clear selected':
			vLayoutMaster.addWidget(self.drop)
		vLayoutMaster.addSpacing(20)
		if self.win_type == 'clear selected':
			vLayoutMaster.addWidget(self.label2)
		vLayoutMaster.addWidget(scrollArea)
		hLayoutBottom.addWidget(self.backButton)
		hLayoutBottom.addWidget(self.submitButton)
		vLayoutMaster.addLayout(hLayoutBottom)

		# Signals / slots
		self.backButton.clicked.connect(self.close)
		self.submitButton.clicked.connect(self.accept)

		# Widget
		self.setLayout(vLayoutMaster)
		self.setFixedSize(self.sizeHint())
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle(self.win_title)
		self.show()

	def get_checked_boxes(self):
		out_list = [cbox.text() for cbox in self.cbox_list if cbox.isChecked()]
		return out_list
