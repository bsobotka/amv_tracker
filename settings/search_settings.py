import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import sqlite3

from settings import settings_window
from misc_files import common_vars


class SearchSettings(QtWidgets.QWidget):
	def __init__(self):
		super(SearchSettings, self).__init__()

		grid_vert_ind = 0

		self.tag_db_conn = sqlite3.connect(common_vars.tag_db())
		self.tag_db_cursor = self.tag_db_conn.cursor()

		self.settings_conn = sqlite3.connect(common_vars.settings_db())
		self.settings_cursor = self.settings_conn.cursor()

		# Initialize search settings dict
		self.search_settings_dict = {}
		self.settings_cursor.execute('SELECT * FROM search_settings')
		for pair in self.settings_cursor.fetchall():
			self.search_settings_dict[pair[0]] = pair[1]

		# Layouts
		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.gridLayout = QtWidgets.QGridLayout()
		self.gridLayout.setAlignment(QtCore.Qt.AlignTop)

		# Widgets
		self.viewTypeLabel = QtWidgets.QLabel()
		self.viewTypeLabel.setText('Search view type:')

		self.viewTypeDrop = QtWidgets.QComboBox()
		self.viewTypeDrop.setFixedWidth(60)
		self.viewTypeDrop.addItem('List')
		self.viewTypeDrop.addItem('Detail')
		if self.search_settings_dict['view_type'] == 'L':
			self.viewTypeDrop.setCurrentIndex(0)
		else:
			self.viewTypeDrop.setCurrentIndex(1)

		self.gridLayout.addWidget(self.viewTypeLabel, grid_vert_ind, 0, 1, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.viewTypeDrop, grid_vert_ind, 1, 1, 2, alignment=QtCore.Qt.AlignLeft)
		grid_vert_ind += 1

		self.fieldDispLabel = QtWidgets.QLabel()
		self.fieldDispLabel.setText('Display these fields on search (list view only):')
		self.gridLayout.addWidget(self.fieldDispLabel, grid_vert_ind, 0, 1, 4, alignment=QtCore.Qt.AlignTop)
		grid_vert_ind += 1

		self.underlineFont = QtGui.QFont()
		self.underlineFont.setUnderline(True)
		self.fieldsAvailableLabel = QtWidgets.QLabel()
		self.fieldsAvailableLabel.setText('Available fields')
		self.fieldsAvailableLabel.setFont(self.underlineFont)
		self.gridLayout.addWidget(self.fieldsAvailableLabel, grid_vert_ind, 0, 1, 2, alignment=QtCore.Qt.AlignCenter)

		self.fieldsDisplayedLabel = QtWidgets.QLabel()
		self.fieldsDisplayedLabel.setText('Fields displayed on search')
		self.fieldsDisplayedLabel.setFont(self.underlineFont)
		self.gridLayout.addWidget(self.fieldsDisplayedLabel, grid_vert_ind, 4, alignment=QtCore.Qt.AlignCenter)
		grid_vert_ind += 1

		self.fieldSrcListWid = QtWidgets.QListWidget()
		self.fieldSrcListWid.setFixedSize(200, 300)
		self.populate_src_list_widgets()
		self.gridLayout.addWidget(self.fieldSrcListWid, grid_vert_ind, 0, 2, 2, alignment=QtCore.Qt.AlignTop)

		self.moveUpButton = QtWidgets.QPushButton(u'\u25B2')
		self.moveUpButton.setFixedWidth(15)

		self.fieldDispListWid = QtWidgets.QListWidget()
		self.fieldDispListWid.setFixedSize(200, 300)
		self.populate_disp_list_widgets()
		self.gridLayout.addWidget(self.moveUpButton, grid_vert_ind, 3, alignment=QtCore.Qt.AlignTop)
		self.gridLayout.addWidget(self.fieldDispListWid, grid_vert_ind, 4, 2, 1, alignment=QtCore.Qt.AlignTop)
		grid_vert_ind += 1

		self.moveDownButton = QtWidgets.QPushButton(u'\u25BC')
		self.moveDownButton.setFixedWidth(15)
		self.gridLayout.addWidget(self.moveDownButton, grid_vert_ind, 3, alignment=QtCore.Qt.AlignTop)
		grid_vert_ind += 1

		self.addButton = QtWidgets.QPushButton('>>')
		self.addButton.setFixedWidth(40)
		self.addButton.setToolTip('Make selected field visible\nin search list view.')
		self.removeButton = QtWidgets.QPushButton('<<')
		self.removeButton.setFixedWidth(40)
		self.removeButton.setToolTip('Remove selected field from\nsearch list view.')

		self.gridLayout.addWidget(self.addButton, grid_vert_ind, 1, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.removeButton, grid_vert_ind, 4, alignment=QtCore.Qt.AlignLeft)

		self.vLayoutMaster.addLayout(self.gridLayout)

		# Signals/slots
		self.addButton.clicked.connect(lambda: self.add_remove_button_clicked('add'))
		self.removeButton.clicked.connect(lambda: self.add_remove_button_clicked('remove'))
		self.fieldDispListWid.itemSelectionChanged.connect(self.disable_move_btns)
		self.moveUpButton.clicked.connect(lambda: self.move_field('up'))
		self.moveDownButton.clicked.connect(lambda: self.move_field('down'))
	
	def populate_src_list_widgets(self):
		self.fieldSrcListWid.clear()
		videoFieldSrcList = []

		# Get field names for source list
		self.settings_cursor.execute('SELECT field_name_display FROM search_field_lookup WHERE '
		                                   'visible_in_search_view = 0 AND in_use = 1')
		for field_name in self.settings_cursor.fetchall():
			videoFieldSrcList.append(field_name[0])

		videoFieldSrcList.sort(key=lambda x: x.lower())

		for src_field_name in videoFieldSrcList:
			self.fieldSrcListWid.addItem(src_field_name)
	
	def populate_disp_list_widgets(self):
		self.fieldDispListWid.clear()
		videoFieldDispList = []

		# Get field names for display list
		self.settings_cursor.execute('SELECT field_name_display, displ_order FROM search_field_lookup WHERE '
		                                   'visible_in_search_view = 1 AND in_use = 1 AND displ_order != ""')
		for field_name in self.settings_cursor.fetchall():
			videoFieldDispList.append(field_name)

		videoFieldDispList.sort(key=lambda x: x[1])
		videoFieldDisplListSorted = [fld[0] for fld in videoFieldDispList]

		for disp_field_name in videoFieldDisplListSorted:
			self.fieldDispListWid.addItem(disp_field_name)

	def add_remove_button_clicked(self, btn_type):
		self.settings_cursor.execute('SELECT displ_order FROM search_field_lookup WHERE displ_order != ""')
		max_displ_order = max([i[0] for i in self.settings_cursor.fetchall()])

		if btn_type == 'add' and self.fieldSrcListWid.selectedItems() != []:
			selected_field = self.fieldSrcListWid.currentItem().text()
			disp_ord = max_displ_order + 1
			self.settings_cursor.execute(
				'UPDATE search_field_lookup SET displ_order = ?, visible_in_search_view = ? '
				'WHERE field_name_display = ?', (disp_ord, 1, selected_field))

		elif btn_type == 'remove' and self.fieldDispListWid.selectedItems() != []:
			# Obtain display order of selected field to be removed from view
			selected_field = self.fieldDispListWid.currentItem().text()
			self.settings_cursor.execute('SELECT displ_order FROM search_field_lookup WHERE '
			                                   'field_name_display = ?', (selected_field,))
			sel_disp_order = self.settings_cursor.fetchall()[0][0]

			# Decrement display order for fields with a higher disp order than the field being removed from view
			self.settings_cursor.execute('SELECT field_name_internal, displ_order FROM search_field_lookup WHERE '
			                                   'displ_order > ? AND displ_order != ""', (sel_disp_order,))
			higher_fields = self.settings_cursor.fetchall()
			for field in higher_fields:
				self.settings_cursor.execute('UPDATE search_field_lookup SET displ_order = ? WHERE '
				                                   'field_name_internal = ?', (int(field[1]) - 1, field[0]))

			# Set the display order of the field being removed from view to blank
			self.settings_cursor.execute(
				'UPDATE search_field_lookup SET displ_order = ?, visible_in_search_view = ? '
				'WHERE field_name_display = ?', ('', 0, selected_field))

		else:
			pass

		self.settings_conn.commit()

		self.populate_src_list_widgets()
		self.populate_disp_list_widgets()

	def disable_move_btns(self):
		if self.fieldDispListWid.currentRow() == 0:
			self.moveUpButton.setDisabled(True)
			if self.fieldDispListWid.count() > 1:
				self.moveDownButton.setEnabled(True)
		elif self.fieldDispListWid.currentRow() == self.fieldDispListWid.count() - 1 and self.fieldDispListWid.count() > 1:
			self.moveDownButton.setDisabled(True)
			if self.fieldDispListWid.count() > 1:
				self.moveUpButton.setEnabled(True)
		else:
			self.moveUpButton.setEnabled(True)
			self.moveDownButton.setEnabled(True)

	def move_field(self, dir):
		if self.fieldDispListWid.selectedItems() != []:
			sel_field = self.fieldDispListWid.currentItem().text()
			self.settings_cursor.execute('SELECT displ_order FROM search_field_lookup WHERE field_name_display = ?',
			                                   (sel_field,))
			sel_displ_order = self.settings_cursor.fetchall()[0][0]

			if dir == 'up':
				new_ord = sel_displ_order - 1
			else:
				new_ord = sel_displ_order + 1

			self.settings_cursor.execute('SELECT field_name_internal FROM search_field_lookup WHERE displ_order = ?',
			                                   (new_ord,))
			field_to_upd = self.settings_cursor.fetchall()[0][0]

			self.settings_cursor.execute('UPDATE search_field_lookup SET displ_order = ? WHERE field_name_display = ?',
			                                   (new_ord, sel_field))
			self.settings_cursor.execute('UPDATE search_field_lookup SET displ_order = ? WHERE field_name_internal = ?',
			                                   (sel_displ_order, field_to_upd))


			self.settings_conn.commit()

			self.populate_disp_list_widgets()
			self.fieldDispListWid.setCurrentRow(new_ord - 1)

		else:
			pass
