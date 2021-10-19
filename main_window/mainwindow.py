import datetime
import sqlite3
from os import getcwd, startfile

import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

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
		self.filterOneVidIDs = []
		self.filterTwoVidIDs = []

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
		self.custListBtn.setIcon(self.custListIcon)
		self.custListBtn.setFixedSize(40, 40)
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
		                         'Date added to database', 'Custom list', 'Editor username']
		self.basicFiltersList.sort()
		self.basicFiltersList.insert(0, 'Show all')
		self.basicFiltersDrop = QtWidgets.QComboBox()
		for item in self.basicFiltersList:
			self.basicFiltersDrop.addItem(item)
		self.basicFiltersDrop.setFixedWidth(230)
		self.basicFiltersDrop.setFont(self.largeFont)
		self.basicFiltersDrop.setMaxVisibleItems(15)

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
		self.init_table()

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

		# Populate table
		self.basic_filter_dropdown_clicked()

		# Signals / slots
		self.addVideoBtn.clicked.connect(self.add_video_pushed)
		self.settingsBtn.clicked.connect(self.settings_button_pushed)
		self.subDBDrop.currentIndexChanged.connect(self.basic_filter_dropdown_clicked)
		self.basicFiltersDrop.currentIndexChanged.connect(self.basic_filter_dropdown_clicked)
		self.basicFilterListWid.itemClicked.connect(self.filter_set_1)
		self.searchTable.cellClicked.connect(lambda: self.table_cell_clicked(
			int(self.searchTable.currentRow()), int(self.searchTable.currentColumn()),
			self.searchTable.item(self.searchTable.currentRow(), 0).text()))

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

	def init_table(self):
		init_tab_sett_conn = sqlite3.connect(common_vars.settings_db())
		init_tab_sett_cursor = init_tab_sett_conn.cursor()
		init_tab_sett_cursor.execute('SELECT field_name_display, displ_order, col_width FROM search_field_lookup WHERE '
		                             'visible_in_search_view = 1')
		field_data = init_tab_sett_cursor.fetchall()
		field_data.sort(key=lambda x: int(x[1]))
		table_header_dict = {x[0]: x[2] for x in field_data}
		table_header_dict['Edit entry'] = 70
		table_header_dict['Watch'] = 60
		table_header_list = [x[0] for x in field_data]
		table_header_list.insert(1, 'Edit entry')
		table_header_list.insert(2, 'Watch')

		self.searchTable.setColumnCount(len(table_header_list))
		self.searchTable.setHorizontalHeaderLabels(table_header_list)
		for ind in range(0, len(table_header_list)):
			self.searchTable.setColumnWidth(ind, table_header_dict[self.searchTable.horizontalHeaderItem(ind).text()])
		self.searchTable.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
		self.searchTable.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

		self.searchTable.setColumnHidden(0, True)  # Hide VidID column

	def basic_filter_dropdown_clicked(self):
		self.basicFilterListWid.clear()

		bf_drop_conn = sqlite3.connect(common_vars.video_db())
		bf_drop_cursor = bf_drop_conn.cursor()

		bf_drop_sub_db_friendly = self.subDBDrop.currentText()
		bf_drop_sub_db_internal = common_vars.sub_db_lookup()[bf_drop_sub_db_friendly]
		filter_text = self.basicFiltersDrop.currentText()

		bf_drop_cursor.execute('SELECT video_id FROM {}'.format(bf_drop_sub_db_internal))
		self.filterOneVidIDs = self.filterTwoVidIDs = [x[0] for x in bf_drop_cursor.fetchall()]

		if filter_text == 'Show all':
			list_wid_pop = []
			self.filter_set_1()
		elif filter_text == 'Custom list':
			list_wid_pop = [k for k, v in common_vars.custom_list_lookup().items()]
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Date added to database':
			list_wid_pop = ['Today', 'Yesterday', 'Last 7 days', 'Last 30 days', 'Last 60 days', 'Last 90 days',
			                'Last 6 months', 'Last 12 months', 'Last 24 months']

		elif filter_text == 'Editor username':
			bf_drop_cursor.execute('SELECT primary_editor_username FROM {}'.format(bf_drop_sub_db_internal))
			editors = bf_drop_cursor.fetchall()
			list_wid_pop = list(set(y for x in editors for y in x))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Year released':
			bf_drop_cursor.execute('SELECT release_date FROM {}'.format(bf_drop_sub_db_internal))
			dates = bf_drop_cursor.fetchall()
			list_wid_pop = list(set([y[:4] for x in dates for y in x]))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort()
			list_wid_pop.insert(0, 'Unknown')
			list_wid_pop.insert(0, 'Not specified')

		elif filter_text == 'Favorited videos':
			list_wid_pop = ['Marked as favorite', 'Not marked as favorite']

		elif filter_text == 'My rating':
			list_wid_pop = [str(rat * 0.5) for rat in range(0, 21)]
			list_wid_pop.insert(0, 'Unrated')

		elif filter_text == 'Notable videos':
			list_wid_pop = ['Marked as notable', 'Not marked as notable']

		elif filter_text == 'Song artist':
			bf_drop_cursor.execute('SELECT song_artist FROM {}'.format(bf_drop_sub_db_internal))
			artists = bf_drop_cursor.fetchall()
			list_wid_pop = list(set(y for x in artists for y in x))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Song genre':
			bf_drop_cursor.execute('SELECT song_genre FROM {}'.format(bf_drop_sub_db_internal))
			song_genres = bf_drop_cursor.fetchall()
			list_wid_pop = list(set(y for x in song_genres for y in x))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Star rating':
			list_wid_pop = ['Unrated or 0.0', '0.50 - 1.99', '2.00 - 2.49', '2.50 - 2.99', '3.00 - 3.49', '3.50 - 3.99',
			                '4.00 - 4.49', '4.50 - 5.00']

		elif filter_text == 'Studio':
			bf_drop_cursor.execute('SELECT studio FROM {}'.format(bf_drop_sub_db_internal))
			studios = bf_drop_cursor.fetchall()
			list_wid_pop = list(set(y for x in studios for y in x))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Video footage':
			list_wid_pop = []
			bf_drop_cursor.execute('SELECT video_footage FROM {}'.format(bf_drop_sub_db_internal))
			for ftg_tup in bf_drop_cursor.fetchall():
				for ftg_grp in list(ftg_tup):
					for ftg in ftg_grp.split('; '):
						if ftg not in list_wid_pop:
							list_wid_pop.append(ftg)
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Video length':
			list_wid_pop = [str(x * 30) + ' - ' + str(((x + 1) * 30) - 1) + ' sec' for x in range(0, 14)]
			list_wid_pop.append('420+ sec')
			list_wid_pop.insert(0, 'Not specified')

		else:
			list_wid_pop = []

		for item in list_wid_pop:
			self.basicFilterListWid.addItem(item)

		bf_drop_conn.close()

	def filter_set_1(self):
		bf_conn = sqlite3.connect(common_vars.video_db())
		bf_cursor = bf_conn.cursor()

		bf_sel_subdb_friendly = self.subDBDrop.currentText()
		bf_sel_subdb_internal = common_vars.sub_db_lookup()[bf_sel_subdb_friendly]
		vidids_list = []
		filtered_vidids_1 = []
		filter_by_text = self.basicFiltersDrop.currentText()
		sel_filter = ''

		if filter_by_text == 'Show all':
			bf_cursor.execute('SELECT video_id FROM {}'.format(bf_sel_subdb_internal))
			for vidid_tup in bf_cursor.fetchall():
				filtered_vidids_1.append(vidid_tup[0])
		else:
			sel_filter = self.basicFilterListWid.currentItem().text()

		if filter_by_text == 'Custom list':
			bf_cursor.execute('SELECT vid_ids FROM custom_lists WHERE list_name = ?', (sel_filter,))
			filtered_vidids_1 = bf_cursor.fetchall()[0][0].split('; ')

		elif filter_by_text == 'Date added to database':
			today = datetime.date.today()
			bf_cursor.execute('SELECT video_id, date_entered FROM {}'.format(bf_sel_subdb_internal))
			for tup in bf_cursor.fetchall():
				if tup[1] != '':
					ent_date_list = [int(x) for x in tup[1].split('/')]
					ent_date = datetime.date(ent_date_list[0], ent_date_list[1], ent_date_list[2])
					delta = today - ent_date
					vidids_list.append((tup[0], delta.days))

			for vid in vidids_list:
				if (sel_filter == 'Today' and vid[1] == 0) or \
						(sel_filter == 'Yesterday' and vid[1] == 1) or \
						(sel_filter == 'Last 7 days' and vid[1] <= 7) or \
						(sel_filter == 'Last 30 days' and vid[1] <= 30) or \
						(sel_filter == 'Last 60 days' and vid[1] <= 60) or \
						(sel_filter == 'Last 90 days' and vid[1] <= 90) or \
						(sel_filter == 'Last 6 months' and vid[1] <= 180) or \
						(sel_filter == 'Last 12 months' and vid[1] <= 365) or \
						(sel_filter == 'Last 24 months' and vid[1] <= 730):
					filtered_vidids_1.append(vid[0])

		elif filter_by_text == 'Editor username':
			bf_cursor.execute('SELECT video_id FROM {} WHERE primary_editor_username = ? OR '
			                  'primary_editor_pseudonyms LIKE ? OR addl_editors LIKE ?'.format(bf_sel_subdb_internal),
			                  (sel_filter, sel_filter, sel_filter))
			for vidid_tup in bf_cursor.fetchall():
				filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Favorited videos':
			if sel_filter == 'Marked as favorite':
				fav = 1
			else:
				fav = 0
			bf_cursor.execute('SELECT video_id FROM {} WHERE favorite = ?'.format(bf_sel_subdb_internal), (fav,))
			for vidid_tup in bf_cursor.fetchall():
				filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'My rating':
			if sel_filter == 'Unrated':
				mr_inp_text = ''
			else:
				mr_inp_text = sel_filter
			bf_cursor.execute('SELECT video_id FROM {} WHERE my_rating = ?'.format(bf_sel_subdb_internal),
			                  (mr_inp_text,))
			for vidid_tup in bf_cursor.fetchall():
				filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Notable videos':
			if sel_filter == 'Marked as notable':
				notable = 1
			else:
				notable = 0
			bf_cursor.execute('SELECT video_id FROM {} WHERE notable = ?'.format(bf_sel_subdb_internal), (notable,))
			for vidid_tup in bf_cursor.fetchall():
				filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Song artist' or filter_by_text == 'Song genre' or filter_by_text == 'Studio':
			column_name = filter_by_text.lower().replace(' ', '_')
			bf_cursor.execute('SELECT video_id FROM {} WHERE {} = ?'.format(bf_sel_subdb_internal, column_name),
			                  (sel_filter,))
			for vidid_tup in bf_cursor.fetchall():
				filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Star rating':
			if sel_filter == 'Unrated or 0.0':
				bf_cursor.execute('SELECT video_id FROM {} WHERE star_rating = "" or star_rating = 0.0'
				                  .format(bf_sel_subdb_internal))
				for vidid_tup in bf_cursor.fetchall():
					filtered_vidids_1.append(vidid_tup[0])
			else:
				star_rat_rng = [float(x) for x in sel_filter.split(' - ')]
				bf_cursor.execute('SELECT video_id, star_rating FROM {} WHERE star_rating != ""'
				                  .format(bf_sel_subdb_internal))
				for vidid_tup in bf_cursor.fetchall():
					if star_rat_rng[0] <= float(vidid_tup[1]) <= star_rat_rng[1]:
						filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Video footage':
			bf_cursor.execute('SELECT video_id, video_footage FROM {}'.format(bf_sel_subdb_internal))
			for vidid_tup in bf_cursor.fetchall():
				for ftg in vidid_tup[1].split('; '):
					if sel_filter == ftg:
						filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Video length':
			if sel_filter == 'Not specified':
				bf_cursor.execute('SELECT video_id FROM {} WHERE video_length = ""'.format(bf_sel_subdb_internal))
				for vidid_tup in bf_cursor.fetchall():
					filtered_vidids_1.append(vidid_tup[0])

			else:
				bf_cursor.execute('SELECT video_id, video_length FROM {} WHERE video_length != ""'
				                  .format(bf_sel_subdb_internal))
				if sel_filter == '420+ sec':
					for vidid_tup in bf_cursor.fetchall():
						if int(vidid_tup[1]) >= 420:
							filtered_vidids_1.append(vidid_tup[0])
				else:
					dur_rng = [int(x) for x in sel_filter[:-4].split(' - ')]
					for vidid_tup in bf_cursor.fetchall():
						if dur_rng[0] <= vidid_tup[1] <= dur_rng[1]:
							filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Year released':
			if sel_filter == 'Not specified':
				bf_cursor.execute('SELECT video_id WHERE release_date = "" AND release_date_unknown = 0')
				for vidid_tup in bf_cursor.fetchall():
					filtered_vidids_1.append(vidid_tup[0])
			elif sel_filter == 'Unknown':
				bf_cursor.execute('SELECT video_id WHERE release_date_unknown = 1')
				for vidid_tup in bf_cursor.fetchall():
					filtered_vidids_1.append(vidid_tup[0])
			else:
				bf_cursor.execute('SELECT video_id, release_date FROM {}'.format(bf_sel_subdb_internal))
				for vidid_tup in bf_cursor.fetchall():
					if sel_filter == vidid_tup[1][:4]:
						filtered_vidids_1.append(vidid_tup[0])

		bf_conn.close()
		self.filterOneVidIDs = filtered_vidids_1
		self.populate_table(self.filterOneVidIDs, self.filterTwoVidIDs)

	def populate_table(self, inp_vidids_1, inp_vidids_2):
		self.searchTable.setRowCount(0)
		final_vidid_list = list(set(inp_vidids_1) & set(inp_vidids_2))
		sub_db = common_vars.sub_db_lookup()[self.subDBDrop.currentText()]
		pop_table_db_conn = sqlite3.connect(common_vars.video_db())
		pop_table_db_cursor = pop_table_db_conn.cursor()
		pop_table_settings_conn = sqlite3.connect(common_vars.settings_db())
		pop_table_settings_cursor = pop_table_settings_conn.cursor()

		pop_table_settings_cursor.execute('SELECT field_name_internal, displ_order FROM search_field_lookup WHERE '
		                                  'visible_in_search_view = 1')
		field_lookup_dict = dict(
			(x[0], x[1] + 2) if x[1] != 0 else (x[0], x[1]) for x in pop_table_settings_cursor.fetchall())

		watch_icon = QtGui.QIcon(getcwd() + '/icons/play-icon.png')
		edit_icon = QtGui.QIcon(getcwd() + '/icons/edit-icon.png')

		matching_vids = []
		for vidid in final_vidid_list:
			pop_table_db_cursor.execute('SELECT primary_editor_username FROM {} WHERE video_id = ?'.format(sub_db),
			                            (vidid,))
			matching_vids.append(pop_table_db_cursor.fetchone())
		matching_vid_check = [x for x in matching_vids if x is not None]

		self.searchTable.setSortingEnabled(False)
		if matching_vid_check != []:  # If there is at least one result in the sub-db
			for row in range(0, len(final_vidid_list)):
				self.searchTable.insertRow(row)
				for field, col in field_lookup_dict.items():
					query = 'SELECT {} FROM {} '.format(field, sub_db)
					pop_table_db_cursor.execute(query + 'WHERE video_id = ?', (final_vidid_list[row],))
					temp_val = pop_table_db_cursor.fetchall()[0][0]

					pop_table_db_cursor.execute('SELECT local_file FROM {} WHERE video_id = ?'.format(sub_db),
					                            (final_vidid_list[row],))
					loc_file_check = pop_table_db_cursor.fetchall()[0][0]
					if loc_file_check != '':
						loc_file_pop = True
					else:
						loc_file_pop = False

					# Populating play local video icon
					if loc_file_pop:
						watch_icon_item = QtWidgets.QTableWidgetItem()
						watch_icon_item.setIcon(watch_icon)
						watch_icon_to_insert = QtWidgets.QTableWidgetItem(watch_icon_item)
						self.searchTable.setItem(row, 2, watch_icon_to_insert)

					# Populating edit icon
					edit_icon_item = QtWidgets.QTableWidgetItem()
					edit_icon_item.setIcon(edit_icon)
					edit_icon_to_insert = QtWidgets.QTableWidgetItem(edit_icon_item)
					self.searchTable.setItem(row, 1, edit_icon_to_insert)

					# Populating table with data from db file
					if temp_val is None:
						val_to_insert = QtWidgets.QTableWidgetItem('')
					else:
						if field == 'star_rating' or field == 'my_rating':
							val_to_insert = QtWidgets.QTableWidgetItem()
							val_to_insert.setTextAlignment(QtCore.Qt.AlignCenter)
							val_to_insert.setData(QtCore.Qt.DisplayRole, temp_val)
						elif field == 'video_length' or field == 'sequence':
							val_to_insert = QtWidgets.QTableWidgetItem()
							val_to_insert.setTextAlignment(QtCore.Qt.AlignCenter)
							val_to_insert.setData(QtCore.Qt.DisplayRole, temp_val)
						else:
							val_to_insert = QtWidgets.QTableWidgetItem(str(temp_val))

					self.searchTable.setItem(row, col, val_to_insert)

		self.searchTable.setSortingEnabled(True)
		self.searchTable.sortByColumn(field_lookup_dict['video_title'], QtCore.Qt.AscendingOrder)
		self.searchTable.sortByColumn(field_lookup_dict['primary_editor_username'], QtCore.Qt.AscendingOrder)

		pop_table_db_conn.close()
		pop_table_settings_conn.close()

	def update_col_width(self):
		pass

	# TODO: Write this method

	def table_cell_clicked(self, row, col, vidid):
		cell_clicked_db_conn = sqlite3.connect(common_vars.video_db())
		cell_clicked_db_cursor = cell_clicked_db_conn.cursor()
		subdb = common_vars.sub_db_lookup()[self.subDBDrop.currentText()]

		if col == 2:
			cell_clicked_db_cursor.execute('SELECT local_file FROM {} WHERE video_id = ?'.format(subdb), (vidid,))
			file_path = cell_clicked_db_cursor.fetchone()[0].replace('\\', '/')
			if file_path != '':
				try:
					startfile(file_path)
				except:
					file_not_found_msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'File not found',
					                                           'Local file not found. Please check the file path in the\n'
					                                           'video\'s AMV Tracker profile.')
					file_not_found_msg.exec_()
			else:
				no_file_msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'No local file specified',
				                                    'You have not specified a local file path for this video. Please\n'
				                                    'go to the video profile to add a local file path.')
				no_file_msg.exec_()
