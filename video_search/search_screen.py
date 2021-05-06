import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import sqlite3

from amvtracker.misc_files import common_vars


class VideoSearch(QtWidgets.QMainWindow):
	def __init__(self):
		super(VideoSearch, self).__init__()

		# Initialize layouts
		vLayoutMaster = QtWidgets.QVBoxLayout()
		vLayout1 = QtWidgets.QVBoxLayout()
		vLayout2 = QtWidgets.QVBoxLayout()
		hLayout = QtWidgets.QHBoxLayout()
		hLayout2 = QtWidgets.QHBoxLayout()

		# Connection to SQLite databases
		self.subDB_conn = sqlite3.connect(common_vars.video_db())
		self.subDB_cursor = self.subDB_conn.cursor()

		# Left partition - Basic search functions
		self.dropdownItems = ['Show all','Primary editor username', 'Studio', 'Release date', 'Star rating',
		                      'Video footage used', 'Song artist', 'Song genre', 'Video length', 'Contests entered',
		                      'Awards won', 'My rating', 'Favorite', 'Tags', 'URL', 'Local file']
		self.searchDropdown = QtWidgets.QComboBox()
		self.searchDropdown.setFixedWidth(170)
		for i in self.dropdownItems:
			self.searchDropdown.addItem(i)

		# Layouts
		vLayout1.addWidget(self.searchDropdown)
		hLayout.addLayout(vLayout1)
		vLayoutMaster.addLayout(hLayout)

		# Signals/slots

		# Widget
		self.searchScreenWid = QtWidgets.QWidget()
		self.searchScreenWid.setLayout(vLayoutMaster)
		self.setCentralWidget(self.searchScreenWid)
		self.setWindowTitle('Find videos')
		self.setFixedSize(500, 500)
		self.show()