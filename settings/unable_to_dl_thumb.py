import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

from os import getcwd

from misc_files import common_vars


class UndownloadedThumbsWin(QtWidgets.QDialog):
	def __init__(self, inp_dict):
		super(UndownloadedThumbsWin, self).__init__()

		self.inp_dict = inp_dict
		self.labelString = ''
		for k, v in self.inp_dict.items():
			if v:
				self.labelString += '<b>{}:</b><br><br>'.format(common_vars.sub_db_lookup(reverse=True)[k])
				for vid in v:
					self.labelString += '{}<br>'.format(vid)
				
				self.labelString += '<br>'

		self.scrollWidget = QtWidgets.QWidget()
		self.scrollArea = QtWidgets.QScrollArea()
		
		self.vLayoutScroll = QtWidgets.QVBoxLayout()
		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.label = QtWidgets.QLabel()
		self.label.setText(self.labelString)
		
		self.okButton = QtWidgets.QPushButton('OK')
		
		# Layouts
		self.scrollWidget.setLayout(self.vLayoutMaster)
		self.scrollArea.setWidget(self.scrollWidget)
		self.vLayoutScroll.addWidget(self.scrollArea)
		self.vLayoutScroll.addWidget(self.label)
		self.vLayoutMaster.addLayout(self.vLayoutScroll)
		self.vLayoutMaster.addSpacing(10)
		self.vLayoutMaster.addWidget(self.okButton)

		# Signals / slots
		self.okButton.clicked.connect(self.accept)

		# Widget
		self.wid = QtWidgets.QWidget()
		self.wid.setLayout(self.vLayoutMaster)
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Thumbs not downloaded')
		self.setFixedSize(200, 300)
		self.wid.show()
