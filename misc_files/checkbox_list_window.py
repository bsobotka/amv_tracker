import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore


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
		self.submitButton = QtWidgets.QPushButton()

		if self.win_type == 'del sub db':
			self.label1.setText('<b>PLEASE NOTE: Deleting a sub-DB removes all</b><br>'
			                    '<b>video entries in it and cannot be undone.</b><br>'
			                    '<b>Proceed with caution.</b><p>Select the sub-DB(s) to delete:')
			self.win_title = 'Delete sub-DBs'
			self.submitButton.setText('Delete')

		elif self.win_type == 'clear all':
			self.label1.setText('<b>PLEASE NOTE: <u>All</u> data will be removed</b><br>'
			                    '<b>from the selected sub-DBs, and this</b><br>'
			                    '<b>cannot be undone. Proceed with caution.</b><p>Select the sub-DB(s) to clear:')
			self.win_title = 'Clear all data'
			self.submitButton.setText('Clear')

		elif self.win_type == 'clear selected':
			self.label1.setText('<b>PLEASE NOTE: All data will be removed</b><br>'
			                    '<b>from the chosen field(s) in the selected</b><br>'
			                    '<b>sub-DB. This cannot be undone. Proceed</b><br>'
			                    '<b>with caution.</b><p>Select the sub-DB to clear:')
			self.label2.setText('Select the field(s) to clear:')
			self.win_title = 'Clear selected data'
			self.submitButton.setText('Clear')

			for subdb in self.drop_list:
				self.drop.addItem(subdb)

		else:
			self.label1.setText('Check the code dingus')

		# CBox widgets
		for cbox in self.cbox_list:
			scrollVLayout.addWidget(cbox)

		# Scroll area
		scrollWidget.setLayout(scrollVLayout)
		scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		scrollArea.setFixedHeight(200)
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
		self.setWindowTitle(self.win_title)
		self.show()

	def get_checked_boxes(self):
		out_list = [cbox.text() for cbox in self.cbox_list if cbox.isChecked()]
		return out_list
