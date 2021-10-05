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

		self.subDBLabel = QtWidgets.QLabel()
		self.subDBLabel.setText('Sub-DB:')
		self.subDBLabel.setFont(self.largeFont)
		self.subDBList = [k for k, v in common_vars.sub_db_lookup().items()]
		self.subDBDrop = QtWidgets.QComboBox()
		self.subDBDrop.setFont(self.largeFont)
		for subdb in self.subDBList:
			self.subDBDrop.addItem(subdb)

		self.basicFiltersLabel = QtWidgets.QLabel()
		self.basicFiltersLabel.setText('Filter by:')
		self.basicFiltersLabel.setFont(self.largeFont)
		self.basicFiltersList = ['Studio', 'Year released', 'Star rating', 'Video footage', 'Song artist', 'Song genre',
		                        'Video length', 'My rating', 'Notable videos', 'Favorited videos',
		                        'Date added to database', 'Custom list']
		self.basicFiltersList.sort()
		self.basicFiltersList.insert(0, 'Show all')
		self.basicFiltersDrop = QtWidgets.QComboBox()
		for item in self.basicFiltersList:
			self.basicFiltersDrop.addItem(item)
		self.basicFiltersDrop.setFixedWidth(230)
		self.basicFiltersDrop.setFont(self.largeFont)

		self.basicFilterListWid = QtWidgets.QListWidget()
		self.basicFilterListWid.setFixedSize(230, 700)

		self.vLayoutLeftBar.addWidget(self.subDBLabel)
		self.vLayoutLeftBar.addWidget(self.subDBDrop)
		self.vLayoutLeftBar.addSpacing(15)
		self.vLayoutLeftBar.addWidget(self.basicFiltersLabel)
		self.vLayoutLeftBar.addWidget(self.basicFiltersDrop)
		self.vLayoutLeftBar.addWidget(self.basicFilterListWid)

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
		self.subDBDrop.currentIndexChanged.connect(self.basic_filter_dropdown_clicked)
		self.basicFiltersDrop.currentIndexChanged.connect(self.basic_filter_dropdown_clicked)

		# Widget
		self.mainWid = QtWidgets.QWidget()
		self.mainWid.setLayout(self.vLayoutMaster)
		self.setCentralWidget(self.mainWid)
		self.setWindowTitle('AMV Tracker')

		video_db_conn.close()
		settings_conn.close()

	def add_video_pushed(self):
		self.add_video = entry_screen.VideoEntry()
		self.add_video.show()

	def settings_button_pushed(self):
		self.settings_screen = settings_window.SettingsWindow()
		self.settings_screen.show()

	def basic_filter_dropdown_clicked(self):
		self.basicFilterListWid.clear()

		bf_conn = sqlite3.connect(common_vars.video_db())
		bf_cursor = bf_conn.cursor()

		sub_db_friendly = self.subDBDrop.currentText()
		sub_db_internal = common_vars.sub_db_lookup()[sub_db_friendly]
		filter_text = self.basicFiltersDrop.currentText()

		if filter_text == 'Show all':
			list_wid_pop = []
		elif filter_text == 'Custom list':
			list_wid_pop = [k for k, v in common_vars.custom_list_lookup().items()]
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Date added to database':
			list_wid_pop = ['Today', 'Yesterday', 'Last 7 days', 'Last 30 days', 'Last 60 days', 'Last 90 days',
			                'Last 6 months', 'Last 12 months', 'Last 24 months']

		elif filter_text == 'Year released':
			bf_cursor.execute('SELECT release_date FROM {}'.format(sub_db_internal))
			dates = bf_cursor.fetchall()
			list_wid_pop = list(set([y[:4] for x in dates for y in x]))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort()

		elif filter_text == 'Favorited videos':
			list_wid_pop = ['Marked as favorite', 'Not marked as favorite']

		elif filter_text == 'My rating':
			list_wid_pop = [str(rat * 0.5) for rat in range(0, 21)]
			list_wid_pop.insert(0, 'Unrated')

		elif filter_text == 'Notable videos':
			list_wid_pop = ['Marked as notable', 'Not marked as notable']

		elif filter_text == 'Song artist':
			bf_cursor.execute('SELECT song_artist FROM {}'.format(sub_db_internal))
			artists = bf_cursor.fetchall()
			list_wid_pop = list(set(y for x in artists for y in x))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Song genre':
			bf_cursor.execute('SELECT song_genre FROM {}'.format(sub_db_internal))
			song_genres = bf_cursor.fetchall()
			list_wid_pop = list(set(y for x in song_genres for y in x))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Star rating':
			list_wid_pop = ['Unrated', '0.00 - 1.99', '2.00 - 2.49', '2.50 - 2.99', '3.00 - 3.49', '3.50 - 3.99',
			                '4.00 - 4.49', '4.50+']

		elif filter_text == 'Studio':
			bf_cursor.execute('SELECT studio FROM {}'.format(sub_db_internal))
			studios = bf_cursor.fetchall()
			list_wid_pop = list(set(y for x in studios for y in x))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Video footage':
			#TODO: Add video source filter logic
			list_wid_pop = []

		elif filter_text == 'Video length':
			list_wid_pop = [str(x * 30) + ' - ' + str(((x + 1) * 30) - 1) + ' sec' for x in range(0, 14)]
			list_wid_pop.append('420+ sec')
			list_wid_pop.insert(0, 'Not specified')

		else:
			list_wid_pop = []

		for item in list_wid_pop:
			self.basicFilterListWid.addItem(item)