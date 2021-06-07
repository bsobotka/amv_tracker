import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import sqlite3
import xlrd

from os import getcwd, listdir
from shutil import copyfile

from misc_files import checkbox_list_window, common_vars, generic_one_line_entry_window


class Worker(QtCore.QObject):
	finished = QtCore.pyqtSignal()
	progress = QtCore.pyqtSignal(str, int, int)

	def __init__(self, f_path):
		super(Worker, self).__init__()
		self.f_path = f_path

	def run(self):
		###
		conn = sqlite3.connect(common_vars.video_db())
		cursor = conn.cursor()
		book = xlrd.open_workbook(self.f_path)

		# Move data
		for sht_ind in range(0, book.nsheets):
			sheet = book.sheet_by_index(sht_ind)
			tn = 'sub_db_{}'.format(sht_ind)

			cursor.execute(
				'CREATE TABLE IF NOT EXISTS "sub_db_{}" (	"video_id"	,"primary_editor_username"	TEXT,'
				'"primary_editor_pseudonyms"	TEXT, "addl_editors"	TEXT, "studio"	TEXT, "video_title"	TEXT,'
				'"release_date"	TEXT, "release_date_unknown"  INTEGER, "star_rating"	REAL, '
				'"video_footage"	TEXT, "song_artist"	TEXT, '
				'"song_title"	TEXT, "song_genre"	TEXT, "video_length"	INTEGER, "contests_entered"	TEXT,'
				'"awards_won"	TEXT, "video_description"	TEXT, "my_rating"	REAL, "notable"	INTEGER, '
				'"favorite"	INTEGER, "tags_1"	TEXT, "tags_2"	TEXT, "tags_3"	TEXT, "tags_4"	TEXT, '
				'"tags_5"	TEXT, "tags_6"	TEXT, "comments"	TEXT, "video_youtube_url"	TEXT, '
				'"video_org_url"	TEXT, "video_amvnews_url"	TEXT, "video_other_url"	TEXT, "local_file"	TEXT, '
				'"editor_youtube_channel_url"	TEXT, "editor_org_profile_url"	TEXT, '
				'"editor_amvnews_profile_url"	TEXT, "editor_other_profile_url"	TEXT, "sequence"	INTEGER, '
				'"date_entered"	TEXT, PRIMARY KEY("video_id"))'.format(sht_ind))

			cursor.execute('INSERT OR IGNORE INTO db_name_lookup (table_name, user_subdb_name) VALUES (?, ?)',
			               (tn, sheet.name))

			for row in range(1, sheet.nrows):
				field_dict = {}
				field_dict['addl_editors'] = ''
				field_dict['studio'] = ''
				field_dict['video_org_url'] = ''
				field_dict['video_youtube_url'] = ''
				field_dict['video_amvnews_url'] = ''
				field_dict['video_other_url'] = ''

				if '//' not in str(sheet.cell_value(row, 0)):
					field_dict['primary_editor_username'] = str(sheet.cell_value(row, 0))
				else:
					field_dict['primary_editor_username'] = str(sheet.cell_value(row, 0)).split(' // ')[0]
					field_dict['addl_editors'] = str(sheet.cell_value(row, 0)).split(' // ')[1]

				field_dict['video_title'] = str(sheet.cell_value(row, 1))
				field_dict['my_rating'] = float(sheet.cell_value(row, 2))
				field_dict['star_rating'] = float(sheet.cell_value(row, 3))
				field_dict['tags_1'] = str(sheet.cell_value(row, 4)).replace(', ', '; ').lower()
				if str(sheet.cell_value(row, 5)) == '?':
					field_dict['release_date'] = ''
					field_dict['release_date_unknown'] = 1
				else:
					rel_date = xlrd.xldate_as_datetime(int(sheet.cell_value(row, 5)), 0).isoformat()[:10]
					field_dict['release_date'] = rel_date
					field_dict['release_date_unknown'] = 0
				field_dict['video_footage'] = str(sheet.cell_value(row, 6)).replace(' // ', '; ')
				field_dict['song_artist'] = str(sheet.cell_value(row, 7))
				field_dict['song_title'] = str(sheet.cell_value(row, 8))
				field_dict['song_genre'] = str(sheet.cell_value(row, 9))
				if str(sheet.cell_value(row, 10)) == '':
					field_dict['video_length'] = ''
				else:
					field_dict['video_length'] = int(sheet.cell_value(row, 10))
				field_dict['tags_2'] = str(sheet.cell_value(row, 11)).replace(', ', '; ').lower()
				field_dict['tags_3'] = str(sheet.cell_value(row, 12)).replace(', ', '; ').lower()
				field_dict['comments'] = str(sheet.cell_value(row, 13))
				if 'animemusicvideos.org' in str(sheet.cell_value(row, 14)):
					field_dict['video_org_url'] = str(sheet.cell_value(row, 14))
				elif 'yout' in str(sheet.cell_value(row, 14)):
					field_dict['video_youtube_url'] = str(sheet.cell_value(row, 14))
				elif 'amvnews' in str(sheet.cell_value(row, 14)):
					field_dict['video_amvnews_url'] = str(sheet.cell_value(row, 14))
				else:
					field_dict['video_other_url'] = str(sheet.cell_value(row, 14))
				field_dict['primary_editor_pseudonyms'] = str(sheet.cell_value(row, 15)).replace(', ', '; ')
				field_dict['local_file'] = str(sheet.cell_value(row, 16))
				field_dict['contests_entered'] = str(sheet.cell_value(row, 17))
				field_dict['video_id'] = str(sheet.cell_value(row, 18))
				if str(sheet.cell_value(row, 19)) == '':
					field_dict['sequence'] = ''
				else:
					field_dict['sequence'] = int(sheet.cell_value(row, 19))
				field_dict['date_entered'] = str(sheet.cell_value(row, 20))
				field_dict['notable'] = 0
				field_dict['favorite'] = 0

				cursor.execute('INSERT OR IGNORE INTO sub_db_{} (video_id) VALUES (?)'.format(sht_ind),
				               (field_dict['video_id'],))
				conn.commit()

				cursor.execute(
					'UPDATE sub_db_{} SET (primary_editor_username, addl_editors, studio, video_title, my_rating, star_rating, '
					'tags_1, release_date, release_date_unknown, video_footage, song_artist, song_title, '
					'song_genre, video_length, tags_2, tags_3, comments, video_org_url, video_youtube_url, '
					'video_amvnews_url, video_other_url, primary_editor_pseudonyms, local_file, '
					'contests_entered, sequence, date_entered, notable, favorite) = (?, ?, ?, ?, ?, ?, ?, ?, '
					'?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) WHERE video_id = ?'.format(
						sht_ind),
					(field_dict['primary_editor_username'], field_dict['addl_editors'], field_dict['studio'],
					 field_dict['video_title'], field_dict['my_rating'], field_dict['star_rating'],
					 field_dict['tags_1'], field_dict['release_date'], field_dict['release_date_unknown'],
					 field_dict['video_footage'], field_dict['song_artist'], field_dict['song_title'],
					 field_dict['song_genre'], field_dict['video_length'], field_dict['tags_2'],
					 field_dict['tags_3'], field_dict['comments'], field_dict['video_org_url'],
					 field_dict['video_youtube_url'], field_dict['video_amvnews_url'],
					 field_dict['video_other_url'], field_dict['primary_editor_pseudonyms'],
					 field_dict['local_file'], field_dict['contests_entered'], field_dict['sequence'],
					 field_dict['date_entered'], field_dict['notable'], field_dict['favorite'],
					 field_dict['video_id']))

				self.progress.emit(book.sheet_names()[sht_ind], row, sheet.nrows)

		conn.commit()
		conn.close()
		self.finished.emit()


class DataMgmtSettings(QtWidgets.QWidget):
	def __init__(self):
		super(DataMgmtSettings, self).__init__()

		self.boldFont = QtGui.QFont()
		self.boldFont.setBold(True)

		self.gridLayout = QtWidgets.QGridLayout()
		self.gridLayout.setAlignment(QtCore.Qt.AlignTop)

		self.importButton = QtWidgets.QPushButton('Import data from...')
		self.importButton.setFixedWidth(150)

		self.importDrop = QtWidgets.QComboBox()
		self.importDrop.setFixedWidth(180)
		self.importDrop.addItem('Previous AMV Tracker version')
		self.importDrop.addItem('CSV document')

		self.pBar = QtWidgets.QProgressBar()
		self.pBar.setGeometry(30, 40, 300, 25)
		self.pBar.setWindowTitle('Importing...')
		self.pBar.setInvertedAppearance(False)
		self.pBar.setTextVisible(True)
		self.pBar.setAlignment(QtCore.Qt.AlignCenter)
		self.pBar.move(1000, 600)

		grid_v_index = 0

		self.gridLayout.addWidget(self.importButton, grid_v_index, 0, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.importDrop, grid_v_index, 1, alignment=QtCore.Qt.AlignLeft)
		grid_v_index += 1

		self.gridLayout.setRowMinimumHeight(grid_v_index, 20)
		grid_v_index += 1

		self.dbOperationsLabel = QtWidgets.QLabel()
		self.dbOperationsLabel.setText('Database operations')
		self.dbOperationsLabel.setFont(self.boldFont)
		self.gridLayout.addWidget(self.dbOperationsLabel, grid_v_index, 0, alignment=QtCore.Qt.AlignLeft)
		grid_v_index += 1

		self.newDBButton = QtWidgets.QPushButton('Create new database')
		self.newDBButton.setFixedWidth(150)
		self.gridLayout.addWidget(self.newDBButton, grid_v_index, 0, 1, 2, alignment=QtCore.Qt.AlignLeft)
		grid_v_index += 1

		self.changeCurrDBButton = QtWidgets.QPushButton('Select working database')
		self.changeCurrDBButton.setFixedWidth(150)
		self.gridLayout.addWidget(self.changeCurrDBButton, grid_v_index, 0, alignment=QtCore.Qt.AlignLeft)
		grid_v_index += 1

		self.gridLayout.setRowMinimumHeight(grid_v_index, 20)
		grid_v_index += 1

		self.subDBOperationsLabel = QtWidgets.QLabel()
		self.subDBOperationsLabel.setText('Sub-database operations')
		self.subDBOperationsLabel.setFont(self.boldFont)
		self.gridLayout.addWidget(self.subDBOperationsLabel, grid_v_index, 0, alignment=QtCore.Qt.AlignLeft)
		grid_v_index += 1

		self.addSubDBButton = QtWidgets.QPushButton('Add sub-DB')
		self.addSubDBButton.setFixedWidth(150)
		self.gridLayout.addWidget(self.addSubDBButton, grid_v_index, 0, alignment=QtCore.Qt.AlignLeft)
		grid_v_index += 1

		self.renameSubDBsButton = QtWidgets.QPushButton('Rename sub-DB')
		self.renameSubDBsButton.setFixedWidth(150)
		self.gridLayout.addWidget(self.renameSubDBsButton, grid_v_index, 0, alignment=QtCore.Qt.AlignLeft)
		grid_v_index += 1

		self.deleteSubDBButton = QtWidgets.QPushButton('Delete sub-DB')
		self.deleteSubDBButton.setFixedWidth(150)
		self.gridLayout.addWidget(self.deleteSubDBButton, grid_v_index, 0, alignment=QtCore.Qt.AlignLeft)
		grid_v_index += 1

		# Signals/slots
		self.importButton.clicked.connect(lambda: self.import_btn_clicked())
		self.newDBButton.clicked.connect(lambda: self.create_db())
		self.changeCurrDBButton.clicked.connect(lambda: self.select_db())
		self.addSubDBButton.clicked.connect(lambda: self.add_subdb())
		self.renameSubDBsButton.clicked.connect(lambda: self.rename_subdb())
		self.deleteSubDBButton.clicked.connect(lambda: self.delete_subdb())

	def import_btn_clicked(self):
		if self.importDrop.currentText() == 'Previous AMV Tracker version':
			f_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select AMVT database', '', 'Spreadsheet file (*xls)')[
				0]
			if f_path != '':
				self.thrd = QtCore.QThread()
				self.worker = Worker(f_path)
				self.worker.moveToThread(self.thrd)

				self.pBar.show()

				self.thrd.started.connect(self.worker.run)
				self.worker.finished.connect(self.thrd.quit)
				self.worker.finished.connect(self.worker.deleteLater)
				self.thrd.finished.connect(self.thrd.deleteLater)
				self.worker.progress.connect(self.show_import_progress)

				self.thrd.start()

		else:  # CSV document
			print('csv')

	def show_import_progress(self, sub_db_name, n, total):
		self.pBar.setFormat('Importing from {}: Entry {} of {}'.format(sub_db_name, n, total - 1))
		self.pBar.setMaximum(total - 1)
		self.pBar.setValue(n)

	def create_db(self):
		create_db_settings_conn = sqlite3.connect(common_vars.settings_db())
		create_db_settings_cursor = create_db_settings_conn.cursor()

		db_template_src = getcwd() + '/db_files/db_template.db'

		f_dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select the directory in which to create the new '
		                                                         'database...')
		if f_dir:
			existing_files = listdir(f_dir)
			name_db_window = generic_one_line_entry_window.GenericEntryWindow('name_db', inp_1=f_dir,
			                                                                  dupe_check_list=existing_files)

			if name_db_window.exec_():
				full_dir = f_dir + '/' + name_db_window.textBox.text() + '.db'
				copyfile(db_template_src, full_dir)

				set_default_window = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Database created',
				                                           'Database {} has been created. Would you like to set it as\n'
				                                           'the current working database?'
				                                           .format(name_db_window.textBox.text()),
				                                           QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)

				if set_default_window.exec() == QtWidgets.QMessageBox.Yes:
					create_db_settings_cursor.execute('UPDATE db_settings SET path_to_db = ?, db_name = ?',
					                                  (full_dir, name_db_window.textBox.text()))
					create_db_settings_conn.commit()

					db_set_window = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Working database set',
					                                      '{} has been set as the current working database.'
					                                      .format(name_db_window.textBox.text() + '.db'))
					db_set_window.exec_()

		create_db_settings_conn.close()

	def select_db(self):
		select_db_settings_conn = sqlite3.connect(common_vars.settings_db())
		select_db_settings_cursor = select_db_settings_conn.cursor()

		template_path = (getcwd() + '/db_files/db_template.db').replace('\\', '/')
		new_db_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select database file', '', 'Database files (*db)')

		if new_db_path[0] != '':
			# TODO: Test to make sure selected .db file is a valid AMVT database
			if template_path != new_db_path[0].replace('\\', '/'):
				file_name = new_db_path[0].replace('\\', '/').split('/')[-1]
				select_db_settings_cursor.execute('UPDATE db_settings SET path_to_db = ?, db_name = ?', (new_db_path[0],
				                                                                                         file_name[:-3]))
				select_db_settings_conn.commit()

				db_path_updated_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Working database set',
				                                            '{} has been set as the current working database.'
				                                            .format(file_name))
				db_path_updated_win.exec_()

			else:
				invalid_selection_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Invalid selection',
				                                              'You cannot set this database as the current\n'
				                                              'working database. No action has been taken.')
				invalid_selection_win.exec_()

		select_db_settings_conn.close()

	def add_subdb(self):
		add_subdb_conn = sqlite3.connect(common_vars.video_db())
		add_subdb_cursor = add_subdb_conn.cursor()
		existing_subdb_list = [key for key, val in common_vars.sub_db_lookup().items()]
		query = common_vars.sqlite_queries('create table')

		name_subdb_window = generic_one_line_entry_window.GenericEntryWindow('new_subdb',
		                                                                     dupe_check_list=existing_subdb_list)

		if name_subdb_window.exec_():
			new_subdb_name = name_subdb_window.textBox.text()
			new_subdb_number = add_subdb_cursor.execute('SELECT COUNT(*) FROM db_name_lookup').fetchone()[0]

			add_subdb_cursor.execute('INSERT OR IGNORE INTO db_name_lookup VALUES (?, ?)',
			                         ('sub_db_{}'.format(new_subdb_number), new_subdb_name))
			add_subdb_cursor.execute(query.format(str(new_subdb_number)))

			add_subdb_conn.commit()

		add_subdb_conn.close()

	def rename_subdb(self):
		rename_subdb_conn = sqlite3.connect(common_vars.video_db())
		rename_subdb_cursor = rename_subdb_conn.cursor()
		subdb_dict = common_vars.sub_db_lookup()
		subdb_name_list = [key for key, val in subdb_dict.items() if key != 'Main database']

		if subdb_name_list:
			subdb_name_list.sort(key=lambda x: x.casefold())
			rename_subdb_window = generic_one_line_entry_window.GenericEntryWindowWithDrop('rename subdb',
			                                                                               subdb_name_list,
			                                                                               dupe_list=subdb_name_list)
			if rename_subdb_window.exec_():
				db_to_rename = common_vars.sub_db_lookup()[rename_subdb_window.drop.currentText()]
				rename_subdb_cursor.execute('UPDATE db_name_lookup SET user_subdb_name = ? WHERE table_name = ?',
				                            (rename_subdb_window.textBox.text(), db_to_rename))
				rename_subdb_conn.commit()

				subdb_renamed_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Sub-db renamed',
				                                          'Sub-db {} has been renamed to {}.'
				                                          .format(rename_subdb_window.drop.currentText(),
				                                          rename_subdb_window.textBox.text()))
				subdb_renamed_win.exec_()

		else:
			no_subdbs_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'No sub-dbs',
			                                      'This database currently has no sub-databases to rename.\n'
			                                      'No action has been taken.')
			no_subdbs_win.exec_()

		rename_subdb_conn.close()

	def delete_subdb(self):
		delete_subdb_conn = sqlite3.connect(common_vars.video_db())
		delete_subdb_cursor = delete_subdb_conn.cursor()
		subdb_dict = common_vars.sub_db_lookup()
		subdb_name_list = [key for key, val in subdb_dict.items() if key != 'Main database']

		if subdb_name_list:
			subdb_cbox_win = checkbox_list_window.CheckboxListWindow('del sub db', subdb_name_list)
			if subdb_cbox_win.exec_():
				if not subdb_cbox_win.get_checked_boxes():
					nothing_selected = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Nothing selected',
					                                         'No sub-DBs selected -- no action has been taken.')
					nothing_selected.exec_()
				else:
					# TODO: Re-number internal sub-db names
					for subdb in subdb_cbox_win.get_checked_boxes():
						delete_subdb_cursor.execute('DROP TABLE IF EXISTS {}'.format(subdb_dict[subdb]))
						delete_subdb_cursor.execute('DELETE FROM db_name_lookup WHERE user_subdb_name = ?', (subdb,))

					delete_subdb_conn.commit()

		else:
			no_subdbs_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'No sub-dbs',
			                                      'This database currently has no sub-databases to delete.\n'
			                                      'No action has been taken.')
			no_subdbs_win.exec_()

		delete_subdb_conn.close()