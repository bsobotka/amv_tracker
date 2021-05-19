import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import sqlite3
import itertools

from datetime import datetime
from random import randint

from video_entry import addl_editors, update_video_entry
from misc_files import common_vars, tag_checkboxes


class VideoEntry(QtWidgets.QMainWindow):
	def __init__(self, edit_entry=False, vidid=None):
		"""
		xxx
		"""
		super(VideoEntry, self).__init__()
		self.edit_entry = edit_entry
		self.vidid = vidid

		# Connection to SQLite databases
		self.settings_conn = sqlite3.connect(common_vars.settings_db())
		self.settings_cursor = self.settings_conn.cursor()

		self.subDB_conn = sqlite3.connect(common_vars.video_db())
		self.subDB_cursor = self.subDB_conn.cursor()
		self.subDB_int_name_list = [val for key, val in common_vars.video_table_lookup().items()]

		self.tag_conn = sqlite3.connect(common_vars.tag_db())
		self.tag_cursor = self.tag_conn.cursor()

		self.tag_list_names = [tags[1] for tags in self.tag_conn.execute('SELECT * FROM tags_lookup')]
		self.tags1_lookup = [row for row in self.tag_conn.execute('SELECT * FROM tags_1')]

		# Initialize settings dict
		self.entry_settings = {}
		self.settings_cursor.execute('SELECT * FROM entry_settings')
		self.entry_settings_list = self.settings_cursor.fetchall()
		for pair in self.entry_settings_list:
			self.entry_settings[pair[0]] = int(pair[1])

		# Initiate top-level layouts
		self.tabs = QtWidgets.QTabWidget()
		self.tab1 = QtWidgets.QWidget()
		self.tab2 = QtWidgets.QWidget()
		self.tab3 = QtWidgets.QWidget()
		self.tab4 = QtWidgets.QWidget()
		vLayoutMaster = QtWidgets.QVBoxLayout()
		hLayoutMain = QtWidgets.QHBoxLayout()
		hLayoutMain.setAlignment(QtCore.Qt.AlignRight)

		tab1_grid_hLayout = QtWidgets.QHBoxLayout()
		tab3_grid_vLayout = QtWidgets.QVBoxLayout()

		# Back/Submit
		self.backButton = QtWidgets.QPushButton('Back')
		self.backButton.setFixedWidth(120)

		self.submitButton = QtWidgets.QPushButton('Submit')
		self.submitButton.setFixedWidth(120)

		hLayoutMain.addWidget(self.backButton, alignment=QtCore.Qt.AlignRight)
		hLayoutMain.addWidget(self.submitButton, alignment=QtCore.Qt.AlignRight)

		## Tab 1 - Left grid ##
		self.tabs.addTab(self.tab1, 'Video information')
		tab_1_grid_L = QtWidgets.QGridLayout()
		tab_1_grid_L.setAlignment(QtCore.Qt.AlignTop)
		tab_1_grid_L.setColumnMinimumWidth(5, 7)
		grid_1_L_vert_ind = 0

		# Editor 1
		self.editorLabel = QtWidgets.QLabel()
		self.editorLabel.setText('Primary editor\nusername:')
		self.editorBox1 = QtWidgets.QLineEdit()
		self.editorBox1.setFixedWidth(150)

		self.editorNameList = []
		for table in self.subDB_int_name_list:
			self.subDB_cursor.execute('SELECT primary_editor_username FROM {}'.format(table))
			for ed_name in self.subDB_cursor.fetchall():
				self.editorNameList.append(ed_name[0])

		self.editorNameListSorted = list(set(self.editorNameList))
		self.editorNameListSorted.sort(key=lambda x: x.casefold())

		self.editorNameCompleter = QtWidgets.QCompleter(self.editorNameListSorted)
		self.editorNameCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.editorNameCompleter.setMaxVisibleItems(15)
		self.editorBox1.setCompleter(self.editorNameCompleter)

		tab_1_grid_L.addWidget(self.editorLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.editorBox1, grid_1_L_vert_ind, 1, 1, 4)

		grid_1_L_vert_ind += 1

		# Pseudonyms
		self.pseudoLabel = QtWidgets.QLabel()
		self.pseudoLabel.setText('Primary editor\nother username(s):')
		self.pseudoLabel.setToolTip('If the editor goes by or has gone by any other usernames,\n'
		                            'enter them here. Separate multiple usernames with a semi-\n'
		                            'colon + space (ex: username1; username2)')
		self.pseudoBox = QtWidgets.QLineEdit()
		self.pseudoBox.setFixedWidth(150)
		self.pseudoBox.setCompleter(self.editorNameCompleter)

		tab_1_grid_L.addWidget(self.pseudoLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.pseudoBox, grid_1_L_vert_ind, 1, 1, 4)

		grid_1_L_vert_ind += 1

		# Addl editors + MEP text
		self.addlEditorsLabel = QtWidgets.QLabel()
		self.addlEditorsLabel.setText('Addl. editor(s):')
		self.editorBox2 = QtWidgets.QLineEdit()
		self.editorBox2.setFixedWidth(150)

		self.MEPfont = QtGui.QFont()
		self.MEPfont.setUnderline(True)
		self.MEPlabel = QtWidgets.QLabel()
		self.MEPlabel.setText('<font color="blue">2+ editors</font>')
		self.MEPlabel.setFont(self.MEPfont)
		self.MEPlabel.setToolTip('<font color=black>Click to inse'
		                         'rt multiple additional editor '
		                         'usernames.</font>')

		self.editorBox2.setDisabled(True)
		self.MEPlabel.setHidden(True)

		tab_1_grid_L.addWidget(self.addlEditorsLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.editorBox2, grid_1_L_vert_ind, 1, 1, 4)
		tab_1_grid_L.addWidget(self.MEPlabel, grid_1_L_vert_ind, 6, 1, 4)

		grid_1_L_vert_ind += 1

		# Studio
		self.studioLabel = QtWidgets.QLabel()
		self.studioLabel.setText('Studio:')
		self.studioBox = QtWidgets.QLineEdit()
		self.studioBox.setFixedWidth(150)

		self.studioList = []
		for table in self.subDB_int_name_list:
			self.subDB_cursor.execute('SELECT studio FROM {}'.format(table))
			for studio_name in self.subDB_cursor.fetchall():
				if studio_name != '':
					self.studioList.append(studio_name[0])

		self.studioListSorted = list(set(self.studioList))
		self.studioListSorted.sort(key=lambda x: x.casefold())

		self.studioCompleter = QtWidgets.QCompleter(self.studioListSorted)
		self.studioCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.studioCompleter.setMaxVisibleItems(15)
		self.studioBox.setCompleter(self.studioCompleter)

		tab_1_grid_L.addWidget(self.studioLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.studioBox, grid_1_L_vert_ind, 1, 1, 4)

		grid_1_L_vert_ind += 1

		# Spacer
		tab_1_grid_L.setRowMinimumHeight(grid_1_L_vert_ind, 20)
		grid_1_L_vert_ind += 1

		# Video title
		self.titleLabel = QtWidgets.QLabel()
		self.titleLabel.setText('Video title:')
		self.titleBox = QtWidgets.QLineEdit()
		self.titleBox.setFixedWidth(150)

		tab_1_grid_L.addWidget(self.titleLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.titleBox, grid_1_L_vert_ind, 1, 1, 4)

		grid_1_L_vert_ind += 1

		# Release date
		self.dateLabel = QtWidgets.QLabel()
		self.dateLabel.setText('Release date:')
		self.dateYear = QtWidgets.QComboBox()
		self.dateYear.setFixedWidth(70)
		self.dateMonth = QtWidgets.QComboBox()
		self.dateMonth.setFixedWidth(70)
		self.dateMonth.setDisabled(True)
		self.dateDay = QtWidgets.QComboBox()
		self.dateDay.setFixedWidth(40)
		self.dateDay.setDisabled(True)
		self.dateUnk = QtWidgets.QCheckBox('Date unknown')

		self.monthDict = {"01 (Jan)": 1,
		                  "02 (Feb)": 2,
		                  "03 (Mar)": 3,
		                  "04 (Apr)": 4,
		                  "05 (May)": 5,
		                  "06 (Jun)": 6,
		                  "07 (Jul)": 7,
		                  "08 (Aug)": 8,
		                  "09 (Sep)": 9,
		                  "10 (Oct)": 10,
		                  "11 (Nov)": 11,
		                  "12 (Dec)": 12}

		self.monthList = [key for key, val in iter(self.monthDict.items())]
		self.monthList.sort()
		self.monthList.insert(0, '')

		for month in self.monthList:
			self.dateMonth.addItem(month)

		self.yearList = [yr for yr in range(common_vars.year_plus_one(), 1981, -1)]
		self.yearList.sort()
		self.yearList.reverse()
		self.yearList.insert(0, '')

		for year in self.yearList:
			self.dateYear.addItem(str(year))

		self.dateMonth.setMaxVisibleItems(13)
		self.dateYear.setMaxVisibleItems(20)

		tab_1_grid_L.addWidget(self.dateLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.dateYear, grid_1_L_vert_ind, 1, 1, 2)
		tab_1_grid_L.addWidget(self.dateMonth, grid_1_L_vert_ind, 3, 1, 2)
		tab_1_grid_L.addWidget(self.dateDay, grid_1_L_vert_ind, 5, 1, 2)
		tab_1_grid_L.addWidget(self.dateUnk, grid_1_L_vert_ind, 7, 1, 4)

		grid_1_L_vert_ind += 1

		# Star rating
		self.starRatingLabel = QtWidgets.QLabel()
		self.starRatingLabel.setText('Star rating:')
		self.starRatingBox = QtWidgets.QLineEdit()

		self.starRatingBox.setFixedWidth(50)

		tab_1_grid_L.addWidget(self.starRatingLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.starRatingBox, grid_1_L_vert_ind, 1, 1, 2)

		grid_1_L_vert_ind += 1

		# Video Footage 1
		self.videoFootageLabel = QtWidgets.QLabel()
		self.videoFootageLabel.setText('Video footage used:')
		self.videoFootageBox1 = QtWidgets.QTextEdit()
		self.videoFootageBox1.setFixedSize(150, 120)
		self.videoFootageBox1.setPlaceholderText('Enter one video source per line...\n\n'
		                                         '...or search for video sources already entered into AMV Tracker '
		                                         'using search tool on right                -->')
		self.videoFootageBox1.installEventFilter(self)

		self.videoSearchBox = QtWidgets.QLineEdit()
		self.videoSearchBox.setFixedWidth(100)
		self.videoSearchBox.setPlaceholderText('Search...')

		tab_1_grid_L.addWidget(self.videoFootageLabel, grid_1_L_vert_ind, 0, alignment=QtCore.Qt.AlignTop)
		tab_1_grid_L.addWidget(self.videoFootageBox1, grid_1_L_vert_ind, 1, 3, 4)
		tab_1_grid_L.addWidget(self.videoSearchBox, grid_1_L_vert_ind, 6, 1, 3, alignment=QtCore.Qt.AlignTop)

		grid_1_L_vert_ind += 1

		# Video footage list
		self.videoFootageList = QtWidgets.QListWidget()
		self.videoFootageList.setFixedSize(140, 70)
		self.ftg_list = []
		for table in self.subDB_int_name_list:
			self.subDB_cursor.execute('SELECT video_footage FROM {}'.format(table))

			for ftg in self.subDB_cursor.fetchall():
				ftg_split = ftg[0].split('; ')

				for ind_ftg in ftg_split:
					if ind_ftg != '' and ind_ftg not in self.ftg_list:
						self.ftg_list.append(ind_ftg)

		self.ftg_list_sorted = []
		marker = set()
		for l in self.ftg_list:
			ll = l.lower()
			if ll not in marker:
				marker.add(ll)
				self.ftg_list_sorted.append(l)

		self.ftg_list_sorted.sort(key=lambda x: x.casefold())

		for f in self.ftg_list_sorted:
			self.videoFootageList.addItem(f)

		tab_1_grid_L.addWidget(self.videoFootageList, grid_1_L_vert_ind, 6, 1, 3, alignment=QtCore.Qt.AlignTop)

		grid_1_L_vert_ind += 1

		# Add video footage
		self.addFootage = QtWidgets.QPushButton('<<')
		self.addFootage.setFixedSize(30, 20)
		self.addFootage.setToolTip('Add to video footage list')

		tab_1_grid_L.addWidget(self.addFootage, grid_1_L_vert_ind, 6, 1, 2, alignment=QtCore.Qt.AlignLeft)

		grid_1_L_vert_ind += 1

		"""# Video Footage 2
		self.videoFootageBox2 = QtWidgets.QLineEdit()
		self.videoFootageBox2.setFixedWidth(150)

		tab_1_grid_L.addWidget(self.videoFootageBox2, grid_1_L_vert_ind, 1, 1, 4)

		grid_1_L_vert_ind += 1

		# Video Footage 3
		self.videoFootageBox3 = QtWidgets.QLineEdit()
		self.videoFootageBox3.setFixedWidth(150)

		tab_1_grid_L.addWidget(self.videoFootageBox3, grid_1_L_vert_ind, 1, 1, 4)

		grid_1_L_vert_ind += 1

		# Video Footage 4
		self.videoFootageBox4 = QtWidgets.QLineEdit()
		self.videoFootageBox4.setFixedWidth(150)
		self.videoFootageVarious = QtWidgets.QCheckBox('More than four')

		tab_1_grid_L.addWidget(self.videoFootageBox4, grid_1_L_vert_ind, 1, 1, 4)
		tab_1_grid_L.addWidget(self.videoFootageVarious, grid_1_L_vert_ind, 6, 1, 4)

		grid_1_L_vert_ind += 1"""

		# Spacer
		tab_1_grid_L.setRowMinimumHeight(grid_1_L_vert_ind, 20)
		grid_1_L_vert_ind += 1

		# Artist
		self.artistLabel = QtWidgets.QLabel()
		self.artistLabel.setText('Song artist:')
		self.artistBox = QtWidgets.QLineEdit()
		self.artistBox.setFixedWidth(150)

		self.artistList = []
		for tn in self.subDB_int_name_list:
			self.subDB_cursor.execute('SELECT song_artist FROM {}'.format(tn))
			for artist in self.subDB_cursor.fetchall():
				if artist[0] != '':
					self.artistList.append(artist[0])

		self.artistListSorted = list(set(self.artistList))
		self.artistListSorted.sort(key=lambda x: x.casefold())

		self.artistCompleter = QtWidgets.QCompleter(self.artistListSorted)
		self.artistCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.artistCompleter.setMaxVisibleItems(15)
		self.artistBox.setCompleter(self.artistCompleter)

		tab_1_grid_L.addWidget(self.artistLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.artistBox, grid_1_L_vert_ind, 1, 1, 4)

		grid_1_L_vert_ind += 1

		# Song title
		self.songTitleLabel = QtWidgets.QLabel()
		self.songTitleLabel.setText('Song title:')
		self.songTitleBox = QtWidgets.QLineEdit()
		self.songTitleBox.setFixedWidth(150)

		tab_1_grid_L.addWidget(self.songTitleLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.songTitleBox, grid_1_L_vert_ind, 1, 1, 4)

		grid_1_L_vert_ind += 1

		# Song genre
		self.songGenreLabel = QtWidgets.QLabel()
		self.songGenreLabel.setText('Song genre:')
		self.songGenreBox = QtWidgets.QLineEdit()
		self.songGenreBox.setFixedWidth(100)
		self.songGenreDrop = QtWidgets.QComboBox()
		self.songGenreDrop.setFixedWidth(150)

		self.genreList = []
		for subDB in self.subDB_int_name_list:
			self.subDB_cursor.execute('SELECT song_genre FROM {}'.format(subDB))
			for genre in self.subDB_cursor.fetchall():
				if genre[0].lower() not in self.genreList and genre[0] != '':
					self.genreList.append(genre[0].lower())

		self.genreList.sort(key=lambda x: x.lower())
		self.genreList.insert(0, '')
		for gen in self.genreList:
			self.songGenreDrop.addItem(gen.capitalize())

		tab_1_grid_L.addWidget(self.songGenreLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.songGenreDrop, grid_1_L_vert_ind, 1, 1, 5)
		tab_1_grid_L.addWidget(self.songGenreBox, grid_1_L_vert_ind, 5, 1, 4)

		grid_1_L_vert_ind += 1

		# Video length
		self.lengthLabel = QtWidgets.QLabel()
		self.lengthLabel.setText('Video length:')

		self.lengthMinDrop = QtWidgets.QComboBox()
		self.lengthMinDrop.setFixedWidth(40)
		self.lengthMinDrop.addItem('')
		for minutes in range(0, 100):
			self.lengthMinDrop.addItem(str(minutes))
		self.lengthMinLabel = QtWidgets.QLabel()
		self.lengthMinLabel.setText('min')

		self.lengthSecDrop = QtWidgets.QComboBox()
		self.lengthSecDrop.setFixedWidth(45)
		self.lengthSecDrop.addItem('')
		for seconds in range(0, 60):
			self.lengthSecDrop.addItem(str(seconds))
		self.lengthSecLabel = QtWidgets.QLabel()
		self.lengthSecLabel.setText('sec')

		tab_1_grid_L.addWidget(self.lengthLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.lengthMinDrop, grid_1_L_vert_ind, 1)
		tab_1_grid_L.addWidget(self.lengthMinLabel, grid_1_L_vert_ind, 2)
		tab_1_grid_L.addWidget(self.lengthSecDrop, grid_1_L_vert_ind, 3)
		tab_1_grid_L.addWidget(self.lengthSecLabel, grid_1_L_vert_ind, 4, 1, 2)

		grid_1_L_vert_ind += 1

		## Tab 1 - Right grid ##
		tab_1_grid_R = QtWidgets.QGridLayout()
		tab_1_grid_R.setAlignment(QtCore.Qt.AlignTop)
		grid_1_R_vert_ind = 0

		# Contests
		self.contestLabel = QtWidgets.QLabel()
		self.contestLabel.setText('Contests entered:')
		self.contestBox = QtWidgets.QTextEdit()
		self.contestBox.setFixedSize(200, 80)

		tab_1_grid_R.addWidget(self.contestLabel, grid_1_R_vert_ind, 0, alignment=QtCore.Qt.AlignTop)
		tab_1_grid_R.addWidget(self.contestBox, grid_1_R_vert_ind, 1)

		grid_1_R_vert_ind += 1

		# Awards
		self.awardsLabel = QtWidgets.QLabel()
		self.awardsLabel.setText('Awards won:')
		self.awardsBox = QtWidgets.QTextEdit()
		self.awardsBox.setFixedSize(200, 80)

		tab_1_grid_R.addWidget(self.awardsLabel, grid_1_R_vert_ind, 0, alignment=QtCore.Qt.AlignTop)
		tab_1_grid_R.addWidget(self.awardsBox, grid_1_R_vert_ind, 1)

		grid_1_R_vert_ind += 1

		# Video description
		self.vidDescLabel = QtWidgets.QLabel()
		self.vidDescLabel.setText('Video description:')
		self.vidDescBox = QtWidgets.QTextEdit()
		self.vidDescBox.setFixedSize(200, 260)

		tab_1_grid_R.addWidget(self.vidDescLabel, grid_1_R_vert_ind, 0, alignment=QtCore.Qt.AlignTop)
		tab_1_grid_R.addWidget(self.vidDescBox, grid_1_R_vert_ind, 1)

		## Tab 2 ##
		self.tabs.addTab(self.tab2, 'My rating/tags/comments')
		tab_2_grid = QtWidgets.QGridLayout()
		tab_2_grid.setAlignment(QtCore.Qt.AlignTop)
		grid_2_vert_ind = 0

		# My Rating
		self.myRatingLabel = QtWidgets.QLabel()
		self.myRatingLabel.setText('My rating:')
		self.myRatingDrop = QtWidgets.QComboBox()
		self.myRatingDrop.setFixedWidth(60)
		self.myRatingDrop.setMaxVisibleItems(15)

		myRatingList = [rat * 0.5 for rat in range(0, 21)]

		self.myRatingDrop.addItem('')
		for rating in myRatingList:
			self.myRatingDrop.addItem(str(rating))

		tab_2_grid.addWidget(self.myRatingLabel, grid_2_vert_ind, 0, alignment=QtCore.Qt.AlignCenter)
		tab_2_grid.addWidget(self.myRatingDrop, grid_2_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)

		grid_2_vert_ind += 1

		# Notable checkbox
		self.notableCheck = QtWidgets.QCheckBox('Notable')
		tab_2_grid.addWidget(self.notableCheck, grid_2_vert_ind, 0, alignment=QtCore.Qt.AlignCenter)

		grid_2_vert_ind += 1

		# Favorite checkbox
		self.favCheck = QtWidgets.QCheckBox('Favorite')
		tab_2_grid.addWidget(self.favCheck, grid_2_vert_ind, 0, alignment=QtCore.Qt.AlignCenter)

		grid_2_vert_ind += 1
		tab_2_grid.setRowMinimumHeight(grid_2_vert_ind, 10)
		grid_2_vert_ind += 1

		# Tags 1
		self.tags1Button = QtWidgets.QPushButton(self.tag_list_names[0])
		self.tags1Box = QtWidgets.QLineEdit()
		self.tags1Box.setPlaceholderText('<-- Click to select tags')
		self.tags1Box.setFixedWidth(580)
		self.tags1Box.setReadOnly(True)
		self.tags1X = QtWidgets.QPushButton('X')
		self.tags1X.setFixedWidth(20)

		tab_2_grid.addWidget(self.tags1Button, grid_2_vert_ind, 0)
		tab_2_grid.addWidget(self.tags1Box, grid_2_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags1X, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)

		grid_2_vert_ind += 1

		# Tags 2
		self.tags2Button = QtWidgets.QPushButton(self.tag_list_names[1])
		self.tags2Box = QtWidgets.QLineEdit()
		self.tags2Box.setPlaceholderText('<-- Click to select tags')
		self.tags2Box.setFixedWidth(580)
		self.tags2Box.setReadOnly(True)
		self.tags2X = QtWidgets.QPushButton('X')
		self.tags2X.setFixedWidth(20)

		tab_2_grid.addWidget(self.tags2Button, grid_2_vert_ind, 0)
		tab_2_grid.addWidget(self.tags2Box, grid_2_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags2X, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)

		grid_2_vert_ind += 1

		# Tags 3
		self.tags3Button = QtWidgets.QPushButton(self.tag_list_names[2])
		self.tags3Box = QtWidgets.QLineEdit()
		self.tags3Box.setPlaceholderText('<-- Click to select tags')
		self.tags3Box.setFixedWidth(580)
		self.tags3Box.setReadOnly(True)
		self.tags3X = QtWidgets.QPushButton('X')
		self.tags3X.setFixedWidth(20)

		tab_2_grid.addWidget(self.tags3Button, grid_2_vert_ind, 0)
		tab_2_grid.addWidget(self.tags3Box, grid_2_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags3X, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)

		grid_2_vert_ind += 1

		# Tags 4
		self.tags4Button = QtWidgets.QPushButton(self.tag_list_names[3])
		self.tags4Box = QtWidgets.QLineEdit()
		self.tags4Box.setPlaceholderText('<-- Click to select tags')
		self.tags4Box.setFixedWidth(580)
		self.tags4Box.setReadOnly(True)
		self.tags4X = QtWidgets.QPushButton('X')
		self.tags4X.setFixedWidth(20)

		tab_2_grid.addWidget(self.tags4Button, grid_2_vert_ind, 0)
		tab_2_grid.addWidget(self.tags4Box, grid_2_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags4X, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)

		grid_2_vert_ind += 1

		# Tags 5
		self.tags5Button = QtWidgets.QPushButton(self.tag_list_names[4])
		self.tags5Box = QtWidgets.QLineEdit()
		self.tags5Box.setPlaceholderText('<-- Click to select tags')
		self.tags5Box.setFixedWidth(580)
		self.tags5Box.setReadOnly(True)
		self.tags5X = QtWidgets.QPushButton('X')
		self.tags5X.setFixedWidth(20)

		tab_2_grid.addWidget(self.tags5Button, grid_2_vert_ind, 0)
		tab_2_grid.addWidget(self.tags5Box, grid_2_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags5X, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)

		grid_2_vert_ind += 1

		# Tags 6
		self.tags6Button = QtWidgets.QPushButton(self.tag_list_names[5])
		self.tags6Box = QtWidgets.QLineEdit()
		self.tags6Box.setPlaceholderText('<-- Click to select tags')
		self.tags6Box.setFixedWidth(580)
		self.tags6Box.setReadOnly(True)
		self.tags6X = QtWidgets.QPushButton('X')
		self.tags6X.setFixedWidth(20)

		tab_2_grid.addWidget(self.tags6Button, grid_2_vert_ind, 0)
		tab_2_grid.addWidget(self.tags6Box, grid_2_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags6X, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)

		grid_2_vert_ind += 1

		# Disable tag buttons
		self.tagWidGroups = [[self.tags1Button, self.tags1Box, self.tags1X],
		                     [self.tags2Button, self.tags2Box, self.tags2X],
		                     [self.tags3Button, self.tags3Box, self.tags3X],
		                     [self.tags4Button, self.tags4Box, self.tags4X],
		                     [self.tags5Button, self.tags5Box, self.tags5X],
		                     [self.tags6Button, self.tags6Box, self.tags6X]]

		for ind in range(0, len(self.tagWidGroups)):
			self.tag_cursor.execute('SELECT * FROM tags_{}'.format(ind + 1))
			table_result = self.tag_cursor.fetchone()
			if table_result is None:
				for widg in self.tagWidGroups[ind]:
					self.tagWidGroups[ind][0].setToolTip('<font color=black>There are no tags in this tag group. '
					                                     'Add tags via the AMV Tracker settings menu.</font>')
					self.tagWidGroups[ind][1].setPlaceholderText('')
					widg.setDisabled(True)

		grid_2_vert_ind += 1
		tab_2_grid.setRowMinimumHeight(grid_2_vert_ind, 20)
		grid_2_vert_ind += 1

		# Comments
		self.commentsLabel = QtWidgets.QLabel()
		self.commentsLabel.setText('Comments:')
		self.commentsBox = QtWidgets.QTextEdit()
		self.commentsBox.setFixedSize(670, 180)

		tab_2_grid.addWidget(self.commentsLabel, grid_2_vert_ind, 0, alignment=QtCore.Qt.AlignTop)
		tab_2_grid.addWidget(self.commentsBox, grid_2_vert_ind + 1, 0, 1, 4, alignment=QtCore.Qt.AlignLeft)

		## Tab 3 - Top grid ##
		self.tabs.addTab(self.tab3, 'Sources and URLs')
		tab_3_grid_T = QtWidgets.QGridLayout()
		tab_3_grid_T.setAlignment(QtCore.Qt.AlignLeft)
		tab_3_grid_T.setAlignment(QtCore.Qt.AlignTop)
		grid_3_T_vert_ind = 0

		# Video header
		self.headerFont = QtGui.QFont()
		self.headerFont.setBold(True)
		self.headerFont.setUnderline(True)
		self.headerFont.setPixelSize(14)

		self.videoHeaderLabel = QtWidgets.QLabel()
		self.videoHeaderLabel.setText('Video sources')
		self.videoHeaderLabel.setFont(self.headerFont)

		tab_3_grid_T.addWidget(self.videoHeaderLabel, grid_3_T_vert_ind, 0, 1, 2, alignment=QtCore.Qt.AlignLeft)

		grid_3_T_vert_ind += 1

		# YouTube URL
		self.ytURLLabel = QtWidgets.QLabel()
		self.ytURLLabel.setText('YouTube URL:')
		self.ytURLBox = QtWidgets.QLineEdit()
		self.ytURLBox.setFixedWidth(350)

		tab_3_grid_T.addWidget(self.ytURLLabel, grid_3_T_vert_ind, 0, alignment=QtCore.Qt.AlignTop)
		tab_3_grid_T.addWidget(self.ytURLBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)

		grid_3_T_vert_ind += 1

		# AMV.org URL
		self.amvOrgURLLabel = QtWidgets.QLabel()
		self.amvOrgURLLabel.setText('AMV.org URL:')
		self.amvOrgURLBox = QtWidgets.QLineEdit()
		self.amvOrgURLBox.setFixedWidth(350)

		tab_3_grid_T.addWidget(self.amvOrgURLLabel, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.amvOrgURLBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)

		grid_3_T_vert_ind += 1

		# amvnews URL
		self.amvnewsURLLabel = QtWidgets.QLabel()
		self.amvnewsURLLabel.setText('amvnews URL:')
		self.amvnewsURLBox = QtWidgets.QLineEdit()
		self.amvnewsURLBox.setFixedWidth(350)

		tab_3_grid_T.addWidget(self.amvnewsURLLabel, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.amvnewsURLBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)

		grid_3_T_vert_ind += 1

		# Other URL
		self.otherURLLabel = QtWidgets.QLabel()
		self.otherURLLabel.setText('Other URL:')
		self.otherURLBox = QtWidgets.QLineEdit()
		self.otherURLBox.setFixedWidth(350)

		tab_3_grid_T.addWidget(self.otherURLLabel, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.otherURLBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)

		grid_3_T_vert_ind += 1

		# Local file
		self.localFileButton = QtWidgets.QPushButton('Local file')
		self.localFileButton.setFixedWidth(90)
		self.localFileBox = QtWidgets.QLineEdit()
		self.localFileBox.setFixedWidth(350)
		self.localFileBox.setReadOnly(True)
		self.localFileBox.setPlaceholderText('<-- Click to locate video file')
		self.localFileX = QtWidgets.QPushButton('X')
		self.localFileX.setFixedWidth(20)
		self.localFileWatch = QtWidgets.QPushButton('Watch')
		self.localFileWatch.setFixedWidth(60)

		tab_3_grid_T.addWidget(self.localFileButton, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.localFileBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.localFileX, grid_3_T_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		# tab_3_grid_T.addWidget(self.localFileWatch, grid_3_T_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)

		grid_3_T_vert_ind += 1

		## Tab 3 - Bottom grid ##
		self.tabs.addTab(self.tab3, 'Sources and URLs')
		tab_3_grid_B = QtWidgets.QGridLayout()
		tab_3_grid_B.setAlignment(QtCore.Qt.AlignLeft)
		tab_3_grid_B.setAlignment(QtCore.Qt.AlignTop)
		tab_3_grid_B.setColumnStretch(1, 400)
		grid_3_B_vert_ind = 0

		# Editor channels/profiles
		self.editorHeaderLabel = QtWidgets.QLabel()
		self.editorHeaderLabel.setText('Editor channels/profiles')
		self.editorHeaderLabel.setFont(self.headerFont)

		tab_3_grid_B.addWidget(self.editorHeaderLabel, grid_3_B_vert_ind, 0, 1, 2)

		grid_3_B_vert_ind += 1

		# Editor YT channel
		self.editorYTChannelLabel = QtWidgets.QLabel()
		self.editorYTChannelLabel.setText('Editor YouTube channel URL:')
		self.editorYTChannelBox = QtWidgets.QLineEdit()
		self.editorYTChannelBox.setFixedWidth(350)

		tab_3_grid_B.addWidget(self.editorYTChannelLabel, grid_3_B_vert_ind, 0)
		tab_3_grid_B.addWidget(self.editorYTChannelBox, grid_3_B_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)

		grid_3_B_vert_ind += 1

		# Editor AMV.org profile
		self.editorAMVOrgProfileLabel = QtWidgets.QLabel()
		self.editorAMVOrgProfileLabel.setText('Editor AMV.org profile URL:')
		self.editorAMVOrgProfileBox = QtWidgets.QLineEdit()
		self.editorAMVOrgProfileBox.setFixedWidth(350)

		tab_3_grid_B.addWidget(self.editorAMVOrgProfileLabel, grid_3_B_vert_ind, 0)
		tab_3_grid_B.addWidget(self.editorAMVOrgProfileBox, grid_3_B_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)

		grid_3_B_vert_ind += 1

		# Editor amvnews profile
		self.editorAmvnewsProfileLabel = QtWidgets.QLabel()
		self.editorAmvnewsProfileLabel.setText('Editor amvnews profile URL:')
		self.editorAmvnewsProfileBox = QtWidgets.QLineEdit()
		self.editorAmvnewsProfileBox.setFixedWidth(350)

		tab_3_grid_B.addWidget(self.editorAmvnewsProfileLabel, grid_3_B_vert_ind, 0)
		tab_3_grid_B.addWidget(self.editorAmvnewsProfileBox, grid_3_B_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)

		grid_3_B_vert_ind += 1

		# Editor Other profile
		self.editorOtherProfileLabel = QtWidgets.QLabel()
		self.editorOtherProfileLabel.setText('Other editor profile URL:')
		self.editorOtherProfileBox = QtWidgets.QLineEdit()
		self.editorOtherProfileBox.setFixedWidth(350)

		tab_3_grid_B.addWidget(self.editorOtherProfileLabel, grid_3_B_vert_ind, 0)
		tab_3_grid_B.addWidget(self.editorOtherProfileBox, grid_3_B_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)

		grid_3_B_vert_ind += 1

		## Tab 4 ##
		self.tabs.addTab(self.tab4, 'Submission rules')
		tab_4_vLayoutMaster = QtWidgets.QVBoxLayout()
		tab_4_vLayoutMaster.setAlignment(QtCore.Qt.AlignTop)
		tab_4_vLayout1 = QtWidgets.QVBoxLayout()
		tab_4_vLayout2 = QtWidgets.QVBoxLayout()
		tab_4_vLayout3 = QtWidgets.QVBoxLayout()
		tab_4_hLayout = QtWidgets.QHBoxLayout()
		tab_4_hLayout.setAlignment(QtCore.Qt.AlignLeft)

		tab_4_scrollvLayout1 = QtWidgets.QVBoxLayout()
		tab_4_scrollvLayout2 = QtWidgets.QVBoxLayout()

		# Checks enabled
		self.checksEnabled = QtWidgets.QCheckBox('Checks enabled')
		if self.entry_settings['checks_enabled_default'] == 1:
			self.checksEnabled.setChecked(True)

		tab_4_vLayout1.addWidget(self.checksEnabled, alignment=QtCore.Qt.AlignTop)
		tab_4_vLayout1.addSpacing(30)

		# Add to sub-dbs
		self.addToSubDBLabel = QtWidgets.QLabel()
		self.addToSubDBLabel.setText('Add to following sub-DBs:')
		self.addToSubDBLabel.setFont(self.headerFont)
		tab_4_vLayout2.addWidget(self.addToSubDBLabel, alignment=QtCore.Qt.AlignCenter)

		# List of sub-db checkboxes (in ScrollArea)
		self.subDBSignalMapper = QtCore.QSignalMapper()
		self.subDB_list_ = [x[0] for x in self.subDB_conn.execute('SELECT user_subdb_name FROM db_name_lookup')]
		self.subDB_list = [self.subDB_list_[0]] + [n for n in sorted(self.subDB_list_[1:])]
		self.list_of_subDB_checks = [QtWidgets.QCheckBox(subDB) for subDB in self.subDB_list]
		sub_db_ind = 0
		for check in self.list_of_subDB_checks:
			tab_4_scrollvLayout1.addWidget(check)
			self.subDBSignalMapper.setMapping(check, sub_db_ind)
			if sub_db_ind == 0:
				check.setChecked(True)
			sub_db_ind += 1
			check.clicked.connect(self.subDBSignalMapper.map)

		self.subDBScrollWidget = QtWidgets.QWidget()
		self.subDBScrollArea = QtWidgets.QScrollArea()
		self.subDBScrollWidget.setLayout(tab_4_scrollvLayout1)
		self.subDBScrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.subDBScrollArea.setFixedSize(250, 350)
		self.subDBScrollArea.setWidget(self.subDBScrollWidget)

		# Add to Custom Lists
		self.addtoCustListsLabel = QtWidgets.QLabel()
		self.addtoCustListsLabel.setText('Add to following Custom Lists:')
		self.addtoCustListsLabel.setFont(self.headerFont)
		tab_4_vLayout3.addWidget(self.addtoCustListsLabel, alignment=QtCore.Qt.AlignCenter)

		# List of Custom Lists (in ScrollArea)
		tab_4_scrollvLayout2.addStretch()

		self.subDBScrollWidget2 = QtWidgets.QWidget()
		self.subDBScrollArea2 = QtWidgets.QScrollArea()
		self.subDBScrollWidget2.setLayout(tab_4_scrollvLayout2)
		self.subDBScrollArea2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.subDBScrollArea2.setFixedSize(250, 350)
		self.subDBScrollArea2.setWidget(self.subDBScrollWidget2)

		## Layouts ##
		tab1_grid_hLayout.addLayout(tab_1_grid_L)
		tab1_grid_hLayout.addSpacing(15)
		tab1_grid_hLayout.addLayout(tab_1_grid_R)

		tab3_grid_vLayout.addLayout(tab_3_grid_T)
		tab3_grid_vLayout.addLayout(tab_3_grid_B)

		tab_4_vLayout2.addWidget(self.subDBScrollArea, alignment=QtCore.Qt.AlignTop)
		tab_4_vLayout3.addWidget(self.subDBScrollArea2, alignment=QtCore.Qt.AlignTop)
		tab_4_hLayout.addLayout(tab_4_vLayout2)
		tab_4_hLayout.addSpacing(20)
		tab_4_hLayout.addLayout(tab_4_vLayout3)
		tab_4_vLayoutMaster.addLayout(tab_4_vLayout1)
		tab_4_vLayoutMaster.addLayout(tab_4_hLayout)

		self.tab1.setLayout(tab1_grid_hLayout)
		self.tab2.setLayout(tab_2_grid)
		self.tab3.setLayout(tab3_grid_vLayout)
		self.tab4.setLayout(tab_4_vLayoutMaster)

		vLayoutMaster.addWidget(self.tabs)
		vLayoutMaster.addLayout(hLayoutMain)

		# Signals/slots
		# Tab 1
		self.editorBox1.textChanged.connect(self.editor_1_text_changed)
		self.MEPlabel.mousePressEvent = self.two_plus_editors
		self.dateYear.currentIndexChanged.connect(lambda: self.en_dis_date_boxes(self.dateYear))
		self.dateMonth.currentIndexChanged.connect(lambda: self.en_dis_date_boxes(self.dateMonth))
		self.dateMonth.currentIndexChanged.connect(self.populate_day_dropdown)
		self.dateUnk.clicked.connect(self.date_unknown_checked)
		self.starRatingBox.editingFinished.connect(self.check_star_rating)
		self.videoSearchBox.textChanged.connect(self.search_for_video_ftg)
		self.addFootage.clicked.connect(self.add_video_ftg)
		self.songGenreDrop.currentIndexChanged.connect(self.update_genre_box)

		# Tab 2
		self.tags1Button.clicked.connect(lambda: self.tag_window(self.tags1Button.text(), self.tags1Box))
		self.tags2Button.clicked.connect(lambda: self.tag_window(self.tags2Button.text(), self.tags2Box))
		self.tags3Button.clicked.connect(lambda: self.tag_window(self.tags3Button.text(), self.tags3Box))
		self.tags4Button.clicked.connect(lambda: self.tag_window(self.tags4Button.text(), self.tags4Box))
		self.tags5Button.clicked.connect(lambda: self.tag_window(self.tags5Button.text(), self.tags5Box))
		self.tags6Button.clicked.connect(lambda: self.tag_window(self.tags6Button.text(), self.tags6Box))

		self.tags1X.clicked.connect(self.tags1Box.clear)
		self.tags2X.clicked.connect(self.tags2Box.clear)
		self.tags3X.clicked.connect(self.tags3Box.clear)
		self.tags4X.clicked.connect(self.tags4Box.clear)
		self.tags5X.clicked.connect(self.tags5Box.clear)
		self.tags6X.clicked.connect(self.tags6Box.clear)

		# Tab 3
		self.localFileButton.clicked.connect(self.local_file_clicked)
		self.localFileX.clicked.connect(self.localFileBox.clear)

		# Back / submit
		self.backButton.clicked.connect(self.close)
		self.submitButton.clicked.connect(self.submit_button_clicked)

		## Widget ##
		self.wid = QtWidgets.QWidget()
		self.wid.setLayout(vLayoutMaster)
		self.setCentralWidget(self.wid)
		self.setWindowTitle('Video entry')
		self.setFixedSize(self.sizeHint())
		self.wid.show()

		self.editorBox1.setFocus()

	def editor_1_text_changed(self):
		if self.editorBox1.text() != '':
			self.editorBox2.setEnabled(True)
			self.MEPlabel.setHidden(False)
		else:
			self.editorBox2.setDisabled(True)
			self.MEPlabel.setHidden(True)

	def two_plus_editors(self, event):
		addl_ed_window = addl_editors.AddlEditorsWindow(self.editorBox1.text(), self.editorBox2.text())
		self.editorBox2.clear()
		if addl_ed_window.exec_():
			if '; ' in addl_ed_window.out_str and addl_ed_window.out_str[-2] == ';':
				self.editorBox2.setText(addl_ed_window.out_str[:-2])
			else:
				self.editorBox2.setText(addl_ed_window.out_str)

	def en_dis_date_boxes(self, wid):
		if wid == self.dateYear:
			if self.dateYear.currentIndex() == 0:
				self.dateMonth.setDisabled(True)
				self.dateDay.setDisabled(True)
			else:
				self.dateMonth.setEnabled(True)
				self.dateDay.setDisabled(True)
			self.dateMonth.setCurrentIndex(0)
			self.dateDay.setCurrentIndex(0)

		elif wid == self.dateMonth:
			if self.dateMonth.currentIndex() == 0:
				self.dateDay.setDisabled(True)
			else:
				self.dateDay.setEnabled(True)
			self.dateDay.setCurrentIndex(0)

	def populate_day_dropdown(self):
		month_len = {"01 (Jan)": 31,
		             "02 (Feb)": 28,
		             "03 (Mar)": 31,
		             "04 (Apr)": 30,
		             "05 (May)": 31,
		             "06 (Jun)": 30,
		             "07 (Jul)": 31,
		             "08 (Aug)": 31,
		             "09 (Sep)": 30,
		             "10 (Oct)": 31,
		             "11 (Nov)": 30,
		             "12 (Dec)": 31}

		if self.dateMonth.currentIndex() != 0:
			if int(self.dateYear.currentText()) % 4 == 0:
				month_len['02 (Feb)'] = 29

			self.dateDay.clear()
			self.dateDay.addItem('')
			for x in range(0, month_len[self.dateMonth.currentText()]):
				self.dateDay.addItem(str(x + 1))
		else:
			pass

	def date_unknown_checked(self):
		if self.dateUnk.isChecked():
			self.dateYear.setCurrentIndex(0)
			self.dateYear.setDisabled(True)
			self.dateMonth.setCurrentIndex(0)
			self.dateMonth.setDisabled(True)
			self.dateDay.setCurrentIndex(0)
			self.dateDay.setDisabled(True)
		else:
			self.dateYear.setEnabled(True)

	def check_star_rating(self):
		try:
			float(str(self.starRatingBox.text()))

			if float(self.starRatingBox.text()) > 5 or 0 < float(self.starRatingBox.text()) < 1 or \
					float(self.starRatingBox.text()) < 0:
				star_rating_range_error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
				                                                'Star rating must be a number\nbetween 1 and 5.')
				star_rating_range_error.exec_()
				self.starRatingBox.clear()
				self.starRatingBox.setFocus()

		except:
			star_rating_type_error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
			                                               'Star rating must be a number\nbetween 1 and 5.')
			star_rating_type_error.exec_()
			self.starRatingBox.clear()
			self.starRatingBox.setFocus()

	def eventFilter(self, source, event):
		if (event.type() == QtCore.QEvent.FocusOut and source is self.videoFootageBox1):
			inp_ftg_list = self.videoFootageBox1.toPlainText().split('\n')
			inp_ftg_list_deduped = []
			if '' in inp_ftg_list:
				inp_ftg_list.remove('')
			marker = set()

			for ftg in inp_ftg_list:
				if ftg.lower() not in marker:
					marker.add(ftg.lower())
					inp_ftg_list_deduped.append(ftg)

			self.videoFootageBox1.clear()

			inp_ftg_list_deduped.sort(key=lambda x: x.lower())
			ftg_str = ''
			for i in range(0, len(inp_ftg_list_deduped)):
				if i < len(inp_ftg_list_deduped) - 1:
					ftg_str += inp_ftg_list_deduped[i] + '\n'
				else:
					ftg_str += inp_ftg_list_deduped[i]

			self.videoFootageBox1.setText(ftg_str)

		return super(VideoEntry, self).eventFilter(source, event)

	def search_for_video_ftg(self):
		self.videoFootageList.clear()
		if self.videoSearchBox.text() == '':
			for vf in self.ftg_list_sorted:
				self.videoFootageList.addItem(vf)

		else:
			new_ftg_list = []
			for ftg in self.ftg_list_sorted:
				if self.videoSearchBox.text().lower() in ftg.lower():
					new_ftg_list.append(ftg)

			for ftg in new_ftg_list:
				self.videoFootageList.addItem(ftg)

			self.videoFootageList.setCurrentRow(0)

	def add_video_ftg(self):
		curr_ftg_list = self.videoFootageBox1.toPlainText().split('\n')
		new_ftg_list = list(set(curr_ftg_list + [self.videoFootageList.currentItem().text()]))
		new_ftg_list.sort(key=lambda x: x.lower())

		try:
			while True:
				new_ftg_list.remove('')
		except ValueError:
			pass

		out_str = ''
		for ftg_ind in range(len(new_ftg_list)):
			if ftg_ind != len(new_ftg_list):
				out_str += new_ftg_list[ftg_ind] + '\n'
			else:
				out_str += new_ftg_list[ftg_ind]

		self.videoFootageBox1.setText(out_str)

	def update_genre_box(self):
		self.songGenreBox.setText(self.songGenreDrop.currentText())

	def tag_window(self, tag_type, tag_box):
		tag_win = tag_checkboxes.TagWindow(tag_type, checked_tags=tag_box.text())
		if tag_win.exec_():
			tag_box.setText(tag_win.out_str[:-2])

	def local_file_clicked(self):
		file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a file')
		if file_path[0]:
			self.localFileBox.setText(file_path[0])

	def submit_button_clicked(self):
		# Checks to make sure data is entered correctly
		## Get list of sub-dbs to enter video into ##
		checked_sub_dbs = [chk.text() for chk in self.list_of_subDB_checks if chk.isChecked()]
		checked_sub_dbs_str = ''
		subdb_dict = common_vars.sub_db_lookup()

		## Check for missing data ##
		missing_fields_list = []

		if self.editorBox1.text() == '':
			missing_fields_list.append('\u2022 Primary editor username')

		if self.titleBox.text() == '':
			missing_fields_list.append('\u2022 Video title')

		if self.checksEnabled.isChecked():
			if self.entry_settings['check_release_date'] == 1 and \
					((self.dateMonth.currentText() == '' or self.dateYear.currentText() == '' or
					  self.dateDay.currentText() == '') and self.dateUnk.isChecked() is False):
				missing_fields_list.append('\u2022 Release date')

			if self.entry_settings['check_video_footage'] == 1 and self.videoFootageBox1.toPlainText() == '':
				missing_fields_list.append('\u2022 Video footage')

			if self.entry_settings['check_song_artist'] == 1 and self.artistBox.text() == '':
				missing_fields_list.append('\u2022 Song artist')

			if self.entry_settings['check_song_title'] == 1 and self.songTitleBox.text() == '':
				missing_fields_list.append('\u2022 Song title')

			if self.entry_settings['check_song_genre'] == 1 and \
					self.songGenreDrop.currentText() == '' and self.songGenreBox.text() == '':
				missing_fields_list.append('\u2022 Song genre')

			if self.entry_settings['check_video_length'] == 1 and \
					(self.lengthMinDrop.currentText() == '' or self.lengthSecDrop.currentText() == ''):
				missing_fields_list.append('\u2022 Video length')

			if self.entry_settings['check_video_desc'] == 1 and self.vidDescBox.toPlainText() == '':
				missing_fields_list.append('\u2022 Video description')

			if self.entry_settings['check_my_rating'] == 1 and self.myRatingDrop.currentText() == '':
				missing_fields_list.append('\u2022 My rating')

			if self.entry_settings['check_tags_1'] == 1 and self.tags1Box.text() == '':
				missing_fields_list.append('\u2022 Tags - ' + common_vars.tag_table_lookup(reverse=True)['tags_1'])

			if self.entry_settings['check_tags_2'] == 1 and self.tags2Box.text() == '':
				missing_fields_list.append('\u2022 Tags - ' + common_vars.tag_table_lookup(reverse=True)['tags_2'])

			if self.entry_settings['check_tags_3'] == 1 and self.tags3Box.text() == '':
				missing_fields_list.append('\u2022 Tags - ' + common_vars.tag_table_lookup(reverse=True)['tags_3'])

			if self.entry_settings['check_tags_4'] == 1 and self.tags4Box.text() == '':
				missing_fields_list.append('\u2022 Tags - ' + common_vars.tag_table_lookup(reverse=True)['tags_4'])

			if self.entry_settings['check_tags_5'] == 1 and self.tags5Box.text() == '':
				missing_fields_list.append('\u2022 Tags - ' + common_vars.tag_table_lookup(reverse=True)['tags_5'])

			if self.entry_settings['check_tags_6'] == 1 and self.tags6Box.text() == '':
				missing_fields_list.append('\u2022 Tags - ' + common_vars.tag_table_lookup(reverse=True)['tags_6'])

		if len(missing_fields_list) > 0:  # If there are missing fields
			missing_fields_string = ''
			for field in missing_fields_list:
				missing_fields_string += field + '\n'

			entry_error_data = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Data missing',
			                                         'The following fields are not populated:\n\n' + \
			                                         missing_fields_string + \
			                                         '\nPlease fill in these fields before submitting.')
			entry_error_data.exec_()

		elif len(checked_sub_dbs) == 0:  # If no sub-dbs are selected
			entry_error_subdb = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
			                                          'You must select at least one sub-database to\n'
			                                          'submit this video entry to.')
			entry_error_subdb.exec_()

		else:  # Data is good -- put video in database
			# Get pseudonyms from editor's existing entries and update this entry with them
			ed_name = self.editorBox1.text()
			pseud_list = self.pseudoBox.text().split('; ')
			for subdb in checked_sub_dbs:
				subdb_formatted = subdb_dict[subdb]
				self.subDB_cursor.execute('SELECT primary_editor_pseudonyms FROM {} WHERE primary_editor_username = ?'
				                          .format(subdb_formatted), (ed_name,))

			all_pseuds = self.subDB_cursor.fetchall()
			all_pseuds_unique_unsplit = []
			for ps_tup in all_pseuds:
				for ps in ps_tup:
					if ps not in all_pseuds_unique_unsplit and ps != '':
						all_pseuds_unique_unsplit.append(ps)

			all_pseuds_unique_split = [[s.strip() for s in x.split(';')] for x in all_pseuds_unique_unsplit]
			all_psueds_flat = list(set(list(itertools.chain.from_iterable(all_pseuds_unique_split)) + pseud_list))
			all_psueds_flat.sort(key=lambda x: x.lower())

			pseud_str = ''
			for pseud in all_psueds_flat:
				if pseud == '':
					pass
				elif pseud != all_psueds_flat[len(all_psueds_flat) - 1]:
					pseud_str += pseud + '; '
				else:
					pseud_str += pseud

			## Prep output dict ##
			output_dict = {}  # Use of this dict takes advantage of Python 3.7+'s feature of preserving insertion order

			if self.vidid is None and self.edit_entry is False:
				vid_id_final = ''
				for dig in range(0, 10):
					rand_list = [str(randint(0, 9)), chr(randint(65, 90)), chr(randint(97, 122))]
					vid_id_final += rand_list[randint(0, 2)]
				output_dict['video_id'] = vid_id_final
			else:
				err = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'error',
				                            'Ctrl-F \'idiot\' in entry_screen.py. You need\nto handle this.')
				err.exec_()

			output_dict['primary_editor_username'] = self.editorBox1.text()
			output_dict['primary_editor_pseudonyms'] = pseud_str
			output_dict['addl_editors'] = self.editorBox2.text()
			output_dict['studio'] = self.studioBox.text()
			output_dict['video_title'] = self.titleBox.text()

			if self.dateMonth.currentText() == '' or self.dateYear.currentText() == '' or self.dateDay.currentText() == '':
				output_dict['release_date'] = ''
			else:
				if int(self.dateDay.currentText()) < 10:
					date_day = '0' + self.dateDay.currentText()
				else:
					date_day = self.dateDay.currentText()
				output_dict['release_date'] = self.dateYear.currentText() + '-' + self.dateMonth.currentText()[:2] + \
				                              '-' + date_day

			if self.dateUnk.isChecked():
				output_dict['release_date_unknown'] = 1
			else:
				output_dict['release_date_unknown'] = 0

			if self.starRatingBox.text() != '':
				output_dict['star_rating'] = float(self.starRatingBox.text())
			else:
				output_dict['star_rating'] = ''

			if self.videoFootageBox1.toPlainText() != '':
				if self.videoFootageBox1.toPlainText().split('\n')[-1] == '':
					ftg_list = self.videoFootageBox1.toPlainText().split('\n')[:-1]
				else:
					ftg_list = self.videoFootageBox1.toPlainText().split('\n')

				ftg_str = ''
				for ftg in ftg_list:
					ftg_str += ftg + '; '
				output_dict['video_footage'] = ftg_str[:-2]
			else:
				output_dict['video_footage'] = ''

			output_dict['song_artist'] = self.artistBox.text()
			output_dict['song_title'] = self.songTitleBox.text()
			output_dict['song_genre'] = self.songGenreBox.text()
			if self.lengthMinDrop.currentText() != '' or self.lengthSecDrop.currentText() != '':
				if self.lengthMinDrop.currentText() == '':
					output_dict['video_length'] = int(self.lengthSecDrop.currentText())
				elif self.lengthSecDrop.currentText() == '':
					output_dict['video_length'] = int(self.lengthMinDrop.currentText()) * 60
				else:
					output_dict['video_length'] = (int(self.lengthMinDrop.currentText()) * 60) + \
					                              int(self.lengthSecDrop.currentText())
			else:
				output_dict['video_length'] = ''

			output_dict['contests_entered'] = self.contestBox.toPlainText()
			output_dict['awards_won'] = self.awardsBox.toPlainText()
			output_dict['video_description'] = self.vidDescBox.toPlainText()
			if self.myRatingDrop.currentText() == '':
				output_dict['my_rating'] = ''
			else:
				output_dict['my_rating'] = float(self.myRatingDrop.currentText())

			if self.notableCheck.isChecked():
				output_dict['notable'] = 1
			else:
				output_dict['notable'] = 0

			if self.favCheck.isChecked():
				output_dict['favorite'] = 1
			else:
				output_dict['favorite'] = 0

			output_dict['tags_1'] = self.tags1Box.text()
			output_dict['tags_2'] = self.tags2Box.text()
			output_dict['tags_3'] = self.tags3Box.text()
			output_dict['tags_4'] = self.tags4Box.text()
			output_dict['tags_5'] = self.tags5Box.text()
			output_dict['tags_6'] = self.tags6Box.text()
			output_dict['comments'] = self.commentsBox.toPlainText()
			output_dict['video_youtube_url'] = self.ytURLBox.text()
			output_dict['video_org_url'] = self.amvOrgURLBox.text()
			output_dict['video_amvnews_url'] = self.amvnewsURLBox.text()
			output_dict['video_other_url'] = self.otherURLBox.text()
			output_dict['local_file'] = self.localFileBox.text()
			output_dict['editor_youtube_channel_url'] = self.editorYTChannelBox.text()
			output_dict['editor_org_profile_url'] = self.editorAMVOrgProfileBox.text()
			output_dict['editor_amvnews_profile_url'] = self.editorAmvnewsProfileBox.text()
			output_dict['editor_other_profile_url'] = self.editorOtherProfileBox.text()
			output_dict['sequence'] = 0

			now = datetime.now()
			yr = str(now.year)
			if now.month < 10:
				mon = '0' + str(now.month)
			else:
				mon = str(now.month)

			if now.day < 10:
				day = '0' + str(now.day)
			else:
				day = str(now.day)

			current_date = yr + '/' + mon + '/' + day
			output_dict['date_entered'] = current_date

			# Update editor's existing entries with any new pseudonyms added
			for uf_name, int_name in subdb_dict.items():
				self.subDB_cursor.execute('UPDATE {} SET primary_editor_pseudonyms = ? WHERE primary_editor_username = ?'
				                          .format(int_name), (pseud_str, ed_name))

			self.subDB_conn.commit()


			## Add video to sub-dbs ##
			if self.edit_entry:
				update_video_entry.update_video_entry(output_dict, checked_sub_dbs, vid_id=self.vidid)
			else:
				update_video_entry.update_video_entry(output_dict, checked_sub_dbs)

			for subdb in checked_sub_dbs:
				checked_sub_dbs_str += '\u2022 ' + subdb + '\n'

			entry_submitted = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Video submitted',
			                                        '{title} has been successfully submitted to the\nfollowing '
			                                        'sub-db(s):\n\n'
			                                        '{subdbs}'.format(title=output_dict['video_title'],
			                                                          subdbs=checked_sub_dbs_str))
			entry_submitted.exec_()

			self.close()
