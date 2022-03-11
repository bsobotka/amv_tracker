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
		self.dataTypeListWid.setFixedSize(100, 140)
		self.dataTypes = ['Editor username', 'Song artist', 'Song genre', 'Video footage']
		for dType in self.dataTypes:
			self.dataTypeListWid.addItem(dType)
		self.gridLayoutMaster.addWidget(self.dataTypeListWid, grid_vert_ind, 0, alignment=QtCore.Qt.AlignTop)

		self.dataListWid = QtWidgets.QListWidget()
		self.dataListWid.setFixedSize(200, 400)
		self.gridLayoutMaster.addWidget(self.dataListWid, grid_vert_ind, 1, 1, 2, alignment=QtCore.Qt.AlignTop)
		grid_vert_ind += 1

		# Row 2
		self.renameButton = QtWidgets.QPushButton('Rename')
		self.renameButton.setFixedWidth(97)
		self.renameButton.setDisabled(True)
		self.gridLayoutMaster.addWidget(self.renameButton, grid_vert_ind, 1, alignment=QtCore.Qt.AlignTop)

		self.deleteButton = QtWidgets.QPushButton('Delete')
		self.deleteButton.setFixedWidth(97)
		self.deleteButton.setDisabled(True)
		self.gridLayoutMaster.addWidget(self.deleteButton, grid_vert_ind, 2, alignment=QtCore.Qt.AlignTop)
		grid_vert_ind += 1

		# Signals / slots
		self.dataTypeListWid.itemClicked.connect(lambda: self.populate_data_listwid(self.dataTypeListWid.currentItem()
																					.text()))
		self.renameButton.clicked.connect(lambda: self.rename_btn_pushed(self.dataListWid.currentItem().text()))
		self.deleteButton.clicked.connect(lambda: self.delete_btn_pushed(self.dataListWid.currentItem().text()))

	def populate_data_listwid(self, data_type):
		pop_data_conn = sqlite3.connect(common_vars.video_db())
		pop_data_cursor = pop_data_conn.cursor()

		dtype_lookup = {'Editor username': 'primary_editor_username',
						'Song artist': 'song_artist',
						'Song genre': 'song_genre',
						'Video footage': 'video_footage'}
		dtype_int = dtype_lookup[data_type]

		pop_data_cursor.execute('SELECT table_name FROM db_name_lookup')
		all_int_subdbs = [x[0] for x in pop_data_cursor.fetchall()]

		self.dataListWid.clear()
		self.renameButton.setEnabled(True)

		if data_type != 'Editor username':
			self.deleteButton.setEnabled(True)
		else:
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

	def rename_btn_pushed(self, txt):
		pass

	def delete_btn_pushed(self, txt):
		pass


