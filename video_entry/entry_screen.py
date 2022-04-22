import itertools
import mimetypes
import os
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import pytube
import requests
import sqlite3
import webbrowser

from bs4 import BeautifulSoup as beautifulsoup
from datetime import datetime
from main_window import copy_move
from os import getcwd
from shutil import copy

from fetch_video_info import fetch_vid_info
from misc_files import check_for_db, check_for_ffmpeg, check_for_internet_conn, common_vars, download_yt_thumb, \
	download_yt_video, generic_dropdown, mult_thumb_generator, tag_checkboxes
from video_entry import addl_editors, update_video_entry


class VideoEntry(QtWidgets.QMainWindow):
	update_list_signal = QtCore.pyqtSignal()

	def __init__(self, edit_entry=False, inp_vidid=None, inp_subdb=None):
		"""
		xxx
		"""
		super(VideoEntry, self).__init__()

		# Check that .db file exists
		check_for_db.check_for_db()

		# Connection to SQLite databases
		settings_conn = sqlite3.connect(common_vars.settings_db())
		settings_cursor = settings_conn.cursor()

		subDB_conn = sqlite3.connect(common_vars.video_db())
		subDB_cursor = subDB_conn.cursor()
		self.subDB_int_name_list = [val for key, val in common_vars.video_table_lookup().items()]

		# Misc variables
		self.edit_entry = edit_entry
		self.inp_vidid = inp_vidid
		self.inp_subdb = inp_subdb
		self.sequence = ''
		self.play_count = 1
		self.tag_list_names = [tags[1] for tags in subDB_conn.execute('SELECT * FROM tags_lookup')]
		self.tags1_lookup = [row for row in subDB_conn.execute('SELECT * FROM tags_1')]

		# Initialize settings dict
		self.entry_settings = {}
		settings_cursor.execute('SELECT * FROM entry_settings')
		self.entry_settings_list = settings_cursor.fetchall()
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

		# Copy/Back/Submit
		self.copyButton = QtWidgets.QPushButton('Copy')
		self.copyButton.setToolTip('Copy video to another sub-DB')
		self.copyButton.setFixedWidth(60)

		self.moveIcon = QtGui.QIcon(getcwd() + '\\icons\\move-icon.png')
		self.moveButton = QtWidgets.QPushButton()
		self.moveButton.setToolTip('Move video to another sub-DB')
		self.moveButton.setFixedSize(40, 40)
		self.moveButton.setIcon(self.moveIcon)
		self.moveButton.setIconSize(QtCore.QSize(25, 25))

		self.backButton = QtWidgets.QPushButton('Back')
		self.backButton.setFixedWidth(120)

		self.submitButton = QtWidgets.QPushButton('Submit')
		self.submitButton.setFixedWidth(120)

		if self.edit_entry:
			hLayoutMain.addWidget(self.copyButton, alignment=QtCore.Qt.AlignLeft)
			hLayoutMain.addSpacing(40)
		hLayoutMain.addWidget(self.backButton, alignment=QtCore.Qt.AlignRight)
		hLayoutMain.addWidget(self.submitButton, alignment=QtCore.Qt.AlignRight)

		## Tab 1 - Left grid ##
		tab_1_grid_L = QtWidgets.QGridLayout()
		tab_1_grid_L.setAlignment(QtCore.Qt.AlignTop)
		tab_1_grid_L.setColumnMinimumWidth(5, 7)
		grid_1_L_vert_ind = 0

		# Editor 1
		self.editorLabel = QtWidgets.QLabel()
		self.editorLabel.setText('Primary editor\nusername:')
		self.editorBox1 = QtWidgets.QLineEdit()
		self.editorBox1.setFixedWidth(200)

		self.editorNameList = []
		for table in self.subDB_int_name_list:
			subDB_cursor.execute('SELECT primary_editor_username FROM {}'.format(table))
			for ed_name in subDB_cursor.fetchall():
				self.editorNameList.append(ed_name[0])

		self.editorNameListSorted = list(set(self.editorNameList))
		self.editorNameListSorted.sort(key=lambda x: x.casefold())

		self.editorNameCompleter = QtWidgets.QCompleter(self.editorNameListSorted)
		self.editorNameCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.editorNameCompleter.setMaxVisibleItems(15)
		self.editorBox1.setCompleter(self.editorNameCompleter)

		tab_1_grid_L.addWidget(self.editorLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.editorBox1, grid_1_L_vert_ind, 1, 1, 6)

		grid_1_L_vert_ind += 1

		# Pseudonyms
		self.pseudoLabel = QtWidgets.QLabel()
		self.pseudoLabel.setText('Primary editor\nother username(s):')
		self.pseudoLabel.setToolTip('If the editor goes by or has gone by any other usernames,\n'
									'enter them here. Separate multiple usernames with a semi-\n'
									'colon + space (ex: username1; username2)')
		self.pseudoBox = QtWidgets.QLineEdit()
		self.pseudoBox.setFixedWidth(200)
		self.pseudoBox.setCompleter(self.editorNameCompleter)

		tab_1_grid_L.addWidget(self.pseudoLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.pseudoBox, grid_1_L_vert_ind, 1, 1, 6)

		grid_1_L_vert_ind += 1

		# Addl editors + MEP text
		self.addlEditorsLabel = QtWidgets.QLabel()
		self.addlEditorsLabel.setText('Addl. editor(s):')
		self.editorBox2 = QtWidgets.QLineEdit()
		self.editorBox2.setFixedWidth(200)

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
		tab_1_grid_L.addWidget(self.editorBox2, grid_1_L_vert_ind, 1, 1, 6)
		tab_1_grid_L.addWidget(self.MEPlabel, grid_1_L_vert_ind, 7, 1, 5)

		grid_1_L_vert_ind += 1

		# Studio
		self.studioLabel = QtWidgets.QLabel()
		self.studioLabel.setText('Studio:')
		self.studioBox = QtWidgets.QLineEdit()
		self.studioBox.setFixedWidth(200)

		self.studioList = []
		for table in self.subDB_int_name_list:
			subDB_cursor.execute('SELECT studio FROM {}'.format(table))
			for studio_name in subDB_cursor.fetchall():
				if studio_name != '':
					self.studioList.append(studio_name[0])

		self.studioListSorted = list(set(self.studioList))
		self.studioListSorted.sort(key=lambda x: x.casefold())

		self.studioCompleter = QtWidgets.QCompleter(self.studioListSorted)
		self.studioCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.studioCompleter.setMaxVisibleItems(15)
		self.studioBox.setCompleter(self.studioCompleter)

		tab_1_grid_L.addWidget(self.studioLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.studioBox, grid_1_L_vert_ind, 1, 1, 6)

		grid_1_L_vert_ind += 1

		# Spacer
		tab_1_grid_L.setRowMinimumHeight(grid_1_L_vert_ind, 20)
		grid_1_L_vert_ind += 1

		# Video title
		self.titleLabel = QtWidgets.QLabel()
		self.titleLabel.setText('Video title:')
		self.titleBox = QtWidgets.QLineEdit()
		self.titleBox.setFixedWidth(200)

		tab_1_grid_L.addWidget(self.titleLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.titleBox, grid_1_L_vert_ind, 1, 1, 6)

		grid_1_L_vert_ind += 1

		# Release date
		self.dateLabel = QtWidgets.QLabel()
		self.dateLabel.setText('Release date:')
		self.dateLabel.setToolTip('Please note that you must provide a year, month, and day\n'
								  'for AMV Tracker to accept the date entry.')
		self.dateYear = QtWidgets.QComboBox()
		self.dateYear.setFixedWidth(70)
		self.dateMonth = QtWidgets.QComboBox()
		self.dateMonth.setFixedWidth(70)
		self.dateMonth.setDisabled(True)
		self.dateDay = QtWidgets.QComboBox()
		self.dateDay.setFixedWidth(40)
		self.dateDay.setDisabled(True)
		self.dateUnk = QtWidgets.QCheckBox('Date unknown')

		self.monthDict = {'01 (Jan)': 1,
						  '02 (Feb)': 2,
						  '03 (Mar)': 3,
						  '04 (Apr)': 4,
						  '05 (May)': 5,
						  '06 (Jun)': 6,
						  '07 (Jul)': 7,
						  '08 (Aug)': 8,
						  '09 (Sep)': 9,
						  '10 (Oct)': 10,
						  '11 (Nov)': 11,
						  '12 (Dec)': 12}

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
		tab_1_grid_L.addWidget(self.dateYear, grid_1_L_vert_ind, 1, 1, 3)
		tab_1_grid_L.addWidget(self.dateMonth, grid_1_L_vert_ind, 3, 1, 3)
		tab_1_grid_L.addWidget(self.dateDay, grid_1_L_vert_ind, 5, 1, 3)
		grid_1_L_vert_ind += 1

		tab_1_grid_L.addWidget(self.dateUnk, grid_1_L_vert_ind, 1, 1, 4)
		grid_1_L_vert_ind += 1

		# Spacer
		tab_1_grid_L.setRowMinimumHeight(grid_1_L_vert_ind, 15)
		grid_1_L_vert_ind += 1

		# Star rating
		self.starRatingLabel = QtWidgets.QLabel()
		self.starRatingLabel.setText('Star rating:')
		self.starRatingLabel.setToolTip('Star ratings can be found on the amv.org entry (if\n'
										'the video is on the .org and you are a Donator) or\n'
										'on the video\'s amvnews page, if one exists.')
		self.starRatingBox = QtWidgets.QLineEdit()

		self.starRatingBox.setFixedWidth(50)

		tab_1_grid_L.addWidget(self.starRatingLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.starRatingBox, grid_1_L_vert_ind, 1, 1, 3)

		grid_1_L_vert_ind += 1

		# Video Footage 1
		self.videoFootageLabel = QtWidgets.QLabel()
		self.videoFootageLabel.setText('Video footage used:')
		self.videoFootageBox = QtWidgets.QListWidget()
		self.videoFootageBox.setFixedSize(200, 120)

		self.videoSearchBox = QtWidgets.QLineEdit()
		self.videoSearchBox.setFixedWidth(200)
		self.videoSearchBox.setPlaceholderText('Search...')
		self.videoSearchBox.setToolTip('If the footage does not show up in the search,\n'
									   'type it out here fully and then click the "+"\n'
									   'button to the right.')

		self.footageList = []
		for table in self.subDB_int_name_list:
			subDB_cursor.execute('SELECT video_footage FROM {}'.format(table))
			for ftg_tup in subDB_cursor.fetchall():
				for ftg_grp in list(ftg_tup):
					for ftg in ftg_grp.split('; '):
						if ftg not in self.footageList:
							self.footageList.append(ftg)

		self.footageListSorted = list(set(self.footageList))
		self.footageListSorted.sort(key=lambda x: x.casefold())

		self.footageCompleter = QtWidgets.QCompleter(self.footageListSorted)
		self.footageCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.footageCompleter.setMaxVisibleItems(15)
		self.videoSearchBox.setCompleter(self.footageCompleter)

		# Add video footage
		self.addFootage = QtWidgets.QPushButton('+')
		self.addFootage.setFixedSize(30, 20)
		self.addFootage.setToolTip('Add to video footage list')
		self.addFootage.setDisabled(True)

		self.removeFootage = QtWidgets.QPushButton('-')
		self.removeFootage.setFixedSize(30, 20)
		self.removeFootage.setToolTip('Remove selected video footage from list')
		self.removeFootage.setDisabled(True)

		tab_1_grid_L.addWidget(self.videoFootageLabel, grid_1_L_vert_ind, 0, alignment=QtCore.Qt.AlignTop)
		tab_1_grid_L.addWidget(self.videoSearchBox, grid_1_L_vert_ind, 1, 1, 6, alignment=QtCore.Qt.AlignTop)
		tab_1_grid_L.addWidget(self.addFootage, grid_1_L_vert_ind, 7, alignment=QtCore.Qt.AlignTop)
		grid_1_L_vert_ind += 1

		tab_1_grid_L.addWidget(self.videoFootageBox, grid_1_L_vert_ind, 1, 1, 6)
		tab_1_grid_L.addWidget(self.removeFootage, grid_1_L_vert_ind, 7, alignment=QtCore.Qt.AlignTop)
		grid_1_L_vert_ind += 1

		# Spacer
		tab_1_grid_L.setRowMinimumHeight(grid_1_L_vert_ind, 20)
		grid_1_L_vert_ind += 1

		# Artist
		self.artistLabel = QtWidgets.QLabel()
		self.artistLabel.setText('Song artist:')
		self.artistBox = QtWidgets.QLineEdit()
		self.artistBox.setFixedWidth(200)

		self.artistList = []
		for tn in self.subDB_int_name_list:
			subDB_cursor.execute('SELECT song_artist FROM {}'.format(tn))
			for artist in subDB_cursor.fetchall():
				if artist[0] != '':
					self.artistList.append(artist[0])

		self.artistListSorted = list(set(self.artistList))
		self.artistListSorted.sort(key=lambda x: x.casefold())

		self.artistCompleter = QtWidgets.QCompleter(self.artistListSorted)
		self.artistCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.artistCompleter.setMaxVisibleItems(15)
		self.artistBox.setCompleter(self.artistCompleter)

		tab_1_grid_L.addWidget(self.artistLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.artistBox, grid_1_L_vert_ind, 1, 1, 6)

		grid_1_L_vert_ind += 1

		# Song title
		self.songTitleLabel = QtWidgets.QLabel()
		self.songTitleLabel.setText('Song title:')
		self.songTitleBox = QtWidgets.QLineEdit()
		self.songTitleBox.setFixedWidth(200)

		tab_1_grid_L.addWidget(self.songTitleLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.songTitleBox, grid_1_L_vert_ind, 1, 1, 6)

		grid_1_L_vert_ind += 1

		# Song genre
		self.songGenreLabel = QtWidgets.QLabel()
		self.songGenreLabel.setText('Song genre:')
		self.songGenreBox = QtWidgets.QLineEdit()
		self.songGenreBox.setFixedWidth(200)

		self.genreList = []
		for subDB in self.subDB_int_name_list:
			subDB_cursor.execute('SELECT song_genre FROM {}'.format(subDB))
			for genre in subDB_cursor.fetchall():
				if genre[0].lower() not in self.genreList and genre[0] != '':
					self.genreList.append(genre[0].lower())

		self.genreList.sort(key=lambda x: x.lower())
		self.genreList.insert(0, '')

		self.songGenreCompleter = QtWidgets.QCompleter(self.genreList)
		self.songGenreCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.songGenreBox.setCompleter(self.songGenreCompleter)

		tab_1_grid_L.addWidget(self.songGenreLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.songGenreBox, grid_1_L_vert_ind, 1, 1, 6)

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
		tab_1_grid_L.addWidget(self.lengthMinLabel, grid_1_L_vert_ind, 2, 1, 2)
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
		tab_1_grid_R.addWidget(self.contestBox, grid_1_R_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		grid_1_R_vert_ind += 1

		# Awards
		self.awardsLabel = QtWidgets.QLabel()
		self.awardsLabel.setText('Awards won:')
		self.awardsBox = QtWidgets.QTextEdit()
		self.awardsBox.setFixedSize(200, 80)

		tab_1_grid_R.addWidget(self.awardsLabel, grid_1_R_vert_ind, 0, alignment=QtCore.Qt.AlignTop)
		tab_1_grid_R.addWidget(self.awardsBox, grid_1_R_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		grid_1_R_vert_ind += 1

		# Video description
		self.vidDescLabel = QtWidgets.QLabel()
		self.vidDescLabel.setText('Video description:')
		self.vidDescBox = QtWidgets.QTextEdit()
		self.vidDescBox.setFixedSize(200, 260)

		tab_1_grid_R.addWidget(self.vidDescLabel, grid_1_R_vert_ind, 0, alignment=QtCore.Qt.AlignTop)
		tab_1_grid_R.addWidget(self.vidDescBox, grid_1_R_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)

		## Tab 2 ##
		tab_2_grid = QtWidgets.QGridLayout()
		tab_2_grid.setAlignment(QtCore.Qt.AlignTop)
		grid_2_vert_ind = 0

		# My Rating
		self.myRatingLabel = QtWidgets.QLabel()
		self.myRatingLabel.setText('My rating:')
		self.myRatingDrop = QtWidgets.QComboBox()
		self.myRatingDrop.setFixedWidth(60)
		self.myRatingDrop.setMaxVisibleItems(22)

		myRatingList = [rat * 0.5 for rat in range(0, 21)]

		self.myRatingDrop.addItem('')
		for rating in myRatingList:
			self.myRatingDrop.addItem(str(rating))

		tab_2_grid.addWidget(self.myRatingLabel, grid_2_vert_ind, 0, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.myRatingDrop, grid_2_vert_ind, 1, 1, 3, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Notable checkbox
		self.notableCheck = QtWidgets.QCheckBox('Notable')
		tab_2_grid.addWidget(self.notableCheck, grid_2_vert_ind, 0, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Favorite checkbox
		self.favCheck = QtWidgets.QCheckBox('Favorite')
		tab_2_grid.addWidget(self.favCheck, grid_2_vert_ind, 0, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		tab_2_grid.setRowMinimumHeight(grid_2_vert_ind, 10)
		grid_2_vert_ind += 1

		# Tags 1
		self.tags1Button = QtWidgets.QPushButton(self.tag_list_names[0])

		self.tags1Box = QtWidgets.QLineEdit()
		self.tags1Box.setPlaceholderText('<-- Click to select tags')
		self.tags1Box.setFixedWidth(550)
		self.tags1Box.setReadOnly(True)
		self.tags1X = QtWidgets.QPushButton('X')
		self.tags1X.setFixedWidth(20)
		self.tags1X.setToolTip('Clear tags')

		tab_2_grid.addWidget(self.tags1Button, grid_2_vert_ind, 0, 1, 2)
		tab_2_grid.addWidget(self.tags1Box, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags1X, grid_2_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Tags 2
		self.tags2Button = QtWidgets.QPushButton(self.tag_list_names[1])
		self.tags2Box = QtWidgets.QLineEdit()
		self.tags2Box.setPlaceholderText('<-- Click to select tags')
		self.tags2Box.setFixedWidth(550)
		self.tags2Box.setReadOnly(True)
		self.tags2X = QtWidgets.QPushButton('X')
		self.tags2X.setFixedWidth(20)
		self.tags2X.setToolTip('Clear tags')

		tab_2_grid.addWidget(self.tags2Button, grid_2_vert_ind, 0, 1, 2)
		tab_2_grid.addWidget(self.tags2Box, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags2X, grid_2_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Tags 3
		self.tags3Button = QtWidgets.QPushButton(self.tag_list_names[2])
		self.tags3Box = QtWidgets.QLineEdit()
		self.tags3Box.setPlaceholderText('<-- Click to select tags')
		self.tags3Box.setFixedWidth(550)
		self.tags3Box.setReadOnly(True)
		self.tags3X = QtWidgets.QPushButton('X')
		self.tags3X.setFixedWidth(20)
		self.tags3X.setToolTip('Clear tags')

		tab_2_grid.addWidget(self.tags3Button, grid_2_vert_ind, 0, 1, 2)
		tab_2_grid.addWidget(self.tags3Box, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags3X, grid_2_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Tags 4
		self.tags4Button = QtWidgets.QPushButton(self.tag_list_names[3])
		self.tags4Box = QtWidgets.QLineEdit()
		self.tags4Box.setPlaceholderText('<-- Click to select tags')
		self.tags4Box.setFixedWidth(550)
		self.tags4Box.setReadOnly(True)
		self.tags4X = QtWidgets.QPushButton('X')
		self.tags4X.setFixedWidth(20)
		self.tags4X.setToolTip('Clear tags')

		tab_2_grid.addWidget(self.tags4Button, grid_2_vert_ind, 0, 1, 2)
		tab_2_grid.addWidget(self.tags4Box, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags4X, grid_2_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Tags 5
		self.tags5Button = QtWidgets.QPushButton(self.tag_list_names[4])
		self.tags5Box = QtWidgets.QLineEdit()
		self.tags5Box.setPlaceholderText('<-- Click to select tags')
		self.tags5Box.setFixedWidth(550)
		self.tags5Box.setReadOnly(True)
		self.tags5X = QtWidgets.QPushButton('X')
		self.tags5X.setFixedWidth(20)
		self.tags5X.setToolTip('Clear tags')

		tab_2_grid.addWidget(self.tags5Button, grid_2_vert_ind, 0, 1, 2)
		tab_2_grid.addWidget(self.tags5Box, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags5X, grid_2_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Tags 6
		self.tags6Button = QtWidgets.QPushButton(self.tag_list_names[5])
		self.tags6Box = QtWidgets.QLineEdit()
		self.tags6Box.setPlaceholderText('<-- Click to select tags')
		self.tags6Box.setFixedWidth(550)
		self.tags6Box.setReadOnly(True)
		self.tags6X = QtWidgets.QPushButton('X')
		self.tags6X.setFixedWidth(20)
		self.tags6X.setToolTip('Clear tags')

		tab_2_grid.addWidget(self.tags6Button, grid_2_vert_ind, 0, 1, 2)
		tab_2_grid.addWidget(self.tags6Box, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags6X, grid_2_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Disable tag buttons
		self.tagWidGroups = [[self.tags1Button, self.tags1Box, self.tags1X],
							 [self.tags2Button, self.tags2Box, self.tags2X],
							 [self.tags3Button, self.tags3Box, self.tags3X],
							 [self.tags4Button, self.tags4Box, self.tags4X],
							 [self.tags5Button, self.tags5Box, self.tags5X],
							 [self.tags6Button, self.tags6Box, self.tags6X]]

		for ind in range(0, len(self.tagWidGroups)):
			subDB_cursor.execute('SELECT * FROM tags_{}'.format(ind + 1))
			table_result = subDB_cursor.fetchone()
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
		self.commentsLabel.setText('Personal comments/notes:')
		self.commentsBox = QtWidgets.QTextEdit()
		self.commentsBox.setFixedSize(670, 180)

		tab_2_grid.addWidget(self.commentsLabel, grid_2_vert_ind, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		tab_2_grid.addWidget(self.commentsBox, grid_2_vert_ind + 1, 0, 1, 4, alignment=QtCore.Qt.AlignTop)

		## Tab 3 - Top grid ##
		tab_3_grid_T = QtWidgets.QGridLayout()
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
		self.dlIcon = QtGui.QIcon(getcwd() + '\\icons\\download-icon.png')
		self.ytURLLabel = QtWidgets.QLabel()
		self.ytURLLabel.setText('Video YouTube URL:')
		self.ytURLBox = QtWidgets.QLineEdit()
		self.ytURLBox.setFixedWidth(350)
		self.searchYTButton = QtWidgets.QPushButton('Search YouTube')
		self.searchYTButton.setFixedWidth(110)
		self.searchYTButton.setToolTip('Search for this video on YouTube. Must have both editor name\n'
									   'and video title entered on the "Video information" tab.')
		self.searchYTButton.setDisabled(True)

		self.fetchYTInfo = QtWidgets.QPushButton('Fetch YT info')
		self.fetchYTInfo.setFixedWidth(110)
		self.fetchYTInfo.setToolTip('If you enter the video\'s YouTube URL, you can use this function\n'
									'to automatically fetch the video info provided on YouTube.')
		self.fetchYTInfo.setDisabled(True)

		self.YTDLButton = QtWidgets.QPushButton()
		self.YTDLButton.setFixedSize(22, 22)
		self.YTDLButton.setIcon(self.dlIcon)
		self.YTDLButton.setToolTip('Download video from YouTube')
		self.YTDLButton.setDisabled(True)

		tab_3_grid_T.addWidget(self.ytURLLabel, grid_3_T_vert_ind, 0, alignment=QtCore.Qt.AlignTop)
		tab_3_grid_T.addWidget(self.ytURLBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.searchYTButton, grid_3_T_vert_ind, 2, 1, 5, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.fetchYTInfo, grid_3_T_vert_ind, 7, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.YTDLButton, grid_3_T_vert_ind, 8, alignment=QtCore.Qt.AlignLeft)
		grid_3_T_vert_ind += 1

		# AMV.org URL
		self.amvOrgURLLabel = QtWidgets.QLabel()
		self.amvOrgURLLabel.setText('Video AMV.org URL:')
		self.amvOrgURLBox = QtWidgets.QLineEdit()
		self.amvOrgURLBox.setFixedWidth(350)

		self.searchOrgButton = QtWidgets.QPushButton('Search amv.org')
		self.searchOrgButton.setFixedWidth(110)
		self.searchOrgButton.setDisabled(True)
		self.searchOrgButton.setToolTip('Search for this video on AnimeMusicVideos.org. Must have both editor name\n'
									   'and video title entered on the "Video information" tab.')

		self.fetchOrgVidDesc = QtWidgets.QPushButton('Fetch video descr.')
		self.fetchOrgVidDesc.setFixedWidth(110)
		self.fetchOrgVidDesc.setDisabled(True)
		self.fetchOrgVidDesc.setToolTip('If you enter an AMV.org video profile link, press this\n'
										'button to populate the Video Description field on the\n'
										'Video Information tab with the description provided\n'
										'on the .org video profile')

		self.fetchOrgInfo = QtWidgets.QPushButton('Fetch .org info')
		self.fetchOrgInfo.setDisabled(True)
		self.fetchOrgInfo.setFixedWidth(110)
		self.fetchOrgInfo.setToolTip('If you enter an AMV.org video profile link, press this\n'
									 'button to populate the rest of the video information\n'
									 'as provided on the video\'s .org profile.')

		tab_3_grid_T.addWidget(self.amvOrgURLLabel, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.amvOrgURLBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		# tab_3_grid_T.addWidget(self.fetchOrgVidDesc, grid_3_T_vert_ind, 2, 1, 10, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.searchOrgButton, grid_3_T_vert_ind, 2, 1, 5, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.fetchOrgInfo, grid_3_T_vert_ind, 7, 1, 10, alignment=QtCore.Qt.AlignLeft)
		grid_3_T_vert_ind += 1

		# amvnews URL
		self.amvnewsURLLabel = QtWidgets.QLabel()
		self.amvnewsURLLabel.setText('Video amvnews URL:')
		self.amvnewsURLBox = QtWidgets.QLineEdit()
		self.amvnewsURLBox.setFixedWidth(350)

		tab_3_grid_T.addWidget(self.amvnewsURLLabel, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.amvnewsURLBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		grid_3_T_vert_ind += 1

		# Other URL
		self.otherURLLabel = QtWidgets.QLabel()
		self.otherURLLabel.setText('Other video URL:')
		self.otherURLBox = QtWidgets.QLineEdit()
		self.otherURLBox.setFixedWidth(350)

		tab_3_grid_T.addWidget(self.otherURLLabel, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.otherURLBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		grid_3_T_vert_ind += 1

		# Local file
		self.localFileButton = QtWidgets.QPushButton('Local file')
		self.localFileButton.setFixedWidth(90)
		self.localFileButton.setToolTip(
			'If this video is kept as a local file on your computer, please locate it here\n'
			'so that you can search for and play this video from AMV Tracker.')
		self.localFileBox = QtWidgets.QLineEdit()
		self.localFileBox.setFixedWidth(350)
		self.localFileBox.setReadOnly(True)
		self.localFileBox.setPlaceholderText('<-- Click to locate video file')
		self.localFileX = QtWidgets.QPushButton('X')
		self.localFileX.setFixedSize(22, 22)
		self.localFileX.setToolTip('Delete local file path')
		self.localFileWatch = QtWidgets.QPushButton('Watch')
		self.localFileWatch.setFixedWidth(60)

		tab_3_grid_T.addWidget(self.localFileButton, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.localFileBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.localFileX, grid_3_T_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		# tab_3_grid_T.addWidget(self.localFileWatch, grid_3_T_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		grid_3_T_vert_ind += 1

		# Thumbnail
		self.thumbnailButton = QtWidgets.QPushButton('Thumbnail')
		self.thumbnailButton.setFixedWidth(90)
		self.thumbnailButton.setToolTip('Thumbnails are used in Detail view (Settings > Video search > Search view\n'
										'type = Detail) to provide a visual for each video entry.')
		self.thumbnailBox = QtWidgets.QLineEdit()
		self.thumbnailBox.setFixedWidth(350)
		self.thumbnailBox.setReadOnly(True)
		self.thumbnailBox.setPlaceholderText('<-- Click to locate thumbnail file')

		self.thumbnailX = QtWidgets.QPushButton('X')
		self.thumbnailX.setFixedSize(22, 22)
		self.thumbnailX.setToolTip('Delete thumbnail file path')

		self.thumbnailDLButton = QtWidgets.QPushButton()
		self.thumbnailDLButton.setFixedSize(22, 22)
		self.thumbnailDLButton.setIcon(self.dlIcon)
		self.thumbnailDLButton.setToolTip('Download YouTube thumbnail (YouTube URL must be\nprovided above)')
		self.thumbnailDLButton.setDisabled(True)

		self.genThumbIcon = QtGui.QIcon(getcwd() + '\\icons\\generate-thumbnail-icon.png')
		self.thumbnailGenButton = QtWidgets.QPushButton()
		self.thumbnailGenButton.setFixedSize(22, 22)
		self.thumbnailGenButton.setIcon(self.genThumbIcon)
		self.thumbnailGenButton.setToolTip(
			'Generate thumbnail from video file (local video file path\nmust be provided '
			'above)')
		self.thumbnailGenButton.setDisabled(True)

		tab_3_grid_T.setColumnStretch(3, 0)
		tab_3_grid_T.setColumnStretch(4, 0)
		tab_3_grid_T.addWidget(self.thumbnailButton, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.thumbnailBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.thumbnailX, grid_3_T_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.thumbnailDLButton, grid_3_T_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.thumbnailGenButton, grid_3_T_vert_ind, 4, alignment=QtCore.Qt.AlignLeft)

		## Tab 3 - Bottom grid ##
		#self.tabs.addTab(self.tab3, 'Sources and URLs')
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

		# Fetch profiles button
		self.fetchProfilesButton = QtWidgets.QPushButton('Fetch URLs from existing entries')
		self.fetchProfilesButton.setFixedWidth(215)
		self.fetchProfilesButton.setDisabled(True)
		self.fetchProfilesButton.setToolTip('If you have already entered these profile URLs on a previous\n'
											'video entry from this editor, click this button to auto-\n'
											'populate these fields with what you\'ve already entered')

		tab_3_grid_B.addWidget(self.fetchProfilesButton, grid_3_B_vert_ind, 0, 1, 2)
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
		tab_4_vLayoutMaster = QtWidgets.QVBoxLayout()
		tab_4_vLayoutMaster.setAlignment(QtCore.Qt.AlignTop)
		tab_4_vLayout1 = QtWidgets.QVBoxLayout()
		tab_4_vLayout2 = QtWidgets.QVBoxLayout()
		tab_4_vLayout3 = QtWidgets.QVBoxLayout()
		tab_4_hLayout = QtWidgets.QHBoxLayout()
		tab_4_hLayout.setAlignment(QtCore.Qt.AlignLeft)

		self.tab_4_scrollvLayout1 = QtWidgets.QVBoxLayout()
		self.tab_4_scrollvLayout2 = QtWidgets.QVBoxLayout()

		# Checks enabled
		self.checksEnabled = QtWidgets.QCheckBox('Checks enabled')
		self.checksEnabled.setToolTip('If checked, AMV Tracker will not allow you to submit a video\n'
									  'to the database unless all fields that you have specified in\n'
									  '[Settings > Video entry] have data in them. Please note that\n'
									  'all entries must have a Primary Editor Username and Video Title\n'
									  'regardless.')
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
		self.subDB_list_ = [x[0] for x in subDB_conn.execute('SELECT user_subdb_name FROM db_name_lookup')]
		self.subDB_list = [self.subDB_list_[0]] + [n for n in sorted(self.subDB_list_[1:], key=lambda x: x.casefold())]
		self.listOfSubDBChecks = [QtWidgets.QCheckBox(subDB) for subDB in self.subDB_list]
		sub_db_ind = 0
		for check in self.listOfSubDBChecks:
			self.tab_4_scrollvLayout1.addWidget(check)
			self.subDBSignalMapper.setMapping(check, sub_db_ind)
			if sub_db_ind == 0:
				check.setChecked(True)
			sub_db_ind += 1
			check.clicked.connect(self.subDBSignalMapper.map)

		self.subDBScrollWidget = QtWidgets.QWidget()
		self.subDBScrollArea = QtWidgets.QScrollArea()
		self.subDBScrollWidget.setLayout(self.tab_4_scrollvLayout1)
		self.subDBScrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.subDBScrollArea.setFixedSize(250, 350)
		self.subDBScrollArea.setWidget(self.subDBScrollWidget)

		# Add to Custom Lists
		self.addtoCustListsLabel = QtWidgets.QLabel()
		self.addtoCustListsLabel.setText('Add to following Custom Lists:')
		self.addtoCustListsLabel.setFont(self.headerFont)
		tab_4_vLayout3.addWidget(self.addtoCustListsLabel, alignment=QtCore.Qt.AlignCenter)

		# List of Custom Lists (in ScrollArea)
		self.tab_4_scrollvLayout2.addStretch()
		self.CL_list = [k for k, v in common_vars.custom_list_lookup().items()]
		self.CL_list.sort(key=lambda x: x.casefold())
		self.listOfCLChecks = [QtWidgets.QCheckBox(cl) for cl in self.CL_list]
		for cbox in self.listOfCLChecks:
			self.tab_4_scrollvLayout2.addWidget(cbox)

		self.custListScrollWidget = QtWidgets.QWidget()
		self.custListScrollArea = QtWidgets.QScrollArea()
		self.custListScrollWidget.setLayout(self.tab_4_scrollvLayout2)
		self.custListScrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.custListScrollArea.setFixedSize(250, 350)
		self.custListScrollArea.setWidget(self.custListScrollWidget)

		## Layouts ##
		self.tabs.addTab(self.tab3, 'Sources and URLs')
		self.tabs.addTab(self.tab1, 'Video information')
		self.tabs.addTab(self.tab2, 'My rating/tags/comments')
		self.tabs.addTab(self.tab4, 'Submission rules')

		tab1_grid_hLayout.addLayout(tab_1_grid_L)
		tab1_grid_hLayout.addSpacing(15)
		tab1_grid_hLayout.addLayout(tab_1_grid_R)

		tab3_grid_vLayout.addLayout(tab_3_grid_T)
		tab3_grid_vLayout.addLayout(tab_3_grid_B)

		tab_4_vLayout2.addWidget(self.subDBScrollArea, alignment=QtCore.Qt.AlignTop)
		tab_4_vLayout3.addWidget(self.custListScrollArea, alignment=QtCore.Qt.AlignTop)
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

		# Misc functions
		if self.inp_vidid is None:
			self.vidid = common_vars.id_generator('video')
		else:
			self.vidid = self.inp_vidid
			self.edit_pop()

		if self.edit_entry:
			if self.editorBox1.text() != '' and self.titleBox.text() != '':
				self.searchYTButton.setEnabled(True)
				self.searchOrgButton.setEnabled(True)

		# Signals/slots
		# Tab 1
		if not self.edit_entry:
			self.editorBox1.editingFinished.connect(self.check_for_existing_entry)
			self.titleBox.editingFinished.connect(self.check_for_existing_entry)
		self.editorBox1.textChanged.connect(self.editor_1_text_changed)
		self.editorBox1.textChanged.connect(self.enable_yt_btns)
		self.editorBox1.textChanged.connect(self.en_dis_org_btns)
		self.MEPlabel.mousePressEvent = self.two_plus_editors
		self.titleBox.textChanged.connect(self.enable_yt_btns)
		self.titleBox.textChanged.connect(self.en_dis_org_btns)
		self.dateYear.currentIndexChanged.connect(lambda: self.en_dis_date_boxes(self.dateYear))
		self.dateMonth.currentIndexChanged.connect(lambda: self.en_dis_date_boxes(self.dateMonth))
		self.dateMonth.currentIndexChanged.connect(self.populate_day_dropdown)
		self.dateUnk.clicked.connect(self.date_unknown_checked)
		self.starRatingBox.editingFinished.connect(self.check_star_rating)
		self.videoSearchBox.textChanged.connect(self.enable_add_ftg_btn)
		self.addFootage.clicked.connect(self.add_video_ftg)
		self.videoFootageBox.itemSelectionChanged.connect(self.enable_remove_ftg_btn)
		self.removeFootage.clicked.connect(self.remove_video_ftg)

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
		self.ytURLBox.textChanged.connect(lambda: self.enable_thumb_btns('yt'))
		self.ytURLBox.textChanged.connect(self.enable_yt_btns)
		self.searchYTButton.clicked.connect(self.search_youtube)
		self.fetchYTInfo.clicked.connect(self.fetch_youtube_info)
		self.YTDLButton.clicked.connect(self.dl_yt_vid)
		self.amvOrgURLBox.textChanged.connect(self.en_dis_org_btns)
		self.searchOrgButton.clicked.connect(self.search_org)
		self.fetchOrgVidDesc.clicked.connect(self.fetch_vid_desc)
		self.fetchOrgInfo.clicked.connect(self.fetch_org_info)
		self.localFileButton.clicked.connect(self.local_file_clicked)
		self.localFileBox.textChanged.connect(lambda: self.enable_thumb_btns('local'))
		self.thumbnailButton.clicked.connect(self.thumbnail_clicked)
		self.thumbnailX.clicked.connect(self.delete_thumb_path)
		self.localFileX.clicked.connect(self.localFileBox.clear)
		self.thumbnailDLButton.clicked.connect(self.dl_thumb)
		self.thumbnailGenButton.clicked.connect(self.generate_thumb)
		self.fetchProfilesButton.clicked.connect(self.fetch_profiles)

		# Tab 4
		self.copyButton.clicked.connect(lambda: self.copy_video(self.inp_vidid,
																common_vars.sub_db_lookup(reverse=True)[self.inp_subdb]))

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

		# Set focus
		self.editorBox1.setFocus()
		
		# Close connections
		settings_conn.close()
		subDB_conn.close()

	def edit_pop(self):
		vid_dict = common_vars.get_all_vid_info(self.inp_subdb, self.inp_vidid)
		subdb_friendly = common_vars.sub_db_lookup(reverse=True)[self.inp_subdb]

		self.editorBox1.setText(vid_dict['primary_editor_username'])
		self.editorBox1.setCursorPosition(0)
		self.pseudoBox.setText(vid_dict['primary_editor_pseudonyms'])
		self.pseudoBox.setCursorPosition(0)
		self.editorBox2.setText(vid_dict['addl_editors'])
		self.editorBox2.setCursorPosition(0)
		self.studioBox.setText(vid_dict['studio'])
		self.studioBox.setCursorPosition(0)
		self.titleBox.setText(vid_dict['video_title'])
		self.titleBox.setCursorPosition(0)

		if vid_dict['release_date_unknown'] == 1:
			self.dateUnk.setChecked(True)
		elif vid_dict['release_date'] != '' and vid_dict['release_date'] is not None:
			rel_date = vid_dict['release_date'].split('/')  # [YYYY, MM, DD]
			self.dateYear.setCurrentText(rel_date[0])
			self.dateMonth.setCurrentIndex(int(rel_date[1]))
			self.dateMonth.setEnabled(True)
			self.populate_day_dropdown()
			self.dateDay.setCurrentIndex(int(rel_date[2]))
			self.dateDay.setEnabled(True)

		self.starRatingBox.setText(str(vid_dict['star_rating']))

		if vid_dict['video_footage'] != '' and vid_dict['video_footage'] is not None:
			ftg_list = vid_dict['video_footage'].split('; ')
			self.videoFootageBox.addItems(ftg_list)

		self.artistBox.setText(vid_dict['song_artist'])
		self.artistBox.setCursorPosition(0)
		self.songTitleBox.setText(vid_dict['song_title'])
		self.songTitleBox.setCursorPosition(0)
		self.songGenreBox.setText(vid_dict['song_genre'])
		self.songGenreBox.setCursorPosition(0)

		length = vid_dict['video_length']
		if length != '' and length is not None:
			len_min = int(length / 60)
			len_sec = int(length % 60)
			self.lengthMinDrop.setCurrentIndex(len_min + 1)
			self.lengthSecDrop.setCurrentIndex(len_sec + 1)

		self.contestBox.setText(vid_dict['contests_entered'])
		self.awardsBox.setText(vid_dict['awards_won'])
		self.vidDescBox.setText(vid_dict['video_description'])

		if vid_dict['my_rating'] != '' and vid_dict['my_rating'] is not None:
			my_rating_ind = int((vid_dict['my_rating'] * 2) + 1)
			self.myRatingDrop.setCurrentIndex(my_rating_ind)

		if vid_dict['notable'] == 1:
			self.notableCheck.setChecked(True)

		if vid_dict['favorite'] == 1:
			self.favCheck.setChecked(True)

		self.tags1Box.setText(vid_dict['tags_1'])
		self.tags1Box.setCursorPosition(0)
		self.tags2Box.setText(vid_dict['tags_2'])
		self.tags2Box.setCursorPosition(0)
		self.tags3Box.setText(vid_dict['tags_3'])
		self.tags3Box.setCursorPosition(0)
		self.tags4Box.setText(vid_dict['tags_4'])
		self.tags4Box.setCursorPosition(0)
		self.tags5Box.setText(vid_dict['tags_5'])
		self.tags5Box.setCursorPosition(0)
		self.tags6Box.setText(vid_dict['tags_6'])
		self.tags6Box.setCursorPosition(0)

		self.commentsBox.setText(vid_dict['comments'])
		self.ytURLBox.setText(vid_dict['video_youtube_url'])
		self.ytURLBox.setCursorPosition(0)
		self.amvOrgURLBox.setText(vid_dict['video_org_url'])
		self.amvOrgURLBox.setCursorPosition(0)
		if self.amvOrgURLBox.text() != '':
			self.fetchOrgInfo.setEnabled(True)
		self.amvnewsURLBox.setText(vid_dict['video_amvnews_url'])
		self.amvnewsURLBox.setCursorPosition(0)
		self.otherURLBox.setText(vid_dict['video_other_url'])
		self.otherURLBox.setCursorPosition(0)
		self.localFileBox.setText(vid_dict['local_file'])
		self.localFileBox.setCursorPosition(0)
		self.thumbnailBox.setText(vid_dict['vid_thumb_path'])
		self.thumbnailBox.setCursorPosition(0)
		self.editorYTChannelBox.setText(vid_dict['editor_youtube_channel_url'])
		self.editorYTChannelBox.setCursorPosition(0)
		self.editorAMVOrgProfileBox.setText(vid_dict['editor_org_profile_url'])
		self.editorAMVOrgProfileBox.setCursorPosition(0)
		self.editorAmvnewsProfileBox.setText(vid_dict['editor_amvnews_profile_url'])
		self.editorAmvnewsProfileBox.setCursorPosition(0)
		self.editorOtherProfileBox.setText(vid_dict['editor_other_profile_url'])
		self.editorOtherProfileBox.setCursorPosition(0)

		for chk in self.listOfSubDBChecks:
			if chk.text() == subdb_friendly:
				chk.setChecked(True)
			else:
				chk.setChecked(False)
			chk.setDisabled(True)

		self.sequence = vid_dict['sequence']
		self.play_count = vid_dict['play_count']

		self.fetchProfilesButton.setEnabled(True)
		self.enable_yt_btns()
		self.enable_thumb_btns('yt')
		self.enable_thumb_btns('local')

	def check_for_existing_entry(self):
		cfee_conn = sqlite3.connect(common_vars.video_db())
		cfee_cursor = cfee_conn.cursor()
		
		ed_name = self.editorBox1.text().casefold()
		vid_title = self.titleBox.text().casefold()
		edit_sdb = None
		matching_subdbs = dict()

		if ed_name != '' and vid_title != '':
			for subdb in self.subDB_int_name_list:
				cfee_cursor.execute('SELECT video_id, primary_editor_username, video_title FROM {}'.format(subdb))
				for entry in cfee_cursor.fetchall():
					if entry[1].casefold() == ed_name and entry[2].casefold() == vid_title:
						matching_subdbs[common_vars.sub_db_lookup(reverse=True)[subdb]] = entry[0]

			if len(matching_subdbs) > 0:
				alert = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Video in database',
											  'This video has already been entered\ninto the following sub-db(s):\n\n{}\n\n'
											  'Would you like to edit this entry?'
											  .format('\n'.join(matching_subdbs)),
											  QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
				result = alert.exec_()

				if result == QtWidgets.QMessageBox.Yes:
					if len(matching_subdbs) > 1:  # If video exists in more than 1 sub-DB
						label_text = 'Please select which sub-DB\'s entry you want to\nedit:'
						window_title = 'Select sub-DB'
						sdb_list = [k for k, v in matching_subdbs.items()]
						dd_win = generic_dropdown.DropdownWindow(label_text, sdb_list, window_title)

						if dd_win.exec_():  # If user pushes "Select" button instead of "Close"
							edit_sdb = dd_win.dropdown.currentText()

					else:  # If video exists in only one sub-DB
						edit_sdb = list(matching_subdbs.keys())[0]

					if edit_sdb:
						edit_sdb_int = common_vars.sub_db_lookup()[edit_sdb]
						self.entry = VideoEntry(edit_entry=True, inp_vidid=matching_subdbs[edit_sdb],
												inp_subdb=edit_sdb_int)
						self.entry.show()
						self.close()

		cfee_conn.close()

	def editor_1_text_changed(self):
		if self.editorBox1.text() != '':
			self.editorBox2.setEnabled(True)
			self.MEPlabel.setHidden(False)
			self.fetchProfilesButton.setEnabled(True)
		else:
			self.editorBox2.setDisabled(True)
			self.MEPlabel.setHidden(True)
			self.fetchProfilesButton.setDisabled(True)

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
		month_len = {'01 (Jan)': 31,
					 '02 (Feb)': 28,
					 '03 (Mar)': 31,
					 '04 (Apr)': 30,
					 '05 (May)': 31,
					 '06 (Jun)': 30,
					 '07 (Jul)': 31,
					 '08 (Aug)': 31,
					 '09 (Sep)': 30,
					 '10 (Oct)': 31,
					 '11 (Nov)': 30,
					 '12 (Dec)': 31}

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

			if float(self.starRatingBox.text()) > 5 or float(self.starRatingBox.text()) < 0:
				star_rating_range_error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
																'Star rating must be a number\nbetween 0 and 5.')
				star_rating_range_error.exec_()
				self.starRatingBox.clear()
				self.starRatingBox.setFocus()

		except:
			star_rating_type_error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
														   'Star rating must be a number\nbetween 0 and 5.')
			star_rating_type_error.exec_()
			self.starRatingBox.clear()
			self.starRatingBox.setFocus()

	def enable_add_ftg_btn(self):
		if self.videoSearchBox.text() != '':
			self.addFootage.setEnabled(True)
		else:
			self.addFootage.setDisabled(True)

	def enable_remove_ftg_btn(self):
		if len(self.videoFootageBox.selectedItems()) != 0:
			self.removeFootage.setEnabled(True)
		else:
			self.removeFootage.setDisabled(True)

	def add_video_ftg(self):
		sel_ftg = [self.videoFootageBox.item(f).text() for f in range(self.videoFootageBox.count())]
		self.videoFootageBox.clear()

		if self.videoSearchBox.text() not in sel_ftg:
			sel_ftg.append(self.videoSearchBox.text())

		sel_ftg.sort(key=lambda x: x.casefold())
		for ftg in sel_ftg:
			self.videoFootageBox.addItem(ftg)

		self.videoSearchBox.clear()
		self.videoSearchBox.setFocus()

	def remove_video_ftg(self):
		ftg_in_box = [self.videoFootageBox.item(f).text() for f in range(self.videoFootageBox.count())]
		ftg_in_box.remove(self.videoFootageBox.currentItem().text())
		self.videoFootageBox.clear()

		for ftg in ftg_in_box:
			self.videoFootageBox.addItem(ftg)

		self.videoSearchBox.setFocus()

	def tag_window(self, tag_type, tag_box):
		tag_win = tag_checkboxes.TagWindow(tag_type, checked_tags=tag_box.text())
		if tag_win.exec_():
			tag_box.setText(tag_win.out_str[:-2])

	def enable_yt_btns(self):
		if self.editorBox1.text() != '' and self.titleBox.text() != '':
			self.searchYTButton.setEnabled(True)
		else:
			self.searchYTButton.setDisabled(True)

		if ('youtube.com' in self.ytURLBox.text() or 'youtu.be' in self.ytURLBox.text()) and 'watch?v=' in \
				self.ytURLBox.text():
			self.fetchYTInfo.setEnabled(True)
			self.YTDLButton.setEnabled(True)
		else:
			self.fetchYTInfo.setDisabled(True)
			self.YTDLButton.setDisabled(True)

	def search_youtube(self):
		search_query = self.editorBox1.text().replace(' ', '+') + '+' + self.titleBox.text().replace(' ', '+') + '+' + \
			'amv'
		webbrowser.open('https://www.youtube.com/results?search_query={}'.format(search_query))

	def fetch_youtube_info(self):
		if check_for_internet_conn.internet_check('https://www.youtube.com'):
			info = fetch_vid_info.download_data(self.ytURLBox.text(), 'youtube')
			self.editorBox1.setText(info['primary_editor_username'])
			self.titleBox.setText(info['video_title'])
			self.artistBox.setText(info['song_artist'])
			self.songTitleBox.setText(info['song_title'])

			year = info['release_date'][0:4]
			month_ind = int(info['release_date'][5:7]) - 1
			day_ind = int(info['release_date'][8:10]) - 1

			self.dateYear.setCurrentText(year)
			self.dateMonth.setCurrentIndex(month_ind)
			self.dateDay.setCurrentIndex(day_ind)

			dur_min = info['video_length'] // 60
			dur_sec = info['video_length'] % 60

			self.lengthMinDrop.setCurrentText(str(dur_min))
			self.lengthSecDrop.setCurrentText(str(dur_sec))

			self.vidDescBox.setText(info['video_description'])
			self.editorYTChannelBox.setText(info['editor_youtube_channel_url'])

		else:
			yt_unresolved_host_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'No response',
														'YouTube is currently unresponsive. Check your\n'
														'internet connection or try again later.')
			yt_unresolved_host_win.exec_()

	def dl_yt_vid(self):
		# TODO: Video still downloads if user clicks no
		yt = pytube.YouTube(self.ytURLBox.text())
		vid_editor = yt.author
		vid_title = yt.title
		full_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '{} - {}.mp4'
														  .format(vid_editor, vid_title))
		dir_path = '/'.join(full_path[0].replace('\\', '/').split('/')[:-1])
		fname = full_path[0].replace('\\', '/').split('/')[-1]

		dl_yt_win = download_yt_video.DownloadFromYT(self.ytURLBox.text(), dir_path, fname)
		if dl_yt_win.exec_():
			self.localFileBox.setText(full_path[0])

	def en_dis_org_btns(self):
		if 'members_videoinfo.php?v' in self.amvOrgURLBox.text():
			self.fetchOrgInfo.setEnabled(True)
		else:
			self.fetchOrgInfo.setDisabled(True)

		if self.editorBox1.text() != '' and self.titleBox.text() != '':
			self.searchOrgButton.setEnabled(True)
		else:
			self.searchOrgButton.setDisabled(True)

	def search_org(self):
		ed_name = self.editorBox1.text().replace(' ', '+')
		vid_title = self.titleBox.text().replace(' ', '+')
		webbrowser.open('https://www.animemusicvideos.org/search/supersearch.php?anime_criteria=&artist_criteria=&'
						'song_criteria=&member_criteria={}&studio_criteria=&spread=less&title={}&comments=&download='
						'&con=&year=&format_id=&o=7&d=1&recent=on&go=go#results'
						.format(ed_name, vid_title))

	def fetch_org_info(self):
		if check_for_internet_conn.internet_check('https://www.animemusicvideos.org'):
			info = fetch_vid_info.download_data(self.amvOrgURLBox.text(), 'org')
			self.editorBox1.setText(info['primary_editor_username'])
			self.editorBox2.setText(info['addl_editors'])
			self.studioBox.setText(info['studio'])
			self.titleBox.setText(info['video_title'])

			if info['release_date'][1] == 0 or info['release_date'][2] == 0:
				self.dateUnk.setChecked(True)
				self.dateYear.setDisabled(True)
			else:
				self.dateYear.setCurrentText(info['release_date'][0])
				self.dateMonth.setCurrentIndex(info['release_date'][1])
				self.dateDay.setCurrentIndex(info['release_date'][2])

			self.videoFootageBox.clear()
			for anime in info['video_footage']:
				self.videoFootageBox.addItem(anime)

			self.artistBox.setText(info['song_artist'])
			self.songTitleBox.setText(info['song_title'])

			self.lengthMinDrop.setCurrentIndex(info['video_length'][0] + 1)
			self.lengthSecDrop.setCurrentIndex(info['video_length'][1] + 1)

			self.contestBox.setText(info['contests_entered'].replace('; ', '\n'))
			self.vidDescBox.setText(info['video_description'])
			self.ytURLBox.setText(info['video_youtube_url'])
			self.amvnewsURLBox.setText(info['video_amvnews_url'])
			self.otherURLBox.setText(info['video_other_url'])
			self.editorAMVOrgProfileBox.setText(info['editor_org_profile_url'])

		else:
			unresolved_host_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'No response',
														'AnimeMusicVideos.org is currently unresponsive. Check your\n'
														'internet connection or try again later.')
			unresolved_host_win.exec_()

	def fetch_vid_desc(self):
		if check_for_internet_conn.internet_check('https://www.animemusicvideos.org'):
			r = requests.get(self.amvOrgURLBox.text())
			soup = beautifulsoup(r.content, 'html5lib')
			vid_desc_html = soup.find('span', attrs={'class': 'comments'})
			self.vidDescBox.setText(vid_desc_html.get_text().strip())

			fetch_succ_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Description fetched',
												   'Video description has been successfully fetched and inserted\n'
												   'into the Video Description field on the Video Information tab.')
			fetch_succ_win.exec_()

		else:
			unresolved_host_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'No response',
														'AnimeMusicVideos.org is currently unresponsive. Check your\n'
														'internet connection or try again later.')
			unresolved_host_win.exec_()

	def local_file_clicked(self):
		file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a file')
		if file_path[0]:
			self.localFileBox.setText(file_path[0])

	def thumbnail_clicked(self):
		file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a thumbnail', '',
														  'Image files (*.png *.jpg *.jpeg *.bmp)')
		if file_path[0]:
			self.thumbnailBox.setText(file_path[0])

	def enable_thumb_btns(self, btn):
		if btn == 'yt':
			if 'yout' in self.ytURLBox.text() and 'watch?' in self.ytURLBox.text():
				self.thumbnailDLButton.setEnabled(True)
			else:
				self.thumbnailDLButton.setDisabled(True)

		elif btn == 'local':
			if self.localFileBox.text() != '':
				self.thumbnailGenButton.setEnabled(True)
			else:
				self.thumbnailGenButton.setDisabled(True)

		else:
			print('something went wrong')

	def delete_thumb_path(self):
		if self.thumbnailBox.text() != '':
			delete_thumb_msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Delete thumbnail file?',
													 'Do you want to delete the thumbnail file as well? If you select No,\n'
													 'the file path will be cleared from the box but the image file itself\n'
													 'will not be removed.',
													 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
			delete_thumb_response = delete_thumb_msg.exec_()

			if delete_thumb_response == QtWidgets.QMessageBox.Yes:
				if os.path.exists(self.thumbnailBox.text()):
					os.remove(self.thumbnailBox.text())

			self.thumbnailBox.clear()

	def dl_thumb(self):
		connected = check_for_internet_conn.internet_check('https://www.youtube.com/')

		if connected:
			thumb_path = download_yt_thumb.download(self.vidid, self.ytURLBox.text())
			if thumb_path == 'no action':
				pass
			elif thumb_path != 'failed':
				self.thumbnailBox.setText(thumb_path)
			else:
				failed_to_dl = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Download failed',
													 'AMV Tracker was unable to download this thumbnail. The video may\n'
													 'no longer be available, or the provided URL is incorrect.')
				failed_to_dl.exec_()

		else:
			no_internet_err = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'No internet connection',
													'You must be connected to the Internet to use this function. Check\n'
													'your connection and try again; alternatively, YouTube may be down at\n'
													'this time.')
			no_internet_err.exec_()

	def generate_thumb(self):
		ffmpeg_exists = check_for_ffmpeg.check()
		temp_thumb_dir = getcwd() + '\\thumbnails\\temp'
		new_thumb_path = common_vars.thumb_path() + '\\{}.jpg'.format(self.vidid)
		ok_to_proceed = True

		if not os.path.isfile(self.localFileBox.text()):
			no_video_file_popup = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Video file does not exist',
														'The file does not exist at the specified local file path. Please\n'
														'select a valid video file by clicking on the "Local file" button.')
			no_video_file_popup.exec_()
			ok_to_proceed = False

		if mimetypes.guess_type(self.localFileBox.text())[0] is None or \
				mimetypes.guess_type(self.localFileBox.text())[0].startswith('video') is False:
			not_a_video_popup = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Incorrect filetype',
													  'The file indicated in the "Local file" box is not a video file;\n'
													  'therefore no thumbnails can be generated.')
			not_a_video_popup.exec_()
			ok_to_proceed = False

		if os.path.isfile(new_thumb_path):
			thumb_exists_popup = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Overwrite thumbnail?',
													   'A thumbnail already exists for this video. OK to '
													   'overwrite?',
													   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
			result = thumb_exists_popup.exec_()

			if result == QtWidgets.QMessageBox.No:
				ok_to_proceed = False

		if ffmpeg_exists:
			file_path = self.localFileBox.text()

			if ok_to_proceed:
				thumb_win = mult_thumb_generator.ThumbnailDialog(file_path, self.vidid)

				if thumb_win.exec_():
					thumb_ind = str(thumb_win.slider.sliderPosition())

					# Copy selected thumbnail from temp folder to thumbnails folder
					copy(temp_thumb_dir + '\\{}-{}.jpg'.format(self.vidid, thumb_ind), new_thumb_path)

					# Update thumbnail text box
					self.thumbnailBox.setText(new_thumb_path)

		else:
			ffmpeg_needed = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'FFMPEG needed',
												  'In order to use this function you will need FFMPEG. Please follow<br>'
												  'the below instructions:<br><br>'
												  '1. Download the latest full build from '
												  '<a href="https://www.gyan.dev/ffmpeg/builds/">here</a>.<br><br>'
												  '2. Open the archive, navigate to the bin folder, and put the ffmpeg.exe<br>'
												  'and ffprobe.exe files in your AMV Tracker directory.<br><br>'
												  '3. That\'s it! Close this window and press the "Generate thumbnail"<br> '
												  'button again.')
			ffmpeg_needed.exec_()

		# Delete all files in temp folder
		for f in os.listdir(temp_thumb_dir):
			os.remove(os.path.join(temp_thumb_dir, f))

	def fetch_profiles(self):
		link_profiles_conn = sqlite3.connect(common_vars.video_db())
		link_profiles_cursor = link_profiles_conn.cursor()
		editor_name = self.editorBox1.text()
		subdb_list = [v for k, v in common_vars.sub_db_lookup().items()]
		url_list = ['editor_youtube_channel_url', 'editor_org_profile_url', 'editor_amvnews_profile_url',
					'editor_other_profile_url']
		url_dict = {link: [] for link in url_list}

		for subdb in subdb_list:
			for url in url_list:

				link_profiles_cursor.execute(
					'SELECT {} FROM {} WHERE primary_editor_username = "{}"'.format(url, subdb, editor_name))
				x = link_profiles_cursor.fetchall()
				if x:
					temp_list = [item[0] for item in x if (item[0] is not None and item[0] != '')]
					temp_list.sort(key=lambda x: x.lower())
					url_dict[url] += temp_list

		if url_dict['editor_youtube_channel_url']:
			self.editorYTChannelBox.setText(url_dict['editor_youtube_channel_url'][0])
			self.editorYTChannelBox.setCursorPosition(0)
		else:
			self.editorYTChannelBox.clear()

		if url_dict['editor_org_profile_url']:
			self.editorAMVOrgProfileBox.setText(url_dict['editor_org_profile_url'][0])
			self.editorAMVOrgProfileBox.setCursorPosition(0)
		else:
			self.editorAMVOrgProfileBox.clear()

		if url_dict['editor_amvnews_profile_url']:
			self.editorAmvnewsProfileBox.setText(url_dict['editor_amvnews_profile_url'][0])
			self.editorAmvnewsProfileBox.setCursorPosition(0)
		else:
			self.editorAmvnewsProfileBox.clear()

		if url_dict['editor_other_profile_url']:
			self.editorOtherProfileBox.setText(url_dict['editor_other_profile_url'][0])
			self.editorOtherProfileBox.setCursorPosition(0)
		else:
			self.editorOtherProfileBox.clear()

		link_profiles_conn.close()

	def copy_video(self, vidid, subdb):
		self.copy_win = copy_move.CopyMoveWindow(vidid, subdb, copy=True)
		self.copy_win.show()

	# noinspection PyTypedDict
	def submit_button_clicked(self):
		# Checks to make sure data is entered correctly
		submit_conn = sqlite3.connect(common_vars.video_db())
		submit_cursor = submit_conn.cursor()
		
		## Get list of sub-dbs to enter video into ##
		checked_sub_dbs = [chk.text() for chk in self.listOfSubDBChecks if chk.isChecked()]
		checked_sub_dbs_str = ''
		subdb_dict = common_vars.sub_db_lookup()

		## Get list of Custom Lists to enter video into ##
		checked_cls = [self.tab_4_scrollvLayout2.itemAt(wid_ind).widget().text() for wid_ind in
					   range(1, self.tab_4_scrollvLayout2.count()) if
					   self.tab_4_scrollvLayout2.itemAt(wid_ind).widget().isChecked()]
		checked_cls_str = ''
		cl_dict = common_vars.custom_list_lookup()

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

			if self.entry_settings['check_video_footage'] == 1 and self.videoFootageBox.count() == 0:
				missing_fields_list.append('\u2022 Video footage')

			if self.entry_settings['check_song_artist'] == 1 and self.artistBox.text() == '':
				missing_fields_list.append('\u2022 Song artist')

			if self.entry_settings['check_song_title'] == 1 and self.songTitleBox.text() == '':
				missing_fields_list.append('\u2022 Song title')

			if self.entry_settings['check_song_genre'] == 1 and self.songGenreBox.text() == '':
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
													 '\nPlease fill in these fields before submitting.\n\n'
													 'You can change the required fields needed to submit\n'
													 'on the "Video entry" tab in the program settings, or\n'
													 'you can uncheck the "Checks enabled" option on the\n'
													 '"Submission rules" tab here to bypass this check.\n\n'
													 'Please note that editor username and video title are\n'
													 'required fields even if checks are disabled.')
			entry_error_data.exec_()

		elif len(checked_sub_dbs) == 0:  # If no sub-dbs are selected
			entry_error_subdb = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
													  'You must select at least one sub-database to\n'
													  'submit this video entry to (see "Submission\n'
													  'rules" tab).')
			entry_error_subdb.exec_()

		else:  # Data is good -- put video in database
			# Get sequence
			seq_dict = {}
			for subdb in checked_sub_dbs:
				subdb_formatted = subdb_dict[subdb]
				submit_cursor.execute('SELECT COUNT(*) FROM {}'.format(subdb_formatted))
				num_rows = submit_cursor.fetchall()
				if num_rows[0][0] == 0:
					seq_dict[subdb_formatted] = 1
				else:
					submit_cursor.execute('SELECT sequence FROM {} WHERE sequence IS NOT NULL AND sequence != ""'
											  .format(subdb_formatted))
					seq_list = [x[0] for x in submit_cursor.fetchall()]
					if not seq_list:
						seq_list = [0]
					seq_dict[subdb_formatted] = max(seq_list) + 1

			# Get pseudonyms from editor's existing entries and update this entry with them
			ed_name = self.editorBox1.text()
			pseud_list = self.pseudoBox.text().split('; ')
			for subdb in checked_sub_dbs:
				subdb_formatted = subdb_dict[subdb]
				submit_cursor.execute('SELECT primary_editor_pseudonyms FROM {} WHERE primary_editor_username = ?'
										  .format(subdb_formatted), (ed_name,))

			all_pseuds = submit_cursor.fetchall()
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
			output_dict = dict()  # Use of this dict takes advantage of Python 3.7+'s feature of preserving insertion order

			output_dict['video_id'] = self.vidid
			output_dict['primary_editor_username'] = self.editorBox1.text()
			if self.entry_settings['link_pseudonyms'] == 0 or self.edit_entry:
				output_dict['primary_editor_pseudonyms'] = self.pseudoBox.text()
			else:
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
				output_dict['release_date'] = self.dateYear.currentText() + '/' + self.dateMonth.currentText()[:2] + \
											  '/' + date_day

			if self.dateUnk.isChecked():
				output_dict['release_date_unknown'] = 1
			else:
				output_dict['release_date_unknown'] = 0

			if self.starRatingBox.text() != '':
				output_dict['star_rating'] = float(self.starRatingBox.text())
			else:
				output_dict['star_rating'] = ''

			video_footage = [self.videoFootageBox.item(f).text() for f in range(self.videoFootageBox.count())]
			video_footage_str = ''
			if video_footage:
				for ftg in video_footage:
					video_footage_str += ftg + '; '
				output_dict['video_footage'] = video_footage_str[:-2]
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
			output_dict['sequence'] = self.sequence  # Sequence is handled in update_video_entry.py for new entries

			current_date = common_vars.current_date()

			if not self.edit_entry:
				output_dict['date_entered'] = current_date
			else:
				submit_cursor.execute('SELECT date_entered FROM {} WHERE video_id = ?'.format(self.inp_subdb),
										(self.inp_vidid,))
				entry_date = submit_cursor.fetchone()[0]
				output_dict['date_entered'] = entry_date

			output_dict['play_count'] = self.play_count
			output_dict['vid_thumb_path'] = self.thumbnailBox.text()

			if not self.edit_entry:
				output_dict['sub_db'] = ''
			else:
				output_dict['sub_db'] = self.inp_subdb

			## Add video to sub-dbs ##
			if self.edit_entry:
				update_video_entry.update_video_entry(output_dict, checked_sub_dbs, vid_id=self.inp_vidid)
			else:
				update_video_entry.update_video_entry(output_dict, checked_sub_dbs, seq_dict=seq_dict)

			for subdb in checked_sub_dbs:
				checked_sub_dbs_str += '\u2022 ' + subdb + '\n'

			# Update editor's existing entries with any new pseudonyms added
			if self.entry_settings['link_pseudonyms'] == 1:
				for uf_name, int_name in subdb_dict.items():
					submit_cursor.execute(
						'UPDATE {} SET primary_editor_pseudonyms = ? WHERE primary_editor_username = ?'
							.format(int_name), (pseud_str, ed_name))

					for p in pseud_str.split('; '):
						list_of_names = pseud_str.split('; ')
						new_list = [ed_name if x == p else x for x in list_of_names]
						new_pseud_str = '; '.join(new_list)
						submit_cursor.execute(
							'UPDATE {} SET primary_editor_pseudonyms = ? WHERE primary_editor_username = ?'
								.format(int_name), (new_pseud_str, p))

				submit_conn.commit()

			entry_submitted = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Video submitted',
													'{title} has been successfully submitted to the\nfollowing '
													'sub-db(s):\n\n'
													'{subdbs}'.format(title=output_dict['video_title'],
																	  subdbs=checked_sub_dbs_str))
			entry_submitted.exec_()

			# Add entry to selected Custom Lists
			if checked_cls:
				for cl_name in checked_cls:
					submit_cursor.execute('SELECT vid_ids FROM custom_lists WHERE list_name = ?', (cl_name,))
					vid_ids_str = submit_cursor.fetchone()[0]
					if self.vidid not in vid_ids_str:
						if vid_ids_str != '':
							vid_ids_str += '; ' + self.vidid
						else:
							vid_ids_str = self.vidid

					submit_cursor.execute('UPDATE custom_lists SET vid_ids = ? WHERE list_name = ?', (vid_ids_str,
																										  cl_name))
					submit_conn.commit()

					checked_cls_str += '\u2022 ' + cl_name + '\n'

				added_to_cls_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Added to Custom List(s)',
														 '{title} has been successfully added to the\nfollowing '
														 'Custom List(s):\n\n'
														 '{cls}'.format(title=output_dict['video_title'],
																		cls=checked_cls_str))
				added_to_cls_win.exec_()

			submit_conn.close()
			self.update_list_signal.emit()
			self.close()
