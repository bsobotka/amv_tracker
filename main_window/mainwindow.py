import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import sqlite3

from os import getcwd
from misc_files import common_vars
from settings import settings_window
from video_entry import entry_screen


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()

		# SQLite connections
		settings_conn = sqlite3.connect(common_vars.settings_db())
		settings_cursor = settings_conn.cursor()
		video_db_conn = sqlite3.connect(common_vars.video_db())
		video_db_cursor = video_db_conn.cursor()

		# Misc variables
		leftWidth = 270
		rightWidth = 270
		settings_cursor.execute('SELECT path_to_db FROM db_settings')
		currentWorkingDB = settings_cursor.fetchone()[0]

		# Layout initialization
		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayoutTopBar = QtWidgets.QHBoxLayout()
		self.hLayoutTopBar_L = QtWidgets.QHBoxLayout()
		self.hLayoutTopBar_L.setAlignment(QtCore.Qt.AlignLeft)
		self.hLayoutTopBar_Ctr = QtWidgets.QHBoxLayout()
		self.hLayoutTopBar_R = QtWidgets.QHBoxLayout()
		self.hLayoutTopBar_R.setAlignment(QtCore.Qt.AlignRight)

		self.hLayoutCenter = QtWidgets.QHBoxLayout()
		self.vLayoutLeftBar = QtWidgets.QVBoxLayout()
		self.gridRightBar = QtWidgets.QGridLayout()

		# Top bar - L
		self.boldFont = QtGui.QFont()
		self.boldFont.setBold(True)
		self.boldFont.setPixelSize(20)
		self.addVideoBtn = QtWidgets.QPushButton('+')
		self.addVideoBtn.setFont(self.boldFont)
		self.addVideoBtn.setFixedSize(40, 40)
		self.addVideoBtn.setToolTip('Add new video to database')

		self.custListIcon = QtGui.QIcon(getcwd() + '/icons/cl-icon.png')
		self.custListBtn = QtWidgets.QPushButton()
		self.custListBtn.setFixedSize(40, 40)
		self.custListBtn.setIcon(self.custListIcon)
		self.custListBtn.setToolTip('Manage custom lists')

		# Top bar - R
		self.settingsIcon = QtGui.QIcon(getcwd() + '/icons/settings-icon.png')
		self.settingsBtn = QtWidgets.QPushButton()
		self.settingsBtn.setFixedSize(40, 40)
		self.settingsBtn.setIcon(self.settingsIcon)
		self.settingsBtn.setToolTip('AMV Tracker settings')

		self.statsIcon = QtGui.QIcon(getcwd() + '/icons/stats-icon.png')
		self.statsBtn = QtWidgets.QPushButton()
		self.statsBtn.setFixedSize(40, 40)
		self.statsBtn.setIcon(self.statsIcon)
		self.statsBtn.setToolTip('Database stats and analytics')

		self.updateBtn = QtWidgets.QPushButton(u'\u2191')
		self.updateBtn.setFont(self.boldFont)
		self.updateBtn.setFixedSize(40, 40)
		self.updateBtn.setToolTip('Check for update')

		# Mid: left bar
		self.scrollWidget_L = QtWidgets.QWidget()
		self.scrollArea_L = QtWidgets.QScrollArea()
		self.scrollArea_L.setFixedWidth(leftWidth)

		self.largeFont = QtGui.QFont()
		self.largeFont.setPixelSize(14)

		self.groupSearchList = ['Studio', 'Year released', 'Star rating', 'Video footage', 'Song artist', 'Song genre',
		                        'Video length', 'My rating', 'Notable videos', 'Favorited videos',
		                        'Date added to database', 'Custom list']
		self.groupSearchList.sort()
		self.groupSearchList.insert(0, 'Sub-db')
		self.groupSearchDrop = QtWidgets.QComboBox()
		for item in self.groupSearchList:
			self.groupSearchDrop.addItem(item)
		self.groupSearchDrop.setFixedWidth(250)
		self.groupSearchDrop.setFont(self.largeFont)
		
		self.vLayoutLeftBar.addWidget(self.groupSearchDrop)

		# Mid: center
		self.searchTable = QtWidgets.QTableWidget()

		# Mid: right bar
		self.scrollWidget_R = QtWidgets.QWidget()
		self.scrollArea_R = QtWidgets.QScrollArea()
		self.scrollArea_R.setFixedWidth(rightWidth)

		# Bottom bar
		self.cwdLabel = QtWidgets.QLabel()
		self.cwdLabel.setText('Current working database: ' + currentWorkingDB)

		# Top layout size restriction
		self.leftWidget = QtWidgets.QWidget()
		self.leftWidget.setLayout(self.hLayoutTopBar_L)
		self.leftWidget.setFixedWidth(leftWidth)

		self.rightWidget = QtWidgets.QWidget()
		self.rightWidget.setLayout(self.hLayoutTopBar_R)
		self.rightWidget.setFixedWidth(rightWidth)

		# Set layouts
		self.hLayoutTopBar_L.addWidget(self.addVideoBtn, alignment=QtCore.Qt.AlignLeft)
		self.hLayoutTopBar_L.addWidget(self.custListBtn, alignment=QtCore.Qt.AlignLeft)
		self.hLayoutTopBar_R.addWidget(self.settingsBtn, alignment=QtCore.Qt.AlignRight)
		self.hLayoutTopBar_R.addWidget(self.statsBtn, alignment=QtCore.Qt.AlignRight)
		self.hLayoutTopBar_R.addWidget(self.updateBtn, alignment=QtCore.Qt.AlignRight)
		self.hLayoutTopBar.addWidget(self.leftWidget, alignment=QtCore.Qt.AlignLeft)
		self.hLayoutTopBar.addLayout(self.hLayoutTopBar_Ctr)
		self.hLayoutTopBar.addWidget(self.rightWidget, alignment=QtCore.Qt.AlignRight)

		self.scrollWidget_L.setLayout(self.vLayoutLeftBar)
		self.scrollArea_L.setWidget(self.scrollWidget_L)
		self.scrollWidget_R.setLayout(self.gridRightBar)
		self.scrollArea_R.setWidget(self.scrollWidget_R)

		self.hLayoutCenter.addWidget(self.scrollArea_L, alignment=QtCore.Qt.AlignLeft)
		self.hLayoutCenter.addWidget(self.searchTable)
		self.hLayoutCenter.addWidget(self.scrollArea_R, alignment=QtCore.Qt.AlignRight)

		self.vLayoutMaster.addLayout(self.hLayoutTopBar)
		self.vLayoutMaster.addLayout(self.hLayoutCenter)
		self.vLayoutMaster.addWidget(self.cwdLabel, alignment=QtCore.Qt.AlignRight)

		# Signals / slots
		self.addVideoBtn.clicked.connect(self.add_video_pushed)
		self.settingsBtn.clicked.connect(self.settings_button_pushed)

		# Widget
		self.mainWid = QtWidgets.QWidget()
		self.mainWid.setLayout(self.vLayoutMaster)
		self.setCentralWidget(self.mainWid)
		self.setWindowTitle('AMV Tracker')

	def add_video_pushed(self):
		self.add_video = entry_screen.VideoEntry()
		self.add_video.show()

	def settings_button_pushed(self):
		self.settings_screen = settings_window.SettingsWindow()
		self.settings_screen.show()