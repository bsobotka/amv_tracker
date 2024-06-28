import itertools
import mimetypes
import os
import time

import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import pytube
import requests
import sqlite3
import webbrowser

from bs4 import BeautifulSoup
from main_window import copy_move
from os import getcwd, startfile
from random import randint
from shutil import copy
from urllib import parse

from fetch_video_info import fetch_vid_info
from misc_files import check_for_db, check_for_ffmpeg, check_for_internet_conn, check_for_thumb_path, common_vars, \
	download_yt_thumb, download_yt_video, fetch_video_length, generate_thumb, generic_dropdown, generic_entry_window, \
	mult_thumb_generator, tag_checkboxes
from video_entry import addl_editors, update_video_entry


class CustomLineEdit(QtWidgets.QLineEdit):
	"""
	Custom QLineEdit class to capture a mouse double-click event (used for showing full list from QCompleter)
	"""
	doubleClicked = QtCore.pyqtSignal()

	def event(self, ev):
		if ev.type() == QtCore.QEvent.Type.MouseButtonDblClick:
			self.doubleClicked.emit()

		return super().event(ev)


class VideoEntry(QtWidgets.QMainWindow):
	update_list_signal = QtCore.pyqtSignal()

	def __init__(self, edit_entry=False, inp_vidid=None, inp_subdb=None):
		"""
		Window used to enter new videos into the database.
		:param edit_entry: If True, this window will open in "edit mode", with fields auto-populated from chosen entry.
		:param inp_vidid: For edit mode. Specifies which video is to be edited.
		:param inp_subdb: For edit mode. Specifies which sub-DB the video can be found in.
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
		self.input_field_dict = dict()

		# Initialize settings dict
		self.entry_settings = {}
		settings_cursor.execute('SELECT * FROM entry_settings')
		self.entry_settings_list = settings_cursor.fetchall()
		for pair in self.entry_settings_list:
			try:
				self.entry_settings[pair[0]] = int(pair[1])
			except:
				self.entry_settings[pair[0]] = pair[1]

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
		self.editorBox1 = CustomLineEdit()
		self.editorBox1.setFixedWidth(200)
		self.input_field_dict['primary_editor_username'] = self.editorBox1

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
		self.pseudoBox = CustomLineEdit()
		self.pseudoBox.setFixedWidth(200)
		self.pseudoBox.setPlaceholderText('Ex: username1; username2; ...')
		self.pseudoBox.setCompleter(self.editorNameCompleter)
		self.input_field_dict['primary_editor_pseudonyms'] = self.pseudoBox

		tab_1_grid_L.addWidget(self.pseudoLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.pseudoBox, grid_1_L_vert_ind, 1, 1, 6)

		grid_1_L_vert_ind += 1

		# Addl editors + MEP text
		self.addlEditorsLabel = QtWidgets.QLabel()
		self.addlEditorsLabel.setText('Addl. editor(s):')
		self.editorBox2 = QtWidgets.QLineEdit()
		self.editorBox2.setFixedWidth(200)
		self.input_field_dict['addl_editors'] = self.editorBox2

		self.MEPfont = QtGui.QFont()
		self.MEPfont.setUnderline(True)
		self.MEPlabel = QtWidgets.QLabel()
		self.MEPlabel.setText('<font color="blue">2+ editors</font>')
		self.MEPlabel.setFont(self.MEPfont)
		self.MEPlabel.setToolTip('Click to insert multiple additional editor\n'
								 'usernames.')

		self.editorBox2.setDisabled(True)
		self.MEPlabel.setHidden(True)

		tab_1_grid_L.addWidget(self.addlEditorsLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.editorBox2, grid_1_L_vert_ind, 1, 1, 6)
		tab_1_grid_L.addWidget(self.MEPlabel, grid_1_L_vert_ind, 7, 1, 5)

		grid_1_L_vert_ind += 1

		# Studio
		self.studioLabel = QtWidgets.QLabel()
		self.studioLabel.setText('Studio:')
		self.studioBox = CustomLineEdit()
		self.studioBox.setFixedWidth(200)
		self.input_field_dict['studio'] = self.studioBox

		self.studioList = []
		for table in self.subDB_int_name_list:
			subDB_cursor.execute('SELECT studio FROM {}'.format(table))
			for studio_name in subDB_cursor.fetchall():
				if studio_name[0] != '' and studio_name[0].casefold() not in (s.casefold() for s in self.studioList):
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
		self.input_field_dict['video_title'] = self.titleBox

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
		self.input_field_dict['release_date'] = [self.dateYear, self.dateMonth, self.dateDay]
		self.input_field_dict['release_date_unknown'] = self.dateUnk

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
		self.input_field_dict['star_rating'] = self.starRatingBox

		tab_1_grid_L.addWidget(self.starRatingLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.starRatingBox, grid_1_L_vert_ind, 1, 1, 3)

		grid_1_L_vert_ind += 1

		# Video Footage 1
		self.videoFootageLabel = QtWidgets.QLabel()
		self.videoFootageLabel.setText('Video footage used:')
		self.videoFootageBox = QtWidgets.QListWidget()
		self.videoFootageBox.setFixedSize(200, 120)

		self.videoSearchBox = CustomLineEdit()
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
						if ftg.casefold() not in (f.casefold() for f in self.footageList):
							self.footageList.append(ftg)

		self.footageListSorted = list(set(self.footageList))
		self.footageListSorted.sort(key=lambda x: x.casefold())

		self.footageCompleter = QtWidgets.QCompleter(self.footageListSorted)
		self.footageCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.footageCompleter.setMaxVisibleItems(15)
		self.videoSearchBox.setCompleter(self.footageCompleter)
		self.input_field_dict['video_footage'] = self.videoFootageBox

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
		self.artistBox = CustomLineEdit()
		self.artistBox.setFixedWidth(200)
		self.input_field_dict['song_artist'] = self.artistBox

		self.artistList = []
		for tn in self.subDB_int_name_list:
			subDB_cursor.execute('SELECT song_artist FROM {}'.format(tn))
			for artist in subDB_cursor.fetchall():
				if artist[0] != '' and artist[0].casefold() not in (a.casefold() for a in self.artistList):
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
		self.input_field_dict['song_title'] = self.songTitleBox

		tab_1_grid_L.addWidget(self.songTitleLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.songTitleBox, grid_1_L_vert_ind, 1, 1, 6)

		grid_1_L_vert_ind += 1

		# Song genre
		self.songGenreLabel = QtWidgets.QLabel()
		self.songGenreLabel.setText('Song genre:')
		self.songGenreBox = CustomLineEdit()
		self.songGenreBox.setFixedWidth(200)
		self.input_field_dict['song_genre'] = self.songGenreBox

		self.genreList = []
		for subDB in self.subDB_int_name_list:
			subDB_cursor.execute('SELECT song_genre FROM {}'.format(subDB))
			for genre in subDB_cursor.fetchall():
				if genre[0].casefold() not in (g.casefold() for g in self.genreList) and genre[0] != '':
					self.genreList.append(genre[0])

		self.genreList.sort(key=lambda x: x.casefold())
		self.genreList.insert(0, '')

		self.songGenreCompleter = QtWidgets.QCompleter(self.genreList)
		self.songGenreCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.songGenreCompleter.setMaxVisibleItems(15)
		self.songGenreBox.setCompleter(self.songGenreCompleter)

		self.songGenreQuestion = QtWidgets.QLabel()
		self.songGenreQuestion.setText('<font color="blue">[?]</font>')
		self.songGenreQuestion.setToolTip('If you are unsure what genre the song is, click here\n'
										  'to execute a search for this artist on RateYourMusic,\n'
										  'which should provide guidance on selecting a genre\n'
										  '(song artist field must be filled in).')

		tab_1_grid_L.addWidget(self.songGenreLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.songGenreBox, grid_1_L_vert_ind, 1, 1, 6)
		tab_1_grid_L.addWidget(self.songGenreQuestion, grid_1_L_vert_ind, 7)

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
		self.input_field_dict['video_length'] = [self.lengthMinDrop, self.lengthSecDrop]

		tab_1_grid_L.addWidget(self.lengthLabel, grid_1_L_vert_ind, 0)
		tab_1_grid_L.addWidget(self.lengthMinDrop, grid_1_L_vert_ind, 1)
		tab_1_grid_L.addWidget(self.lengthMinLabel, grid_1_L_vert_ind, 2, 1, 2)
		tab_1_grid_L.addWidget(self.lengthSecDrop, grid_1_L_vert_ind, 3)
		tab_1_grid_L.addWidget(self.lengthSecLabel, grid_1_L_vert_ind, 4, 1, 2)

		grid_1_L_vert_ind += 1

		## Tab 1 - Right grid ##
		tab_1_grid_R = QtWidgets.QGridLayout()
		tab_1_grid_R.setAlignment(QtCore.Qt.AlignRight)
		grid_1_R_vert_ind = 0

		# Contests
		self.contestLabel = QtWidgets.QLabel()
		self.contestLabel.setText('Contests entered:')
		self.contestBox = QtWidgets.QTextEdit()
		self.contestBox.setFixedSize(260, 80)
		self.input_field_dict['contests_entered'] = self.contestBox

		tab_1_grid_R.addWidget(self.contestLabel, grid_1_R_vert_ind, 0, alignment=QtCore.Qt.AlignTop)
		tab_1_grid_R.addWidget(self.contestBox, grid_1_R_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		grid_1_R_vert_ind += 1

		# Awards
		self.awardsLabel = QtWidgets.QLabel()
		self.awardsLabel.setText('Awards won:')
		self.awardsBox = QtWidgets.QTextEdit()
		self.awardsBox.setFixedSize(260, 80)
		self.input_field_dict['awards_won'] = self.awardsBox

		tab_1_grid_R.addWidget(self.awardsLabel, grid_1_R_vert_ind, 0, alignment=QtCore.Qt.AlignTop)
		tab_1_grid_R.addWidget(self.awardsBox, grid_1_R_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		grid_1_R_vert_ind += 1

		# Video description
		self.vidDescLabel = QtWidgets.QLabel()
		self.vidDescLabel.setText('Video description:')
		self.vidDescBox = QtWidgets.QTextEdit()
		self.vidDescBox.setFixedSize(260, 350)
		self.input_field_dict['description'] = self.vidDescBox

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
		self.input_field_dict['my_rating'] = self.myRatingDrop

		myRatingList = [rat * 0.5 for rat in range(0, 21)]

		self.myRatingDrop.addItem('')
		for rating in myRatingList:
			self.myRatingDrop.addItem(str(rating))

		tab_2_grid.addWidget(self.myRatingLabel, grid_2_vert_ind, 0, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.myRatingDrop, grid_2_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Notable checkbox
		self.notableCheck = QtWidgets.QCheckBox('Notable')
		self.input_field_dict['notable'] = self.notableCheck
		tab_2_grid.addWidget(self.notableCheck, grid_2_vert_ind, 0, 1, 2, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Favorite checkbox
		self.favCheck = QtWidgets.QCheckBox('Favorite')
		self.input_field_dict['favorite'] = self.favCheck
		tab_2_grid.addWidget(self.favCheck, grid_2_vert_ind, 0, 1, 2, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		tab_2_grid.setRowMinimumHeight(grid_2_vert_ind, 10)
		grid_2_vert_ind += 1

		# Apply custom logic
		self.applyLogicBtn = QtWidgets.QPushButton('Apply custom logic')
		self.applyLogicBtn.setFixedWidth(170)
		self.applyLogicBtn.setDisabled(True)
		self.applyLogicBtn.setToolTip('If you have defined custom tag logic in [Settings > Video entry],\n'
									  'press this button to apply those rules here. Please note that if\n'
									  'you have entered any tags before clicking this button, ALL tag\n'
									  'boxes will be overwritten based on the logic.\n\n'
									  'If this button is disabled, you either haven\'t defined any custom\n'
									  'logic rules, or all rules you have defined are disabled.')
		tab_2_grid.addWidget(self.applyLogicBtn, grid_2_vert_ind, 0, 1, 2)
		grid_2_vert_ind += 1

		# Tags 1
		self.tags1Button = QtWidgets.QPushButton(self.tag_list_names[0])
		self.tags1Button.setFixedWidth(170)

		self.tags1Box = QtWidgets.QLineEdit()
		self.tags1Box.setPlaceholderText('<-- Click to select tags')
		self.tags1Box.setFixedWidth(530)
		self.tags1Box.setReadOnly(True)
		self.tags1Add = QtWidgets.QPushButton('+')
		self.tags1Add.setFixedWidth(20)
		self.tags1Add.setToolTip('Add new tag to this tag group')
		self.tags1X = QtWidgets.QPushButton('X')
		self.tags1X.setFixedWidth(20)
		self.tags1X.setToolTip('Clear tags')
		self.input_field_dict['tags_1'] = self.tags1Box

		tab_2_grid.addWidget(self.tags1Button, grid_2_vert_ind, 0, 1, 2)
		tab_2_grid.addWidget(self.tags1Box, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags1Add, grid_2_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags1X, grid_2_vert_ind, 4, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Tags 2
		self.tags2Button = QtWidgets.QPushButton(self.tag_list_names[1])
		self.tags2Button.setFixedWidth(170)
		self.tags2Box = QtWidgets.QLineEdit()
		self.tags2Box.setPlaceholderText('<-- Click to select tags')
		self.tags2Box.setFixedWidth(530)
		self.tags2Box.setReadOnly(True)
		self.tags2Add = QtWidgets.QPushButton('+')
		self.tags2Add.setFixedWidth(20)
		self.tags2Add.setToolTip('Add new tag to this tag group')
		self.tags2X = QtWidgets.QPushButton('X')
		self.tags2X.setFixedWidth(20)
		self.tags2X.setToolTip('Clear tags')
		self.input_field_dict['tags_2'] = self.tags2Box

		tab_2_grid.addWidget(self.tags2Button, grid_2_vert_ind, 0, 1, 2)
		tab_2_grid.addWidget(self.tags2Box, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags2Add, grid_2_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags2X, grid_2_vert_ind, 4, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Tags 3
		self.tags3Button = QtWidgets.QPushButton(self.tag_list_names[2])
		self.tags3Button.setFixedWidth(170)
		self.tags3Box = QtWidgets.QLineEdit()
		self.tags3Box.setPlaceholderText('<-- Click to select tags')
		self.tags3Box.setFixedWidth(530)
		self.tags3Box.setReadOnly(True)
		self.tags3Add = QtWidgets.QPushButton('+')
		self.tags3Add.setFixedWidth(20)
		self.tags3Add.setToolTip('Add new tag to this tag group')
		self.tags3X = QtWidgets.QPushButton('X')
		self.tags3X.setFixedWidth(20)
		self.tags3X.setToolTip('Clear tags')
		self.input_field_dict['tags_3'] = self.tags3Box

		tab_2_grid.addWidget(self.tags3Button, grid_2_vert_ind, 0, 1, 2)
		tab_2_grid.addWidget(self.tags3Box, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags3Add, grid_2_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags3X, grid_2_vert_ind, 4, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Tags 4
		self.tags4Button = QtWidgets.QPushButton(self.tag_list_names[3])
		self.tags4Button.setFixedWidth(170)
		self.tags4Box = QtWidgets.QLineEdit()
		self.tags4Box.setPlaceholderText('<-- Click to select tags')
		self.tags4Box.setFixedWidth(530)
		self.tags4Box.setReadOnly(True)
		self.tags4Add = QtWidgets.QPushButton('+')
		self.tags4Add.setFixedWidth(20)
		self.tags4Add.setToolTip('Add new tag to this tag group')
		self.tags4X = QtWidgets.QPushButton('X')
		self.tags4X.setFixedWidth(20)
		self.tags4X.setToolTip('Clear tags')
		self.input_field_dict['tags_4'] = self.tags4Box

		tab_2_grid.addWidget(self.tags4Button, grid_2_vert_ind, 0, 1, 2)
		tab_2_grid.addWidget(self.tags4Box, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags4Add, grid_2_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags4X, grid_2_vert_ind, 4, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Tags 5
		self.tags5Button = QtWidgets.QPushButton(self.tag_list_names[4])
		self.tags5Button.setFixedWidth(170)
		self.tags5Box = QtWidgets.QLineEdit()
		self.tags5Box.setPlaceholderText('<-- Click to select tags')
		self.tags5Box.setFixedWidth(530)
		self.tags5Box.setReadOnly(True)
		self.tags5Add = QtWidgets.QPushButton('+')
		self.tags5Add.setFixedWidth(20)
		self.tags5Add.setToolTip('Add new tag to this tag group')
		self.tags5X = QtWidgets.QPushButton('X')
		self.tags5X.setFixedWidth(20)
		self.tags5X.setToolTip('Clear tags')
		self.input_field_dict['tags_5'] = self.tags5Box

		tab_2_grid.addWidget(self.tags5Button, grid_2_vert_ind, 0, 1, 2)
		tab_2_grid.addWidget(self.tags5Box, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags5Add, grid_2_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags5X, grid_2_vert_ind, 4, alignment=QtCore.Qt.AlignLeft)
		grid_2_vert_ind += 1

		# Tags 6
		self.tags6Button = QtWidgets.QPushButton(self.tag_list_names[5])
		self.tags6Button.setFixedWidth(170)
		self.tags6Box = QtWidgets.QLineEdit()
		self.tags6Box.setPlaceholderText('<-- Click to select tags')
		self.tags6Box.setFixedWidth(530)
		self.tags6Box.setReadOnly(True)
		self.tags6Add = QtWidgets.QPushButton('+')
		self.tags6Add.setFixedWidth(20)
		self.tags6Add.setToolTip('Add new tag to this tag group')
		self.tags6X = QtWidgets.QPushButton('X')
		self.tags6X.setFixedWidth(20)
		self.tags6X.setToolTip('Clear tags')
		self.input_field_dict['tags_6'] = self.tags6Box

		tab_2_grid.addWidget(self.tags6Button, grid_2_vert_ind, 0, 1, 2)
		tab_2_grid.addWidget(self.tags6Box, grid_2_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags6Add, grid_2_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		tab_2_grid.addWidget(self.tags6X, grid_2_vert_ind, 4, alignment=QtCore.Qt.AlignLeft)
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
					self.tagWidGroups[ind][0].setToolTip('There are no tags in this tag group. Add tags via\n'
														 'the "+" button on the right, or the AMV Tracker\n'
														 'Settings menu.')
					self.tagWidGroups[ind][1].setPlaceholderText('')
					widg.setDisabled(True)

		grid_2_vert_ind += 1
		tab_2_grid.setRowMinimumHeight(grid_2_vert_ind, 20)
		grid_2_vert_ind += 1

		# Comments
		self.commentsLabel = QtWidgets.QLabel()
		self.commentsLabel.setText('Personal comments/notes:')
		self.commentsBox = QtWidgets.QTextEdit()
		self.commentsBox.setFixedSize(750, 180)
		self.input_field_dict['comments'] = self.commentsBox

		tab_2_grid.addWidget(self.commentsLabel, grid_2_vert_ind, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		tab_2_grid.addWidget(self.commentsBox, grid_2_vert_ind + 1, 0, 1, 6, alignment=QtCore.Qt.AlignTop)

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
		self.goToURLIcon = QtGui.QIcon(getcwd() + '\\icons\\go-icon.png')
		self.dlIcon = QtGui.QIcon(getcwd() + '\\icons\\download-icon.png')
		self.searchIcon = QtGui.QIcon(getcwd() + '\\icons\\search-icon.png')
		self.fetchIcon = QtGui.QIcon(getcwd() + '\\icons\\fetch-icon.png')

		self.ytURLLabel = QtWidgets.QLabel()
		self.ytURLLabel.setText('Video YouTube URL:')
		self.ytURLBox = QtWidgets.QLineEdit()
		self.ytURLBox.setFixedWidth(350)
		self.input_field_dict['video_youtube_url'] = self.ytURLBox

		self.goToYT = QtWidgets.QPushButton()
		self.goToYT.setFixedSize(22, 22)
		self.goToYT.setIcon(self.goToURLIcon)
		self.goToYT.setToolTip('Go to video on YouTube')

		self.searchYTButton = QtWidgets.QPushButton()
		self.searchYTButton.setFixedSize(22, 22)
		self.searchYTButton.setIcon(self.searchIcon)
		self.searchYTButton.setToolTip('Search for this video on YouTube. Must have both editor name\n'
									   'and video title entered on the "Video information" tab.')
		self.searchYTButton.setDisabled(True)

		self.fetchYTInfo = QtWidgets.QPushButton()
		self.fetchYTInfo.setFixedSize(22, 22)
		self.fetchYTInfo.setIcon(self.fetchIcon)
		self.fetchYTInfo.setIconSize(QtCore.QSize(14, 14))
		self.fetchYTInfo.setToolTip('If you enter the video\'s YouTube URL, you can press this button\n'
									'to automatically fetch the video info provided on YouTube.')
		self.fetchYTInfo.setDisabled(True)

		self.YTDLButton = QtWidgets.QPushButton()
		self.YTDLButton.setFixedSize(22, 22)
		self.YTDLButton.setIcon(self.dlIcon)
		self.YTDLButton.setToolTip('Download video from YouTube')
		self.YTDLButton.setDisabled(True)

		if self.ytURLBox.text() == '':
			self.goToYT.setDisabled(True)

		tab_3_grid_T.addWidget(self.ytURLLabel, grid_3_T_vert_ind, 0, alignment=QtCore.Qt.AlignTop)
		tab_3_grid_T.addWidget(self.ytURLBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.goToYT, grid_3_T_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.searchYTButton, grid_3_T_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.fetchYTInfo, grid_3_T_vert_ind, 4, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.YTDLButton, grid_3_T_vert_ind, 5, alignment=QtCore.Qt.AlignLeft)
		grid_3_T_vert_ind += 1

		# AMV.org URL
		self.searchAndFetchIcon = QtGui.QIcon(getcwd() + '\\icons\\search-and-fetch-icon.png')

		self.amvOrgURLLabel = QtWidgets.QLabel()
		self.amvOrgURLLabel.setText('Video AMV.org URL:')
		self.amvOrgURLBox = QtWidgets.QLineEdit()
		self.amvOrgURLBox.setFixedWidth(350)
		self.input_field_dict['video_org_url'] = self.amvOrgURLBox

		self.goToOrg = QtWidgets.QPushButton()
		self.goToOrg.setFixedSize(22, 22)
		self.goToOrg.setIcon(self.goToURLIcon)
		self.goToOrg.setToolTip('Go to video on amv.org')
		self.goToOrg.setDisabled(True)

		self.searchOrgButton = QtWidgets.QPushButton()
		self.searchOrgButton.setFixedSize(22, 22)
		self.searchOrgButton.setIcon(self.searchIcon)
		self.searchOrgButton.setDisabled(True)
		self.searchOrgButton.setToolTip('Search for this video on AnimeMusicVideos.org. Must have both editor name\n'
										'and video title entered on the "Video information" tab.')

		self.fetchOrgInfo = QtWidgets.QPushButton()
		self.fetchOrgInfo.setDisabled(True)
		self.fetchOrgInfo.setFixedSize(22, 22)
		self.fetchOrgInfo.setIcon(self.fetchIcon)
		self.fetchOrgInfo.setIconSize(QtCore.QSize(14, 14))
		self.fetchOrgInfo.setToolTip('If you enter an AMV.org video profile link, press this\n'
									 'button to populate the rest of the video information\n'
									 'as provided on the video\'s .org profile.')

		self.searchAndFetch = QtWidgets.QPushButton()
		self.searchAndFetch.setDisabled(True)
		self.searchAndFetch.setFixedSize(50, 22)
		self.searchAndFetch.setIcon(self.searchAndFetchIcon)
		self.searchAndFetch.setIconSize(QtCore.QSize(46, 18))
		self.searchAndFetch.setToolTip('Search for this video on AnimeMusicVideos.org (must have both editor name\n'
									   'and video title entered on the "Video information" tab), and populate the\n'
									   'rest of the video information with the info found on the first video profile\n'
									   'in the search results.')

		self.downloadOrgVideo = QtWidgets.QPushButton()
		self.downloadOrgVideo.setDisabled(True)
		self.downloadOrgVideo.setFixedSize(22, 22)
		self.downloadOrgVideo.setIcon(self.dlIcon)
		self.downloadOrgVideo.setToolTip('Download this video from the .org. NOTE: You must be logged in to your\n'
										 '.org account, and you must have fewer than 10 outstanding Star Ratings\n'
										 'to be given (these can be cleared on the Members Main Page).')

		tab_3_grid_T.addWidget(self.amvOrgURLLabel, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.amvOrgURLBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		# tab_3_grid_T.addWidget(self.fetchOrgVidDesc, grid_3_T_vert_ind, 2, 1, 10, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.goToOrg, grid_3_T_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.searchOrgButton, grid_3_T_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.fetchOrgInfo, grid_3_T_vert_ind, 4, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.downloadOrgVideo, grid_3_T_vert_ind, 5, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.searchAndFetch, grid_3_T_vert_ind, 6, 1, 10, alignment=QtCore.Qt.AlignLeft)
		grid_3_T_vert_ind += 1

		# amvnews URL
		self.amvnewsURLLabel = QtWidgets.QLabel()
		self.amvnewsURLLabel.setText('Video amvnews URL:')
		self.amvnewsURLBox = QtWidgets.QLineEdit()
		self.amvnewsURLBox.setFixedWidth(350)
		self.input_field_dict['video_amvnews_url'] = self.amvnewsURLBox

		self.goToAMVNews = QtWidgets.QPushButton()
		self.goToAMVNews.setFixedSize(22, 22)
		self.goToAMVNews.setIcon(self.goToURLIcon)
		self.goToAMVNews.setToolTip('Go to video on amvnews.ru')
		self.goToAMVNews.setDisabled(True)

		self.fetchAMVNewsInfo = QtWidgets.QPushButton()
		self.fetchAMVNewsInfo.setFixedSize(22, 22)
		self.fetchAMVNewsInfo.setIcon(self.fetchIcon)
		self.fetchAMVNewsInfo.setIconSize(QtCore.QSize(14, 14))
		self.fetchAMVNewsInfo.setToolTip('If you enter the video\'s amvnews URL, you can press this button\n'
										 'to automatically fetch the video info provided on amvnews.')
		self.fetchAMVNewsInfo.setDisabled(True)

		self.searchAMVNewsButton = QtWidgets.QPushButton()
		self.searchAMVNewsButton.setFixedSize(22, 22)
		self.searchAMVNewsButton.setIcon(self.searchIcon)
		self.searchAMVNewsButton.setToolTip('Search for this video on amvnews.ru. Must have the video title\n'
											'entered on the "Video information" tab.')
		if self.titleBox.text() == '':
			self.searchAMVNewsButton.setDisabled(True)

		self.downloadAMVNewsVideo = QtWidgets.QPushButton()
		self.downloadAMVNewsVideo.setFixedSize(22, 22)
		self.downloadAMVNewsVideo.setIcon(self.dlIcon)
		self.downloadAMVNewsVideo.setToolTip('Download video from amvnews')
		self.downloadAMVNewsVideo.setDisabled(True)

		tab_3_grid_T.addWidget(self.amvnewsURLLabel, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.amvnewsURLBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.goToAMVNews, grid_3_T_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.searchAMVNewsButton, grid_3_T_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.fetchAMVNewsInfo, grid_3_T_vert_ind, 4, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.downloadAMVNewsVideo, grid_3_T_vert_ind, 5, alignment=QtCore.Qt.AlignLeft)
		grid_3_T_vert_ind += 1

		# Other URL
		self.otherURLLabel = QtWidgets.QLabel()
		self.otherURLLabel.setText('Other video URL:')
		self.otherURLBox = QtWidgets.QLineEdit()
		self.otherURLBox.setFixedWidth(350)
		self.input_field_dict['video_other_url'] = self.otherURLBox

		self.goToOther = QtWidgets.QPushButton()
		self.goToOther.setFixedSize(22, 22)
		self.goToOther.setIcon(self.goToURLIcon)
		self.goToOther.setToolTip('Go to video on other website')
		self.goToOther.setDisabled(True)

		tab_3_grid_T.addWidget(self.otherURLLabel, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.otherURLBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.goToOther, grid_3_T_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
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
		self.localFileX.setDisabled(True)
		self.localFileX.setToolTip('Delete local file path')
		self.localFileWatchIcon = QtGui.QIcon(getcwd() + '\\icons\\play-icon.png')
		self.localFileWatch = QtWidgets.QPushButton()
		self.localFileWatch.setToolTip('Play video')
		self.localFileWatch.setIcon(self.localFileWatchIcon)
		self.localFileWatch.setFixedSize(22, 22)
		self.localFileWatch.setIconSize(QtCore.QSize(14, 14))
		self.input_field_dict['local_file'] = self.localFileBox

		tab_3_grid_T.addWidget(self.localFileButton, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.localFileBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.localFileX, grid_3_T_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.localFileWatch, grid_3_T_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
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
		self.input_field_dict['vid_thumb_path'] = self.thumbnailBox

		self.thumbnailX = QtWidgets.QPushButton('X')
		self.thumbnailX.setFixedSize(22, 22)
		self.thumbnailX.setDisabled(True)
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

		self.miniThumbLabel = QtWidgets.QLabel()
		self.miniThumbLabel.setFixedSize(320, 180)
		self.update_mini_thumb()
		"""self.miniThumbPixmap = QtGui.QPixmap(getcwd() + '/thumbnails/no_thumb.jpg')
		self.miniThumbLabel.setPixmap(self.miniThumbPixmap.scaled(self.miniThumbLabel.size(),
																  QtCore.Qt.KeepAspectRatio))"""

		tab_3_grid_T.setColumnStretch(3, 0)
		tab_3_grid_T.setColumnStretch(4, 0)
		tab_3_grid_T.addWidget(self.thumbnailButton, grid_3_T_vert_ind, 0)
		tab_3_grid_T.addWidget(self.thumbnailBox, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.thumbnailX, grid_3_T_vert_ind, 2, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.thumbnailDLButton, grid_3_T_vert_ind, 3, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_T.addWidget(self.thumbnailGenButton, grid_3_T_vert_ind, 4, alignment=QtCore.Qt.AlignLeft)
		grid_3_T_vert_ind += 1
		tab_3_grid_T.addWidget(self.miniThumbLabel, grid_3_T_vert_ind, 1, alignment=QtCore.Qt.AlignCenter)

		## Tab 3 - Bottom grid ##
		# self.tabs.addTab(self.tab3, 'Sources and URLs')
		tab_3_grid_B = QtWidgets.QGridLayout()
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
		self.input_field_dict['editor_youtube_channel_url'] = self.editorYTChannelBox

		self.goToYTChannel = QtWidgets.QPushButton()
		self.goToYTChannel.setFixedSize(22, 22)
		self.goToYTChannel.setIcon(self.goToURLIcon)
		self.goToYTChannel.setToolTip('Go to editor\'s YouTube channel')
		self.goToYTChannel.setDisabled(True)

		tab_3_grid_B.addWidget(self.editorYTChannelLabel, grid_3_B_vert_ind, 0)
		tab_3_grid_B.addWidget(self.editorYTChannelBox, grid_3_B_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_B.addWidget(self.goToYTChannel, grid_3_B_vert_ind, 2, 1, 10, alignment=QtCore.Qt.AlignLeft)
		grid_3_B_vert_ind += 1

		# Editor AMV.org profile
		self.editorAMVOrgProfileLabel = QtWidgets.QLabel()
		self.editorAMVOrgProfileLabel.setText('Editor AMV.org profile URL:')
		self.editorAMVOrgProfileBox = QtWidgets.QLineEdit()
		self.editorAMVOrgProfileBox.setFixedWidth(350)
		self.input_field_dict['editor_org_profile_url'] = self.editorAMVOrgProfileBox

		self.goToOrgProfile = QtWidgets.QPushButton()
		self.goToOrgProfile.setFixedSize(22, 22)
		self.goToOrgProfile.setIcon(self.goToURLIcon)
		self.goToOrgProfile.setToolTip('Go to editor\'s amv.org profile')
		self.goToOrgProfile.setDisabled(True)

		tab_3_grid_B.addWidget(self.editorAMVOrgProfileLabel, grid_3_B_vert_ind, 0)
		tab_3_grid_B.addWidget(self.editorAMVOrgProfileBox, grid_3_B_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_B.addWidget(self.goToOrgProfile, grid_3_B_vert_ind, 2, 1, 10, alignment=QtCore.Qt.AlignLeft)
		grid_3_B_vert_ind += 1

		# Editor amvnews profile
		self.editorAmvnewsProfileLabel = QtWidgets.QLabel()
		self.editorAmvnewsProfileLabel.setText('Editor amvnews profile URL:')
		self.editorAmvnewsProfileBox = QtWidgets.QLineEdit()
		self.editorAmvnewsProfileBox.setFixedWidth(350)
		self.input_field_dict['editor_amvnews_profile_url'] = self.editorAmvnewsProfileBox

		self.goToAmvnewsProfile = QtWidgets.QPushButton()
		self.goToAmvnewsProfile.setFixedSize(22, 22)
		self.goToAmvnewsProfile.setIcon(self.goToURLIcon)
		self.goToAmvnewsProfile.setToolTip('Go to editor\'s amvnews.ru profile')
		self.goToAmvnewsProfile.setDisabled(True)

		tab_3_grid_B.addWidget(self.editorAmvnewsProfileLabel, grid_3_B_vert_ind, 0)
		tab_3_grid_B.addWidget(self.editorAmvnewsProfileBox, grid_3_B_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_B.addWidget(self.goToAmvnewsProfile, grid_3_B_vert_ind, 2, 1, 10, alignment=QtCore.Qt.AlignLeft)
		grid_3_B_vert_ind += 1

		# Editor Other profile
		self.editorOtherProfileLabel = QtWidgets.QLabel()
		self.editorOtherProfileLabel.setText('Other editor profile URL:')
		self.editorOtherProfileBox = QtWidgets.QLineEdit()
		self.editorOtherProfileBox.setFixedWidth(350)
		self.input_field_dict['editor_other_profile_url'] = self.editorOtherProfileBox

		self.goToOtherProfile = QtWidgets.QPushButton()
		self.goToOtherProfile.setFixedSize(22, 22)
		self.goToOtherProfile.setIcon(self.goToURLIcon)
		self.goToOtherProfile.setToolTip('Go to editor\'s other profile')
		self.goToOtherProfile.setDisabled(True)

		tab_3_grid_B.addWidget(self.editorOtherProfileLabel, grid_3_B_vert_ind, 0)
		tab_3_grid_B.addWidget(self.editorOtherProfileBox, grid_3_B_vert_ind, 1, alignment=QtCore.Qt.AlignLeft)
		tab_3_grid_B.addWidget(self.goToOtherProfile, grid_3_B_vert_ind, 2, 1, 50, alignment=QtCore.Qt.AlignLeft)
		grid_3_B_vert_ind += 1

		## Tab 4 ##
		tab_4_vLayoutMaster = QtWidgets.QVBoxLayout()
		tab_4_vLayoutMaster.setAlignment(QtCore.Qt.AlignTop)
		tab_4_vLayout1 = QtWidgets.QVBoxLayout()
		tab_4_vLayout2 = QtWidgets.QVBoxLayout()
		tab_4_vLayout3 = QtWidgets.QVBoxLayout()
		tab_4_hLayout1 = QtWidgets.QHBoxLayout()
		tab_4_hLayout1.setAlignment(QtCore.Qt.AlignLeft)
		tab_4_hLayout2 = QtWidgets.QHBoxLayout()
		tab_4_hLayout2.setAlignment(QtCore.Qt.AlignLeft)

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

		# Video source
		self.videoSourceLabel = QtWidgets.QLabel()
		self.videoSourceLabel.setText('Video source:')
		self.videoSourceLabel.setToolTip('You can use this field to identify where this video came from, either in\n'
										 'terms of where you found this video on the internet or the method by\n'
										 'which it was entered into AMV Tracker. The default value in this field\n'
										 'can be changed in [Settings > Video entry].')
		self.videoSourceTextBox = CustomLineEdit()
		self.videoSourceTextBox.setFixedWidth(160)
		settings_cursor.execute('SELECT value FROM entry_settings WHERE setting_name = "default_manual_entry_source"')
		self.videoSourceTextBox.setText(settings_cursor.fetchone()[0])

		self.videoSourceList = []
		for subDB in self.subDB_int_name_list:
			subDB_cursor.execute('SELECT video_source FROM {}'.format(subDB))
			for src_tup in subDB_cursor.fetchall():
				if src_tup[0].casefold() not in (s.casefold() for s in self.videoSourceList) and src_tup[0] != '':
					self.videoSourceList.append(src_tup[0])
		self.videoSourceList.sort(key=lambda x: x.casefold())

		self.videoSourceCompleter = QtWidgets.QCompleter(self.videoSourceList)
		self.videoSourceCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.videoSourceCompleter.setMaxVisibleItems(15)
		self.videoSourceTextBox.setCompleter(self.videoSourceCompleter)

		tab_4_hLayout1.addWidget(self.videoSourceLabel)
		tab_4_hLayout1.addWidget(self.videoSourceTextBox, alignment=QtCore.Qt.AlignLeft)
		tab_4_vLayout1.addLayout(tab_4_hLayout1)
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

		# COME BACK HERE
		tab_4_vLayout2.addWidget(self.subDBScrollArea, alignment=QtCore.Qt.AlignTop)
		tab_4_vLayout3.addWidget(self.custListScrollArea, alignment=QtCore.Qt.AlignTop)
		tab_4_hLayout2.addLayout(tab_4_vLayout2)
		tab_4_hLayout2.addSpacing(20)
		tab_4_hLayout2.addLayout(tab_4_vLayout3)
		tab_4_vLayoutMaster.addLayout(tab_4_vLayout1)
		tab_4_vLayoutMaster.addLayout(tab_4_hLayout2)

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
			self.editor_1_text_changed()

			if self.editorBox1.text() != '' and self.titleBox.text() != '':
				self.searchYTButton.setEnabled(True)
				self.searchOrgButton.setEnabled(True)
				self.searchAndFetch.setEnabled(True)

			if self.localFileBox.text() != '':
				self.localFileX.setEnabled(True)

			if self.thumbnailBox.text() != '':
				self.thumbnailX.setEnabled(True)

			if self.ytURLBox.text() != '':
				self.goToYT.setEnabled(True)

			if self.amvOrgURLBox.text() != '':
				self.goToOrg.setEnabled(True)

			if self.amvnewsURLBox.text() != '':
				self.goToAMVNews.setEnabled(True)

			if self.otherURLBox.text() != '':
				self.goToOther.setEnabled(True)

			if self.editorYTChannelBox.text() != '':
				self.goToYTChannel.setEnabled(True)

			if self.editorAMVOrgProfileBox.text() != '':
				self.goToOrgProfile.setEnabled(True)

			if self.editorAmvnewsProfileBox.text() != '':
				self.goToAmvnewsProfile.setEnabled(True)

			if self.editorOtherProfileBox.text() != '':
				self.goToOtherProfile.setEnabled(True)

		self.enable_cust_log_btn()

		# Signals/slots
		# Tab 1
		if not self.edit_entry:
			self.editorBox1.editingFinished.connect(self.check_for_existing_entry)
			self.titleBox.editingFinished.connect(self.check_for_existing_entry)
		self.editorBox1.textChanged.connect(self.editor_1_text_changed)
		self.editorBox1.textChanged.connect(self.enable_yt_btns)
		self.editorBox1.textChanged.connect(self.en_dis_org_btns)
		self.editorBox1.doubleClicked.connect(lambda: self.show_all_completer(self.editorNameCompleter))
		self.pseudoBox.doubleClicked.connect(lambda: self.show_all_completer(self.editorNameCompleter))
		self.studioBox.doubleClicked.connect(lambda: self.show_all_completer(self.studioCompleter))
		self.MEPlabel.mousePressEvent = self.two_plus_editors
		self.titleBox.textChanged.connect(self.enable_yt_btns)
		self.titleBox.textChanged.connect(self.en_dis_org_btns)
		self.titleBox.textChanged.connect(self.en_dis_amvnews_search)
		self.dateYear.currentIndexChanged.connect(lambda: self.en_dis_date_boxes(self.dateYear))
		self.dateMonth.currentIndexChanged.connect(lambda: self.en_dis_date_boxes(self.dateMonth))
		self.dateMonth.currentIndexChanged.connect(self.populate_day_dropdown)
		self.dateUnk.clicked.connect(self.date_unknown_checked)
		self.starRatingBox.editingFinished.connect(self.check_star_rating)
		self.videoSearchBox.doubleClicked.connect(lambda: self.show_all_completer(self.footageCompleter))
		self.videoSearchBox.textChanged.connect(self.enable_add_ftg_btn)
		self.addFootage.clicked.connect(self.add_video_ftg)
		self.videoFootageBox.itemSelectionChanged.connect(self.enable_remove_ftg_btn)
		self.removeFootage.clicked.connect(self.remove_video_ftg)
		self.artistBox.doubleClicked.connect(lambda: self.show_all_completer(self.artistCompleter))
		self.songGenreBox.doubleClicked.connect(lambda: self.show_all_completer(self.songGenreCompleter))
		if self.entry_settings['autopop_genre'] == 1:
			self.artistBox.editingFinished.connect(self.autopop_genre)
		self.songGenreQuestion.mousePressEvent = self.rym_artist_search

		# Tab 2
		self.applyLogicBtn.clicked.connect(self.cust_log_btn_clicked)

		self.tags1Button.clicked.connect(lambda: self.tag_window(self.tags1Button.text(), self.tags1Box))
		self.tags2Button.clicked.connect(lambda: self.tag_window(self.tags2Button.text(), self.tags2Box))
		self.tags3Button.clicked.connect(lambda: self.tag_window(self.tags3Button.text(), self.tags3Box))
		self.tags4Button.clicked.connect(lambda: self.tag_window(self.tags4Button.text(), self.tags4Box))
		self.tags5Button.clicked.connect(lambda: self.tag_window(self.tags5Button.text(), self.tags5Box))
		self.tags6Button.clicked.connect(lambda: self.tag_window(self.tags6Button.text(), self.tags6Box))

		self.tags1Add.clicked.connect(lambda: self.add_tag(self.tags1Button))
		self.tags2Add.clicked.connect(lambda: self.add_tag(self.tags2Button))
		self.tags3Add.clicked.connect(lambda: self.add_tag(self.tags3Button))
		self.tags4Add.clicked.connect(lambda: self.add_tag(self.tags4Button))
		self.tags5Add.clicked.connect(lambda: self.add_tag(self.tags5Button))
		self.tags6Add.clicked.connect(lambda: self.add_tag(self.tags6Button))

		self.tags1X.clicked.connect(self.tags1Box.clear)
		self.tags2X.clicked.connect(self.tags2Box.clear)
		self.tags3X.clicked.connect(self.tags3Box.clear)
		self.tags4X.clicked.connect(self.tags4Box.clear)
		self.tags5X.clicked.connect(self.tags5Box.clear)
		self.tags6X.clicked.connect(self.tags6Box.clear)

		# Tab 3
		self.goToYT.clicked.connect(lambda: self.go_to_website(self.ytURLBox.text()))
		self.ytURLBox.textChanged.connect(lambda: self.enable_thumb_btns('yt'))
		self.ytURLBox.textChanged.connect(self.enable_yt_btns)
		self.searchYTButton.clicked.connect(self.search_youtube)
		self.fetchYTInfo.clicked.connect(self.fetch_youtube_info)
		self.YTDLButton.clicked.connect(self.dl_yt_vid)
		self.goToOrg.clicked.connect(lambda: self.go_to_website(self.amvOrgURLBox.text()))
		self.amvOrgURLBox.textChanged.connect(self.en_dis_org_btns)
		self.searchOrgButton.clicked.connect(self.search_org)
		self.fetchOrgInfo.clicked.connect(lambda: self.fetch_org_info(self.amvOrgURLBox.text()))
		self.downloadOrgVideo.clicked.connect(lambda: self.dl_org_video(self.amvOrgURLBox.text()))
		self.searchAndFetch.clicked.connect(self.org_search_and_fetch)
		self.goToAMVNews.clicked.connect(lambda: self.go_to_website(self.amvnewsURLBox.text()))
		self.amvnewsURLBox.textChanged.connect(self.en_dis_amvnews_btns)
		self.searchAMVNewsButton.clicked.connect(self.search_amvnews)
		self.fetchAMVNewsInfo.clicked.connect(lambda: self.fetch_amvnews_info(self.amvnewsURLBox.text()))
		self.downloadAMVNewsVideo.clicked.connect(lambda: self.dl_amvnews(self.amvnewsURLBox.text()))
		self.goToOther.clicked.connect(lambda: self.go_to_website(self.otherURLBox.text()))
		self.localFileButton.clicked.connect(self.local_file_clicked)
		self.localFileBox.textChanged.connect(lambda: self.enable_thumb_btns('local'))
		self.localFileBox.textChanged.connect(self.en_dis_watch_button)
		self.localFileBox.textChanged.connect(self.local_file_changed)
		self.localFileBox.textChanged.connect(self.get_video_length)
		self.localFileWatch.clicked.connect(self.play_vid)
		self.thumbnailButton.clicked.connect(self.thumbnail_clicked)
		self.thumbnailBox.textChanged.connect(lambda: self.enable_thumb_btns('thumbs'))
		self.thumbnailBox.textChanged.connect(self.update_mini_thumb)
		self.thumbnailX.clicked.connect(self.delete_thumb_path)
		self.localFileX.clicked.connect(self.localFileBox.clear)
		self.thumbnailDLButton.clicked.connect(self.dl_thumb)
		self.thumbnailGenButton.clicked.connect(self.generate_thumb)
		self.fetchProfilesButton.clicked.connect(self.fetch_profiles)

		self.goToYTChannel.clicked.connect(lambda: self.go_to_website(self.editorYTChannelBox.text()))
		self.goToOrgProfile.clicked.connect(lambda: self.go_to_website(self.editorAMVOrgProfileBox.text()))
		self.goToAmvnewsProfile.clicked.connect(lambda: self.go_to_website(self.goToAmvnewsProfile.text()))
		self.goToOtherProfile.clicked.connect(lambda: self.go_to_website(self.editorOtherProfileBox.text()))

		## Enable Go To buttons
		self.ytURLBox.textChanged.connect(lambda: self.en_dis_go_to_btns(self.goToYT, self.ytURLBox.text()))
		self.amvOrgURLBox.textChanged.connect(lambda: self.en_dis_go_to_btns(self.goToOrg, self.amvOrgURLBox.text()))
		self.amvnewsURLBox.textChanged.connect(
			lambda: self.en_dis_go_to_btns(self.goToAMVNews, self.amvnewsURLBox.text()))
		self.otherURLBox.textChanged.connect(lambda: self.en_dis_go_to_btns(self.goToOther, self.otherURLBox.text()))

		self.editorYTChannelBox.textChanged.connect(
			lambda: self.en_dis_go_to_btns(self.goToYTChannel, self.editorYTChannelBox.text()))
		self.editorAMVOrgProfileBox.textChanged.connect(
			lambda: self.en_dis_go_to_btns(self.goToOrgProfile, self.editorAMVOrgProfileBox.text()))
		self.editorAmvnewsProfileBox.textChanged.connect(
			lambda: self.en_dis_go_to_btns(self.goToAmvnewsProfile, self.editorAmvnewsProfileBox.text()))
		self.editorOtherProfileBox.textChanged.connect(
			lambda: self.en_dis_go_to_btns(self.goToOtherProfile, self.editorOtherProfileBox.text()))

		# Tab 4
		self.videoSourceTextBox.doubleClicked.connect(lambda: self.show_all_completer(self.videoSourceCompleter))
		self.copyButton.clicked.connect(lambda: self.copy_video(self.inp_vidid,
																common_vars.sub_db_lookup(reverse=True)[
																	self.inp_subdb]))

		# Back / submit
		self.backButton.clicked.connect(self.back_button_clicked)
		self.submitButton.clicked.connect(self.submit_button_clicked)

		## Widget ##
		self.wid = QtWidgets.QWidget()
		self.wid.setLayout(vLayoutMaster)
		self.setCentralWidget(self.wid)
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Video entry')
		self.setFixedSize(self.sizeHint())
		self.wid.show()

		# Set focus
		self.editorBox1.setFocus()

		# Enable watch button if local file box already populated
		if self.localFileBox.text() == '':
			self.localFileWatch.setDisabled(True)

		# Close connections
		settings_conn.close()
		subDB_conn.close()

	def edit_pop(self):
		"""
		Populates fields on entry screen with data from selected video.
		"""
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
			self.dateYear.setDisabled(True)
			self.dateMonth.setDisabled(True)
			self.dateDay.setDisabled(True)
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
			self.downloadOrgVideo.setEnabled(True)
		self.amvnewsURLBox.setText(vid_dict['video_amvnews_url'])
		self.amvnewsURLBox.setCursorPosition(0)
		self.otherURLBox.setText(vid_dict['video_other_url'])
		self.otherURLBox.setCursorPosition(0)
		self.localFileBox.setText(vid_dict['local_file'])
		self.localFileBox.setCursorPosition(0)

		if os.path.isfile(getcwd() + vid_dict['vid_thumb_path']):
			self.thumbnailBox.setText(getcwd() + vid_dict['vid_thumb_path'])
		else:
			if vid_dict['vid_thumb_path'] == '':
				pass
			elif os.path.isfile(vid_dict['vid_thumb_path']):
				self.thumbnailBox.setText(vid_dict['vid_thumb_path'])
			else:
				self.thumbnailBox.setPlaceholderText('Thumbnail file has been moved or deleted')
		self.thumbnailBox.setCursorPosition(0)

		self.editorYTChannelBox.setText(vid_dict['editor_youtube_channel_url'])
		self.editorYTChannelBox.setCursorPosition(0)
		self.editorAMVOrgProfileBox.setText(vid_dict['editor_org_profile_url'])
		self.editorAMVOrgProfileBox.setCursorPosition(0)
		self.editorAmvnewsProfileBox.setText(vid_dict['editor_amvnews_profile_url'])
		self.editorAmvnewsProfileBox.setCursorPosition(0)
		self.editorOtherProfileBox.setText(vid_dict['editor_other_profile_url'])
		self.editorOtherProfileBox.setCursorPosition(0)
		self.videoSourceTextBox.setText(vid_dict['video_source'])
		self.videoSourceTextBox.setCursorPosition(0)

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
		self.update_mini_thumb()

	def update_mini_thumb(self):
		if self.thumbnailBox.text() == '' or not os.path.isfile(self.thumbnailBox.text()):
			self.miniThumbPixmap = QtGui.QPixmap(getcwd() + '/thumbnails/no_thumb.jpg')
			if self.thumbnailBox.text() != '':
				self.miniThumbLabel.setToolTip('If there is a file path in the thumbnail text box and you\n'
											   'are still seeing this image, that means that the original\n'
											   'thumbnail file has been moved or deleted.')
			else:
				self.miniThumbLabel.setToolTip('')

		else:
			self.miniThumbPixmap = QtGui.QPixmap(self.thumbnailBox.text())
			self.miniThumbLabel.setToolTip('')

		self.miniThumbLabel.setPixmap(self.miniThumbPixmap.scaled(self.miniThumbLabel.size(),
																  QtCore.Qt.KeepAspectRatio))

	def check_for_existing_entry(self):
		"""
		Checks to see if editor name/video title combination exists in the database already, and if so, asks user if
		they'd like to be taken to the existing entry.
		"""
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
			self.editorBox1.clear()
			self.editorBox1.setCompleter(self.editorNameCompleter)

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
		"""
		Programmatically determines # of days in the month given the year and month.
		"""
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
		"""
		Ensures that the data put into the Star Rating box is an int or a float between 0 and 5
		"""
		try:
			if self.starRatingBox.text() != '':
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

	def show_all_completer(self, compl):
		"""
		Shows all items in a QCompleter.
		:param compl: QCompleter widget to be parsed.
		"""
		compl.complete()

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

	def autopop_genre(self):
		"""
		Searches through DB and populates genre box with most-used genre for a given song artist (if the song artist is
		already in the database, and this option has been enabled in Settings).
		"""
		autopop_conn = sqlite3.connect(common_vars.video_db())
		autopop_cursor = autopop_conn.cursor()
		list_of_subdbs = [v for k, v in common_vars.sub_db_lookup().items()]
		genre_dict = dict()
		artist = self.artistBox.text()

		for sdb in list_of_subdbs:
			autopop_cursor.execute('SELECT song_genre FROM {} WHERE song_artist = ? COLLATE NOCASE'.format(sdb),
								   (artist,))
			genres = [x[0] for x in autopop_cursor.fetchall()]
			for g in genres:
				if g not in genre_dict:
					genre_dict[g] = 1
				else:
					genre_dict[g] += 1

		if len(genre_dict) > 0:
			genre_out = max(genre_dict, key=genre_dict.get)  # Returns the key with the max value
		else:
			genre_out = ''
		self.songGenreBox.setText(genre_out)

	def rym_artist_search(self, event):
		if self.artistBox.text().strip() != '':
			webbrowser.open('https://rateyourmusic.com/search?searchterm={}&searchtype='.format(
				self.artistBox.text().replace(' ', '+')))

	def enable_cust_log_btn(self):
		cust_log_conn = sqlite3.connect(common_vars.video_db())
		cust_log_cursor = cust_log_conn.cursor()

		cust_log_cursor.execute('SELECT ctlr_id FROM custom_tag_logic WHERE in_use = 1')
		if len(cust_log_cursor.fetchall()) > 0:
			self.applyLogicBtn.setEnabled(True)

		cust_log_conn.close()

	def populate_tag_boxes(self, tag_dict):
		pop_tag_conn = sqlite3.connect(common_vars.video_db())
		pop_tag_cursor = pop_tag_conn.cursor()

		for tg, tl in tag_dict.items():
			dis_tags = []

			for t in tl:
				pop_tag_cursor.execute('SELECT disable_tags FROM {} WHERE tag_name = ? COLLATE NOCASE'.format(tg), (t,))
				m_e_tags = pop_tag_cursor.fetchone()
				if m_e_tags:
					for tag in m_e_tags[0].split('; '):
						dis_tags.append(tag.casefold())

			en_tags = [t for t in tl if t not in dis_tags]
			if en_tags:
				tags_to_check = '; '.join(en_tags)
			else:
				tags_to_check = ''

			self.input_field_dict[tg].setText(tags_to_check)

		pop_tag_conn.close()

	def cust_log_btn_clicked(self):
		cust_log_btn_conn = sqlite3.connect(common_vars.video_db())
		cust_log_btn_cursor = cust_log_btn_conn.cursor()

		tags_to_check = {'tags_1': [], 'tags_2': [], 'tags_3': [], 'tags_4': [], 'tags_5': [], 'tags_6': []}
		cust_log_btn_cursor.execute('SELECT * FROM custom_tag_logic')
		for tup in cust_log_btn_cursor.fetchall():
			criteria_matched = False
			field = tup[1]
			operation = tup[2]
			value = tup[3]
			tags = [tup[4], tup[5], tup[6], tup[7], tup[8], tup[9]]
			field_wid = self.input_field_dict[field]

			if operation == 'STARTS WITH':
				if isinstance(field_wid, QtWidgets.QLineEdit):
					if field_wid.text().casefold()[:len(value)] == value.casefold():
						criteria_matched = True

				elif isinstance(field_wid, QtWidgets.QListWidget):
					lw_items_sw = [field_wid.item(x).text() for x in range(field_wid.count())]
					for st in lw_items_sw:
						if st.casefold()[:len(value)] == value.casefold():
							criteria_matched = True

				else:  # TextEdit class
					if field_wid.toPlainText().casefold()[:len(value)] == value.casefold():
						criteria_matched = True

			elif operation == 'CONTAINS':
				if isinstance(field_wid, QtWidgets.QLineEdit):
					if value.casefold() in field_wid.text().casefold():
						criteria_matched = True

				elif isinstance(field_wid, QtWidgets.QListWidget):
					lw_items_con = [field_wid.item(x).text() for x in range(field_wid.count())]
					for s in lw_items_con:
						if value.casefold() in s.casefold():
							criteria_matched = True

				else:  # TextEdit class
					if value.casefold() in field_wid.toPlainText().casefold():
						criteria_matched = True

			elif operation == '=':
				if isinstance(field_wid, QtWidgets.QLineEdit):
					if value.casefold() == field_wid.text().casefold():
						criteria_matched = True

				elif isinstance(field_wid, QtWidgets.QTextEdit):
					if value.casefold() == field_wid.toPlainText().casefold():
						criteria_matched = True

				elif isinstance(field_wid, QtWidgets.QListWidget):
					lw_items_eq = [field_wid.item(x).text() for x in range(field_wid.count())]
					for ftg in lw_items_eq:
						if value.casefold() == ftg.casefold():
							criteria_matched = True

				else:  # QComboBox class
					if value != '' and field_wid.currentText() == '':
						criteria_matched = False
					elif value == '' and field.currentText() == '':
						criteria_matched = True
					elif float(value.casefold()) == float(field_wid.currentText()):
						criteria_matched = True

			elif operation == '!=':
				if isinstance(field_wid, QtWidgets.QLineEdit):
					if value.casefold() != field_wid.text().casefold():
						criteria_matched = True

				elif isinstance(field_wid, QtWidgets.QTextEdit):
					if value.casefold() != field_wid.toPlainText().casefold():
						criteria_matched = True

				else:  # QListWidget class
					lw_items_dne = [field_wid.item(x).text() for x in range(field_wid.count())]
					for ftg_ in lw_items_dne:
						if value.casefold() != ftg_.casefold():
							criteria_matched = True
						else:
							criteria_matched = False
							break

			elif operation == '<':
				if field == 'video_length':
					if self.lengthMinDrop.currentText() != '' and self.lengthSecDrop.currentText() != '':
						if ((int(self.lengthMinDrop.currentText()) * 60) + int(self.lengthSecDrop.currentText())) < \
								int(value):
							criteria_matched = True
				else:
					if isinstance(field_wid, QtWidgets.QLineEdit):
						if float(field_wid.text()) < float(value):
							criteria_matched = True

					else:  # QComboBox class
						if field_wid.currentText() != '':
							if float(field_wid.currentText()) > float(value):
								criteria_matched = True

			elif operation == '>':
				if field == 'video_length':
					if self.lengthMinDrop.currentText() != '' and self.lengthSecDrop.currentText() != '':
						if ((int(self.lengthMinDrop.currentText()) * 60) + int(self.lengthSecDrop.currentText())) > \
								int(value):
							criteria_matched = True
				else:
					if isinstance(field_wid, QtWidgets.QLineEdit):
						if float(field_wid.text()) > float(value):
							criteria_matched = True

					else:  # QComboBox class
						if field_wid.currentText() != '':
							if float(field_wid.currentText()) > float(value):
								criteria_matched = True

			elif operation == 'BEFORE' or operation == 'AFTER' or operation == 'BETWEEN':
				if self.dateYear.currentText() != '' and self.dateMonth.currentText() != '' and \
						self.dateDay.currentText() != '':
					inp_datetime = time.strptime('{}/{}/{}'.format(self.dateYear.currentText(),
																   self.dateMonth.currentText()[0:2],
																   self.dateDay.currentText()), '%Y/%m/%d')

					if operation == 'BEFORE' or operation == 'AFTER':
						criteria_datetime = time.strptime(value, '%Y/%m/%d')
						if operation == 'BEFORE':
							if inp_datetime < criteria_datetime:
								criteria_matched = True

						else:
							if inp_datetime > criteria_datetime:
								criteria_matched = True

					else:  # BETWEEN
						dates = value.split(' AND ')
						criteria_datetime_low = time.strptime(dates[0], '%Y/%m/%d')
						criteria_datetime_high = time.strptime(dates[1], '%Y/%m/%d')
						if criteria_datetime_low < inp_datetime < criteria_datetime_high:
							criteria_matched = True

			elif operation == 'IS CHECKED':
				if field_wid.isChecked():
					criteria_matched = True

			elif operation == 'IS UNCHECKED':
				if not field_wid.isChecked():
					criteria_matched = True

			elif operation == 'IS POPULATED':
				if field_wid.text() != '':
					criteria_matched = True

			elif operation == 'IS NOT POPULATED':
				if field_wid.text() == '':
					criteria_matched = True

			else:
				print('You shouldn\'t have been able to get here dude.')

			if criteria_matched:
				ind = 1
				for t_list in tags:
					for t in t_list.split('; '):
						if t != '' and t not in tags_to_check['tags_{}'.format(str(ind))]:
							tags_to_check['tags_{}'.format(str(ind))].append(t)

					ind += 1

		self.populate_tag_boxes(tags_to_check)
		cust_log_btn_conn.close()

	def tag_window(self, tag_type, tag_box):
		tag_win = tag_checkboxes.TagWindow(tag_type, checked_tags=tag_box.text())
		if tag_win.exec_():
			tag_box.setText(tag_win.out_str[:-2])

	def add_tag(self, tag_button):
		tag_grp_name = tag_button.text()
		tag_conn = sqlite3.connect(common_vars.video_db())
		tag_cursor = tag_conn.cursor()
		internal_tag_grp = common_vars.tag_table_lookup()[tag_grp_name]
		sort_order = [so for so in tag_cursor.execute('SELECT sort_order FROM {}'.format(internal_tag_grp))]
		if not sort_order:
			max_sort_order_number = 0
		else:
			max_sort_order_number = max(sort_order)[0]

		tag_cursor.execute('SELECT tag_name FROM {}'.format(internal_tag_grp))
		tag_list = [tup[0] for tup in tag_cursor.fetchall()]

		new_tag_win = generic_entry_window.GenericEntryWindow('new', inp_1='tag', dupe_check_list=tag_list)
		if new_tag_win.exec_():
			new_tag = new_tag_win.textBox.text()
			tag_cursor.execute(
				'INSERT INTO {} (tag_name, tag_desc, sort_order, disable_tags) VALUES (?, ?, ?, ?)'
					.format(internal_tag_grp), (new_tag, '', max_sort_order_number + 1, ''))
			tag_cursor.execute('UPDATE tags_lookup SET in_use = 1 WHERE internal_field_name = ?', (internal_tag_grp,))

			if not tag_button.isEnabled():
				tag_button.setEnabled(True)
				tag_button.setToolTip('')

			success_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Tag added',
												'New tag <b>{}</b> has successfully been<br>added to tag group {}.'
												.format(new_tag, tag_button.text()))
			success_win.exec_()

		tag_conn.commit()
		tag_conn.close()

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

	def en_dis_go_to_btns(self, btn, text):
		if 'http' in text or 'www' in text:
			btn.setEnabled(True)
		else:
			btn.setDisabled(True)

	def go_to_website(self, url):
		try:
			webbrowser.open(url)
		except:
			website_err_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Error',
													'This does not appear to be a valid URL. Please double-check the URL\n'
													'entered and try again.')
			website_err_win.exec_()

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
			self.autopop_genre()
			self.songTitleBox.setText(info['song_title'])

			year = info['release_date'][0:4]
			month_ind = int(info['release_date'][5:7])
			day_ind = int(info['release_date'][8:10])

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
		ok_to_proceed = True

		# Check if paths to exes have been specified
		if common_vars.get_ytdlp_path() == '' or common_vars.get_ffmpeg_path() == '' or \
			common_vars.get_ffprobe_path() == '':
			missing_exe_spec = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'yt-dlp and/or ffmpeg missing',
													 'You need both yt-dlp and ffmpeg to use this function. Please go to\n'
													 'AMV Tracker\'s Settings and see the instructions under both the\n'
													 '"yt-dlp" and "ffmpeg / ffprobe" headers in the "Data import" tab.\n'
													 'If you decide to manually download the ffmpeg build, please be\n'
													 'sure to place those .exe files in the same folder as yt-dlp.exe.')
			missing_exe_spec.exec_()
			ok_to_proceed = True

		# Check that exe files still exist if path has been specified
		if ((common_vars.get_ytdlp_path() != '' and not os.path.isfile(common_vars.get_ytdlp_path())) or
				(common_vars.get_ffmpeg_path() != '' and not os.path.isfile(common_vars.get_ffmpeg_path())) or
				(common_vars.get_ffprobe_path() != '' and not os.path.isfile(common_vars.get_ffprobe_path()))):
			missing_exe_loc = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'yt-dlp and/or ffmpeg missing',
													 'This function requires that you have downloaded yt-dlp and\n'
													 'ffmpeg, and have identified the location of the corresponding\n'
													 'executables. It appears that you have specified the location\n'
													 'of all of the following files within AMV Tracker\'s Settings:\n\n'
													 '\u2022 yt-dlp.exe\n'
													 '\u2022 ffmpeg.exe\n'
													 '\u2022 ffprobe.exe\n\n'
													 '...but inspection reveals that one or more have since been\n'
													 'moved or deleted. Please go to AMV Tracker\'s Settings and\n'
													 'ensure that the paths being pointed to for each of these is\n'
													 'correct.')
			missing_exe_loc.exec_()
			ok_to_proceed = False

		if ok_to_proceed:
			yt = pytube.YouTube(self.ytURLBox.text())

			vid_editor = yt.author
			try:
				vid_title = yt.title
			except:
				vid_title = ''

			try:
				dl_win = download_yt_video.DownloadFromYouTube(self.ytURLBox.text(), vid_editor, vid_title)
				if dl_win.exec_() and self.localFileBox.text() == '' and dl_win.savePathBox.text() != '' and \
						dl_win.statusBox.toPlainText() == 'Done!':
					self.localFileBox.setText(dl_win.savePathBox.text() + '.mp4')

			except:  # yt-dlp is not working
				not_working_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
														'If you are seeing this message, AMV Tracker was not able to<br>'
														'run the code to download the video from YouTube. A possible<br>'
														'fix is to ensure, if you have <u>manually</u> downloaded yt-dlp and<br>'
														'ffmpeg, that you have put all the related executables in the<br>'
														'same folder. You can check this in the "Data import" tab within<br>'
														'AMV Tracker\'s Settings.<br><br>'
														'If you have done this and you still get this error, please create<br>'
														'a post on the AMV Tracker <a href="https://github.com/bsobotka/amv_tracker/issues">Issues page</a>'
														'on GitHub.')
				not_working_win.exec_()

				# file_name = dl_win.savePathBox.text().split('/')[-1]
				# fdir = '/'.join(dl_win.savePathBox.text().split('/')[:-1])
				# root, dirs, files = next(os.walk(fdir, topdown=True))
				# files = [os.path.join(root, f).replace('\\', '/') for f in files if file_name in f]
				# self.localFileBox.setText(files[0])

		"""full_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '{} - {}'
														  .format(vid_editor, vid_title))
		dir_path = '/'.join(full_path[0].replace('\\', '/').split('/')[:-1])
		fname = full_path[0].replace('\\', '/').split('/')[-1]

		if fname != '':
			dl_win = download_yt_video.DownloadFromYouTube(self.ytURLBox.text(), full_path[0])
			dl_win.exec_()
			dl_yt_win = download_yt_video.DownloadFromYT(self.ytURLBox.text(), dir_path, fname)
			if dl_yt_win.exec_():
				self.localFileBox.setText(full_path[0])"""

	def en_dis_org_btns(self):
		if 'members_videoinfo.php?v' in self.amvOrgURLBox.text():
			self.fetchOrgInfo.setEnabled(True)
			self.downloadOrgVideo.setEnabled(True)
		else:
			self.fetchOrgInfo.setDisabled(True)
			self.downloadOrgVideo.setDisabled(True)

		if self.editorBox1.text() != '' and self.titleBox.text() != '':
			self.searchOrgButton.setEnabled(True)
			self.searchAndFetch.setEnabled(True)
		else:
			self.searchOrgButton.setDisabled(True)
			self.searchAndFetch.setDisabled(True)

	def search_org(self):
		ed_name = self.editorBox1.text().replace(' ', '+')
		vid_title = self.titleBox.text().replace(' ', '+')
		webbrowser.open('https://www.animemusicvideos.org/search/supersearch.php?anime_criteria=&artist_criteria=&'
						'song_criteria=&member_criteria={}&studio_criteria=&spread=less&title={}&comments=&download='
						'&con=&year=&format_id=&o=7&d=1&recent=on&go=go#results'
						.format(ed_name, vid_title))

	def fetch_org_info(self, url):
		if check_for_internet_conn.internet_check('https://www.animemusicvideos.org'):
			info = fetch_vid_info.download_data(url, 'org')
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
			self.autopop_genre()
			self.songTitleBox.setText(info['song_title'])

			if info['video_length'][0] != -1 and info['video_length'][1] != -1:
				self.lengthMinDrop.setCurrentIndex(info['video_length'][0] + 1)
				self.lengthSecDrop.setCurrentIndex(info['video_length'][1] + 1)

			self.contestBox.setText(info['contests_entered'].replace('; ', '\n'))
			self.vidDescBox.setText(info['video_description'])
			if 'video_youtube_url' in info.keys():  # info dict may not have this key; see fetch_vid_info.py
				self.ytURLBox.setText(info['video_youtube_url'])
			self.amvnewsURLBox.setText(info['video_amvnews_url'])
			self.otherURLBox.setText(info['video_other_url'])
			self.editorAMVOrgProfileBox.setText(info['editor_org_profile_url'])

		else:
			unresolved_host_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'No response',
														'AnimeMusicVideos.org is currently unresponsive. Check your\n'
														'internet connection or try again later.')
			unresolved_host_win.exec_()

	def org_search_and_fetch(self):
		ed_name = self.editorBox1.text().replace(' ', '+')
		vid_title = self.titleBox.text().replace(' ', '+')
		url = 'https://www.animemusicvideos.org/search/supersearch.php?anime_criteria=&artist_criteria=&' \
			  'song_criteria=&member_criteria={}&studio_criteria=&spread=less&title={}&comments=&download=' \
			  '&con=&year=&format_id=&o=7&d=1&recent=on&go=go#results'.format(ed_name, vid_title)

		r = requests.get(url)
		soup = BeautifulSoup(r.content, 'html5lib')
		try:
			vid_url_html = soup.find('li', {'class': 'video'}).find_all('a')[1]
			vid_url = 'https://www.animemusicvideos.org' + parse.unquote(vid_url_html.get('href'))
			self.fetch_org_info(vid_url)
			self.amvOrgURLBox.setText(vid_url)

		except:
			nothing_found_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Nothing found',
													  'The provided editor username/video title combination found\n'
													  'no results on amv.org. Please ensure the spelling of both is\n'
													  'correct. Alternatively, this video may not exist on the .org.')
			nothing_found_win.exec_()

	def dl_org_video(self, url):
		org_id = url.split('=')[-1]
		dl_url = 'https://www.animemusicvideos.org/members/localdownload-pancake.php?v={}&thead=yep&actionz=proceed'.format(
			org_id)
		webbrowser.open(dl_url)

	def en_dis_amvnews_btns(self):
		if 'amvnews.ru/index.php?go=Files&in=view&id=' in self.amvnewsURLBox.text():
			self.fetchAMVNewsInfo.setEnabled(True)
			self.downloadAMVNewsVideo.setEnabled(True)
		else:
			self.fetchAMVNewsInfo.setDisabled(True)
			self.downloadAMVNewsVideo.setDisabled(True)

	def en_dis_amvnews_search(self):
		if self.titleBox.text() != '':
			self.searchAMVNewsButton.setEnabled(True)
		else:
			self.searchAMVNewsButton.setDisabled(True)

	def search_amvnews(self):
		query = self.titleBox.text().replace(' ', '+')
		search_url = 'https://amvnews.ru/index.php?go=Search&modname=Files&query={}'.format(query)
		webbrowser.open(search_url)

	def fetch_amvnews_info(self, url):
		if check_for_internet_conn.internet_check('https://amvnews.ru'):
			amvnews_data = fetch_vid_info.download_data(url, 'amvnews')
			self.editorBox1.setText(amvnews_data['primary_editor_username'])
			self.editorBox2.setText(amvnews_data['addl_editors'])
			self.editorBox2.setCursorPosition(0)
			self.titleBox.setText(amvnews_data['video_title'])
			self.studioBox.setText(amvnews_data['studio'])
			self.awardsBox.setText(amvnews_data['awards_won'])
			self.dateYear.setCurrentText(amvnews_data['release_date'][0])
			self.dateMonth.setCurrentIndex(int(amvnews_data['release_date'][1]))
			self.dateDay.setCurrentIndex(int(amvnews_data['release_date'][2]))
			self.artistBox.setText(amvnews_data['song_artist'])
			self.songTitleBox.setText(amvnews_data['song_title'])
			self.starRatingBox.setText(amvnews_data['star_rating'])
			self.vidDescBox.setText(amvnews_data['video_description'])

			if amvnews_data['video_length'] != 0:
				dur_min = amvnews_data['video_length'] // 60
				self.lengthMinDrop.setCurrentText(str(dur_min))
				dur_sec = amvnews_data['video_length'] % 60
				self.lengthSecDrop.setCurrentText(str(dur_sec))

			ftg_ind = 0
			for ftg in amvnews_data['video_footage']:
				self.videoFootageBox.insertItem(ftg_ind, ftg)
				ftg_ind += 1

			self.ytURLBox.setText(amvnews_data['video_youtube_url'])
			self.amvOrgURLBox.setText(amvnews_data['org_video_url'])
			self.editorYTChannelBox.setText(amvnews_data['editor_youtube_channel_url'])
			self.editorAmvnewsProfileBox.setText(amvnews_data['editor_amvnews_profile_url'])

		else:
			unresolved_host_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'No response',
														'amvnews.ru is currently unresponsive. Check your\n'
														'internet connection or try again later.')
			unresolved_host_win.exec_()

	def dl_amvnews(self, url):
		amvnews_id = url.split('id=')[1]
		dl_url = 'https://amvnews.ru/index.php?go=Files&file=down&id={}'.format(amvnews_id)
		webbrowser.open(dl_url)

	def local_file_clicked(self):
		file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a file')
		if file_path[0]:
			self.localFileBox.setText(file_path[0])

	def local_file_changed(self):
		if self.entry_settings['auto_gen_thumbs'] == 1 and check_for_ffmpeg.check():
			thumb_path = common_vars.thumb_path() + '\\' + self.vidid + '.jpg'
			if self.localFileBox.text() != '' and self.thumbnailBox.text() == '':
				QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
				generate_thumb.thumb_generator(self.localFileBox.text(), thumb_path, randint(1, 5),
											   fetch_video_length.return_duration(self.localFileBox.text()))
				self.thumbnailBox.setText(thumb_path)
				QtWidgets.QApplication.restoreOverrideCursor()

	def get_video_length(self):
		ffmpeg_exists = check_for_ffmpeg.check()
		ok_to_proceed = True

		if not os.path.isfile(self.localFileBox.text()) or mimetypes.guess_type(self.localFileBox.text())[0] is \
				None or mimetypes.guess_type(self.localFileBox.text())[0].startswith('video') is False:
			ok_to_proceed = False

		if ffmpeg_exists and ok_to_proceed:
			result = fetch_video_length.return_duration(self.localFileBox.text())
			vid_length = int(result)
			vid_min = vid_length // 60
			vid_sec = vid_length % 60

			self.lengthMinDrop.setCurrentIndex(vid_min + 1)
			self.lengthSecDrop.setCurrentIndex(vid_sec + 1)

	def en_dis_watch_button(self):
		if self.localFileBox.text() == '':
			self.localFileWatch.setDisabled(True)
			self.localFileX.setDisabled(True)
		else:
			self.localFileWatch.setEnabled(True)
			self.localFileX.setEnabled(True)

	def play_vid(self):
		play_vid_conn = sqlite3.connect(common_vars.video_db())
		play_vid_cursor = play_vid_conn.cursor()

		try:
			startfile(self.localFileBox.text())
			if self.edit_entry:  # Increases the play count for this video in the database
				play_vid_cursor.execute('SELECT play_count FROM {} WHERE video_id = ?'.format(self.inp_subdb),
										(self.inp_vidid,))
				curr_play_ct = int(play_vid_cursor.fetchone()[0])
				curr_play_ct += 1
				play_vid_cursor.execute('UPDATE {} SET play_count = ? WHERE video_id = ?'.format(self.inp_subdb),
										(str(curr_play_ct), self.inp_vidid))
				play_vid_conn.commit()

		except:
			file_not_found_msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'File not found',
													   'Local file not found. Please check the file path.')
			file_not_found_msg.exec_()

		play_vid_conn.close()

	def thumbnail_clicked(self):
		file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a thumbnail', '',
														  'Image files (*.png *.jpg *.jpeg *.bmp *.gif)')
		if file_path[0]:
			if file_path[0] == str(getcwd() + '/thumbnails/no_thumb.jpg').replace('\\', '/'):
				thumb_err = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Invalid selection',
												  'This is a restricted file, and cannot be manually chosen as a\n'
												  'thumbnail. Please select a different file.')
				thumb_err.exec_()
			else:
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

		elif btn == 'thumbs':
			if self.thumbnailBox.text() != '':
				self.thumbnailX.setEnabled(True)
			else:
				self.thumbnailX.setDisabled(True)

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
		if common_vars.get_ffmpeg_path() == '' or common_vars.get_ffprobe_path() == '':
			ffmpeg_exists = False
		else:
			ffmpeg_exists = True
		# ffmpeg_exists = check_for_ffmpeg.check()
		temp_thumb_dir = getcwd() + '\\thumbnails\\temp'
		new_thumb_path_partial = common_vars.thumb_path() + '\\{}.jpg'.format(self.vidid)
		new_thumb_path_full = getcwd() + new_thumb_path_partial
		ok_to_proceed = True
		check_for_thumb_path.check_for_thumb_path()

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

		if os.path.isfile(new_thumb_path_full):
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
					copy(temp_thumb_dir + '\\{}-{}.jpg'.format(self.vidid, thumb_ind), new_thumb_path_full)

					# Update thumbnail text box
					self.thumbnailBox.clear()
					self.thumbnailBox.setText(new_thumb_path_full)

		else:
			"""ffmpeg_needed = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'FFMPEG needed',
												  'In order to use this function you will need FFMPEG. Please follow<br>'
												  'the below instructions:<br><br>'
												  '<b><u>Option 1</u></b><br>'
												  '1. Download the latest full build from '
												  '<a href="https://www.gyan.dev/ffmpeg/builds/">here</a>.<br><br>'
												  '2. Open the archive, navigate to the \'bin\' folder, and put the ffmpeg.exe<br>'
												  'and ffprobe.exe files in your AMV Tracker directory.<br><br>'
												  '3. That\'s it! Close this window and press the "Generate thumbnail"<br> '
												  'button again.<br><br>'
												  '<b><u>Option 2</u></b><br>'
												  'If you would rather install ffmpeg directly and have it be available<br>'
												  'in your Windows PATH variables, open PowerShell and type:'
												  '<p style="font-family:System; font-size:8px;">winget install Gyan.FFmpeg</p>'
												  'You may need to then restart AMV Tracker to begin generating thumbnails.')"""
			ffmpeg_needed = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'ffmpeg needed',
												  'In order to use this function, you will need ffmpeg. Please go to\n'
												  'AMV Tracker\'s Settings and follow the instructions under the\n'
												  '"ffmpeg / ffprobe" section in the "Data import" tab.')
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

	def back_button_clicked(self):
		if not self.edit_entry and self.thumbnailBox.text() != '':
			if os.path.isfile(self.thumbnailBox.text()):
				os.remove(self.thumbnailBox.text())

		self.close()

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

			if self.entry_settings['check_video_source'] == 1 and self.videoSourceTextBox.text() == '':
				missing_fields_list.append('\u2022 Video source')

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

			final_thumb_path_list = self.thumbnailBox.text().split(getcwd())
			if len(final_thumb_path_list) > 1:
				final_thumb_path = final_thumb_path_list[1]
			else:
				final_thumb_path = final_thumb_path_list[0]
			output_dict['vid_thumb_path'] = final_thumb_path

			if not self.edit_entry:
				output_dict['sub_db'] = ''
			else:
				output_dict['sub_db'] = self.inp_subdb

			output_dict['video_source'] = self.videoSourceTextBox.text()

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
