import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import sqlite3

from misc_files import common_vars, generic_entry_window


class LibraryManagement(QtWidgets.QWidget):
	def __init__(self):
		super(LibraryManagement, self).__init__()

		# Misc
		grid_vert_ind = 0
		self.headerFont = QtGui.QFont()
		self.headerFont.setBold(True)
		self.headerFont.setUnderline(True)
		self.headerFont.setPixelSize(14)

		# Layouts
		self.gridLayoutMaster = QtWidgets.QGridLayout()
		self.gridLayoutMaster.setAlignment(QtCore.Qt.AlignTop)

		# Row 0
		self.dateTypeHeader = QtWidgets.QLabel()
		self.dateTypeHeader.setText('Data type')
		self.dateTypeHeader.setFont(self.headerFont)
		self.gridLayoutMaster.addWidget(self.dateTypeHeader, grid_vert_ind, 0, alignment=QtCore.Qt.AlignCenter)

		self.dataHeader = QtWidgets.QLabel()
		self.dataHeader.setText('Data')
		self.dataHeader.setFont(self.headerFont)
		self.gridLayoutMaster.addWidget(self.dataHeader, grid_vert_ind, 1, 1, 2, alignment=QtCore.Qt.AlignCenter)
		grid_vert_ind += 1

		# Row 1
		self.dataTypeListWid = QtWidgets.QListWidget()
		self.dataTypeListWid.setFixedSize(120, 140)
		self.dataTypes = ['Editor username', 'Song artist', 'Song genre', 'Video footage', 'Video source']
		for dType in self.dataTypes:
			self.dataTypeListWid.addItem(dType)
		self.gridLayoutMaster.addWidget(self.dataTypeListWid, grid_vert_ind, 0, alignment=QtCore.Qt.AlignTop)

		self.dataListWid = QtWidgets.QListWidget()
		self.dataListWid.setFixedSize(400, 400)
		self.gridLayoutMaster.addWidget(self.dataListWid, grid_vert_ind, 1, 1, 2, alignment=QtCore.Qt.AlignTop)
		grid_vert_ind += 1

		# Row 2
		self.renameButton = QtWidgets.QPushButton('Rename')
		self.renameButton.setFixedWidth(97)
		self.renameButton.setDisabled(True)
		self.gridLayoutMaster.addWidget(self.renameButton, grid_vert_ind, 1, alignment=QtCore.Qt.AlignRight)

		self.deleteButton = QtWidgets.QPushButton('Delete')
		self.deleteButton.setFixedWidth(97)
		self.deleteButton.setDisabled(True)
		self.gridLayoutMaster.addWidget(self.deleteButton, grid_vert_ind, 2, alignment=QtCore.Qt.AlignTop)
		grid_vert_ind += 1

		# Signals / slots
		self.dataTypeListWid.itemClicked.connect(lambda: self.populate_data_listwid(self.dataTypeListWid.currentItem()
																					.text()))
		self.dataListWid.itemClicked.connect(self.data_clicked)
		self.renameButton.clicked.connect(lambda: self.del_rename_btn_pushed('rename'))
		self.deleteButton.clicked.connect(lambda: self.del_rename_btn_pushed('delete'))

	def populate_data_listwid(self, data_type):
		pop_data_conn = sqlite3.connect(common_vars.video_db())
		pop_data_cursor = pop_data_conn.cursor()

		dtype_lookup = {'Editor username': 'primary_editor_username',
						'Song artist': 'song_artist',
						'Song genre': 'song_genre',
						'Video footage': 'video_footage',
						'Video source': 'video_source'}
		dtype_int = dtype_lookup[data_type]

		pop_data_cursor.execute('SELECT table_name FROM db_name_lookup')
		all_int_subdbs = [x[0] for x in pop_data_cursor.fetchall()]

		self.dataListWid.clear()
		self.renameButton.setDisabled(True)
		self.deleteButton.setDisabled(True)

		list_of_all_data = []
		for sdb in all_int_subdbs:
			pop_data_cursor.execute('SELECT {} FROM {}'.format(dtype_int, sdb))
			if data_type == 'Video footage':
				ftg_tups = pop_data_cursor.fetchall()

				for tup in ftg_tups:
					temp_lst = tup[0].split('; ')

					for ftg in temp_lst:
						list_of_all_data.append(ftg)
			else:
				list_of_all_data += [x[0] for x in pop_data_cursor.fetchall()]

		list_of_all_data_deduped = list(set(list_of_all_data))
		list_of_all_data_deduped.sort(key=lambda x: x.casefold())
		if '' in list_of_all_data_deduped:
			list_of_all_data_deduped.remove('')

		for item in list_of_all_data_deduped:
			self.dataListWid.addItem(item)

		pop_data_conn.close()

	def data_clicked(self):
		if self.dataTypeListWid.currentItem().text() == 'Editor username':
			self.deleteButton.setDisabled(True)
			self.renameButton.setEnabled(True)
		else:
			self.deleteButton.setEnabled(True)
			self.renameButton.setEnabled(True)

	def del_rename_btn_pushed(self, btn):
		btn_conn = sqlite3.connect(common_vars.video_db())
		btn_cursor = btn_conn.cursor()
		all_subdbs = [v for k, v in common_vars.sub_db_lookup().items()]

		dtype_selected = self.dataTypeListWid.currentItem().text()
		data_selected = self.dataListWid.currentItem().text()
		dtype_lookup = {'Editor username': 'primary_editor_username',
						'Song artist': 'song_artist',
						'Song genre': 'song_genre',
						'Video footage': 'video_footage',
						'Video source': 'video_source'}
		dtype_int = dtype_lookup[dtype_selected]
		proceed = False

		if btn == 'rename':
			rename_window = generic_entry_window.GenericEntryWindow('rename', inp_1='', inp_2=dtype_selected.lower(),
																	inp_3=data_selected, max_item_length=100)
			if rename_window.exec_():
				new_name = rename_window.textBox.text()
				proceed = True

		else:  # Deleting data
			new_name = ''
			del_warning_window = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Delete',
													   'You are about to remove {}:<br><br><b>{}</b><br><br>'
													   '...from every entry in which it appears<br>'
													   'in AMV Tracker. This cannot be undone.<br>'
													   'Ok to proceed?'.format(dtype_selected.lower(), data_selected),
													   QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
			warning_result = del_warning_window.exec_()
			if warning_result == QtWidgets.QMessageBox.Yes:
				proceed = True

		if proceed:
			match_dict = dict()
			for sdb in all_subdbs:
				if dtype_selected == 'Video footage':
					btn_cursor.execute('SELECT video_id, {} FROM {} WHERE {} LIKE "%{}%"'
									   .format(dtype_int, sdb, dtype_int, data_selected))
				else:
					btn_cursor.execute('SELECT video_id, {} FROM {} WHERE {} = ?'
									   .format(dtype_int, sdb, dtype_int), (data_selected,))
				sdb_output = [[x[0], x[1]] for x in btn_cursor.fetchall()]
				if sdb_output:
					match_dict[sdb] = sdb_output

			for k, v in match_dict.items():
				for ind in range(len(v)):
					v_id = v[ind][0]
					if dtype_selected != 'Video footage':
						new_str = new_name

					else:
						temp_list = v[ind][1].split('; ')
						if btn == 'rename':
							upd_list = [new_name if x == data_selected else x for x in temp_list]
						else:
							temp_list.remove(data_selected)
							upd_list = temp_list
						upd_list.sort(key=lambda x: x.casefold())
						new_str = '; '.join(upd_list)

					btn_cursor.execute('UPDATE {} SET {} = ? WHERE video_id = ?'.format(k, dtype_int),
									   (new_str, v_id))
					btn_conn.commit()

			if btn == 'rename':
				msg = 'renamed to <b>{}</b>'.format(new_name)
			else:
				msg = 'removed from AMV Tracker'
			success_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Item {}d'.format(btn),
												'{} <b>{}</b> has been successfully<br>{}.'
												.format(dtype_selected, data_selected, msg))
			success_win.exec_()
			self.populate_data_listwid(dtype_selected)

		btn_conn.close()
