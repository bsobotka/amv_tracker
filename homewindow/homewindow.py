import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from os import getcwd

from misc_files import common_vars, check_for_db
from settings import settings_window
from video_entry import entry_screen
from video_search import search_screen


class HomeWindow(QtWidgets.QMainWindow):
	"""
	test
	"""

	def __init__(self, first_load=False):
		# TODO: Check on startup that .db file still exists -- if not prompt user to locate .db file
		super(HomeWindow, self).__init__()
		check_for_db.check_for_db()
		self.setFixedSize(self.sizeHint())

		self.cwd = getcwd()
		self.settingsIcon = QtGui.QIcon(self.cwd + '/icons/settings-icon.png')

		vLayoutMaster = QtWidgets.QVBoxLayout()
		vLayout1 = QtWidgets.QVBoxLayout()
		vLayout2 = QtWidgets.QVBoxLayout()
		hLayout1 = QtWidgets.QHBoxLayout()
		hLayout2 = QtWidgets.QHBoxLayout()
		hLayout3 = QtWidgets.QHBoxLayout()
		hLayoutTop = QtWidgets.QHBoxLayout()

		self.boldFont = QtGui.QFont()
		self.boldFont.setBold(True)

		self.settingsButton = QtWidgets.QPushButton()
		self.settingsButton.setFixedSize(23, 23)
		self.settingsButton.setIcon(self.settingsIcon)

		self.checkForUpdate = QtWidgets.QPushButton(u"\u2191")
		self.checkForUpdate.setFixedWidth(20)
		self.checkForUpdate.setToolTip('Check for update')
		self.checkForUpdate.setFont(self.boldFont)

		self.tutBox = QtWidgets.QPushButton('?')
		self.tutBox.setFont(self.boldFont)
		self.tutBox.setToolTip('How to use this program')
		self.tutBox.setFixedWidth(20)

		self.currentVersion = '1.3.0a'

		self.labelFont = QtGui.QFont("Arial", 8)
		self.versionLabel = QtWidgets.QLabel()
		self.versionLabel.setText("AMV Tracker v" + self.currentVersion)
		self.versionLabel.setFont(self.labelFont)

		# self.dbFileName = global_vars.global_vars().replace('/', '\\').split('\\')[-1]
		# self.workingDBLabel = QtWidgets.QLabel()
		# if len(self.dbFileName) < 36:
		#	self.workingDBLabel.setText('Working database: ' + self.dbFileName)
		# else:
		#	self.workingDBLabel.setText('Working database: ' + self.dbFileName[:20] + '...' + self.dbFileName[-10:])

		self.spacer = QtWidgets.QLabel()
		self.spacer2 = QtWidgets.QLabel()
		self.spacer3 = QtWidgets.QLabel()
		self.spacer2.setMaximumHeight(5)

		self.searchButton = QtWidgets.QPushButton("Search the\nDatabase")
		self.searchButton.setFixedSize(150, 110)

		self.custListBtn = QtWidgets.QPushButton('Custom Lists')
		self.custListBtn.setFixedSize(150, 65)

		self.freeEntryButton = QtWidgets.QPushButton("Enter video")
		self.freeEntryButton.setFixedSize(150, 140)

		self.addFromFolder = QtWidgets.QPushButton('Add from folder')
		self.addFromFolder.setFixedSize(150, 29)

		self.statsButton = QtWidgets.QPushButton('DB\nStatistics')
		self.statsButton.setFixedSize(95, 40)

		self.amvNotepad = QtWidgets.QPushButton('AMV\nNotepad')
		self.amvNotepad.setFixedSize(95, 40)

		self.spreadManage = QtWidgets.QPushButton("DB\nManagement")
		self.spreadManage.setFixedSize(95, 40)

		self.quitButton = QtWidgets.QPushButton("Quit")

		vLayout1.addWidget(self.freeEntryButton)
		vLayout1.addWidget(self.addFromFolder)

		vLayout2.addWidget(self.searchButton)
		vLayout2.addWidget(self.custListBtn)

		hLayoutTop.addWidget(self.versionLabel)
		hLayoutTop.addWidget(self.settingsButton)
		hLayoutTop.addWidget(self.checkForUpdate)
		hLayoutTop.addWidget(self.tutBox)
		vLayoutMaster.addLayout(hLayoutTop)
		# vLayoutMaster.addWidget(self.workingDBLabel)
		vLayoutMaster.addWidget(self.spacer)
		hLayout1.addLayout(vLayout2)
		hLayout1.addLayout(vLayout1)
		hLayout2.addWidget(self.quitButton)
		hLayout3.addWidget(self.statsButton)
		hLayout3.addWidget(self.spreadManage)
		hLayout3.addWidget(self.amvNotepad)
		vLayoutMaster.addLayout(hLayout1)
		vLayoutMaster.addWidget(self.spacer2)
		vLayoutMaster.addLayout(hLayout3)
		vLayoutMaster.addWidget(self.spacer3)
		vLayoutMaster.addLayout(hLayout2)

		# Tooltips
		self.freeEntryButton.setToolTip('Enter a video without any checks on data entered. Only the\n'
		                                '"Editor username" and "Video title" fields are required.\n'
		                                'Choose this option if you just want to enter only the data\n'
		                                'you care most about on each video.')

		self.addFromFolder.setToolTip('This option will allow you to select a folder of AMVs on your hard\n'
		                              'drive, and will provide a list of the videos in that folder. You can\n'
		                              'then click on each one to pull up a video entry window with the\n'
		                              '"Local file" field automatically populated with that video\'s file\n'
		                              'location.')

		self.custListBtn.setToolTip('View and edit your Custom Lists.')

		self.statsButton.setToolTip('Here you\'ll find many different ways to slice and visualize\n'
		                            'the data in your database. PLEASE NOTE: These functions\n'
		                            'work best when you are entering all data (i.e. release date,\n'
		                            'anime, video length, tags, etc.) for every video.')

		self.spreadManage.setToolTip('Various options for managing your database(s) and the\n'
		                             'data contained within.')

		self.amvNotepad.setToolTip('A tool for organizing ideas you have for editing your own AMVs.')

		# Signals / slots
		self.settingsButton.clicked.connect(self.settings_window)
		# self.checkForUpdate.clicked.connect(self.check_for_update)
		# self.tutBox.clicked.connect(self.tutorials_btn_clicked)
		self.searchButton.clicked.connect(self.search_button_clicked)
		# self.custListBtn.clicked.connect(self.cust_lists_clicked)
		# self.gpEntryButton.clicked.connect(lambda: self.data_entry_window(False))
		self.freeEntryButton.clicked.connect(self.data_entry_window)
		# self.addFromFolder.clicked.connect(self.add_by_folder)
		# self.statsButton.clicked.connect(self.stats_clicked)
		# self.amvNotepad.clicked.connect(self.amv_notepad_clicked)
		# self.spreadManage.clicked.connect(self.ss_management)
		self.quitButton.clicked.connect(self.close)

		# Widget
		self.homeWid = QtWidgets.QWidget()
		self.homeWid.setLayout(vLayoutMaster)
		self.setCentralWidget(self.homeWid)
		self.setWindowTitle("AMV Tracker")
		self.homeWid.show()

	def settings_window(self):
		self.settings = settings_window.SettingsWindow()
		self.settings.show()

	def search_button_clicked(self):
		self.search_window = search_screen.VideoSearch()
		self.search_window.show()

	def data_entry_window(self):
		self.data_entry = entry_screen.VideoEntry()
		self.data_entry.show()
