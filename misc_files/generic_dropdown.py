import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore


class DropdownWindow(QtWidgets.QDialog):
	def __init__(self, inp_str, inp_list, win_title):
		super(DropdownWindow, self).__init__()

		self.inp_str = inp_str
		self.inp_list = inp_list
		self.win_title = win_title

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayout = QtWidgets.QHBoxLayout()

		self.label = QtWidgets.QLabel()
		self.label.setText(self.inp_str)

		self.dropdown = QtWidgets.QComboBox()
		self.dropdown.setFixedWidth(150)
		for item in self.inp_list:
			self.dropdown.addItem(item)

		self.closeButton = QtWidgets.QPushButton('Close')
		self.closeButton.setFixedWidth(80)

		self.selButton = QtWidgets.QPushButton('Select')
		self.selButton.setFixedWidth(80)

		# Layouts
		self.vLayoutMaster.addWidget(self.label)
		self.vLayoutMaster.addSpacing(10)
		self.vLayoutMaster.addWidget(self.dropdown)
		self.vLayoutMaster.addSpacing(10)
		self.hLayout.addWidget(self.closeButton)
		self.hLayout.addWidget(self.selButton)
		self.vLayoutMaster.addLayout(self.hLayout)

		# Signals / slots
		self.closeButton.clicked.connect(self.close)
		self.selButton.clicked.connect(self.accept)

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setWindowTitle(self.win_title)
		self.setFixedSize(self.sizeHint())
		self.setMinimumWidth(180)
		self.show()
