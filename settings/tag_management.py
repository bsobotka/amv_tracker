import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import sqlite3

from settings import settings_notifications, move_tag_window
from misc_files import common_vars, generic_entry_window


class TagManagement(QtWidgets.QWidget):
	# TODO: Refresh data on tab click (like on entry settings)
	def __init__(self):
		super(TagManagement, self).__init__()

		# Connection to SQLite databases
		tm_settings_conn = sqlite3.connect(common_vars.settings_db())
		tm_settings_cursor = tm_settings_conn.cursor()

		tag_lookup = tm_settings_cursor.fetchall()
		self.tag_list_names = [tags[1] for tags in tag_lookup]

		## Tag management ##
		# Labels
		self.editTagsGridLayout = QtWidgets.QGridLayout()
		self.editTagsGridLayout.setAlignment(QtCore.Qt.AlignTop)
		self.tagEditHeaderFont = QtGui.QFont()
		self.tagEditHeaderFont.setBold(True)
		self.tagEditHeaderFont.setUnderline(True)
		self.tagEditHeaderFont.setPixelSize(14)

		self.tagTypeLabel = QtWidgets.QLabel()
		self.tagTypeLabel.setText('Tag type')
		self.tagTypeLabel.setFont(self.tagEditHeaderFont)

		self.tagsLabel = QtWidgets.QLabel()
		self.tagsLabel.setText('Tags')
		self.tagsLabel.setFont(self.tagEditHeaderFont)

		self.tagDescLabel = QtWidgets.QLabel()
		self.tagDescLabel.setText('Tag description')
		self.tagDescLabel.setFont(self.tagEditHeaderFont)

		self.editTagsGridLayout.addWidget(self.tagTypeLabel, 0, 0, alignment=QtCore.Qt.AlignCenter)
		self.editTagsGridLayout.addWidget(self.tagsLabel, 0, 1, 1, 3, alignment=QtCore.Qt.AlignCenter)
		self.editTagsGridLayout.addWidget(self.tagDescLabel, 0, 5, alignment=QtCore.Qt.AlignCenter)

		self.tagTypeListWid = QtWidgets.QListWidget()
		self.tagTypeListWid.setFixedSize(100, 140)

		self.tagListWid = QtWidgets.QListWidget()
		self.tagListWid.setFixedSize(200, 300)

		self.tagDescEditor = QtWidgets.QTextEdit()
		self.tagDescEditor.setFixedSize(200, 300)

		self.editTagsGridLayout.addWidget(self.tagTypeListWid, 1, 0, alignment=QtCore.Qt.AlignTop)
		self.editTagsGridLayout.addWidget(self.tagListWid, 1, 1, 2, 4, alignment=QtCore.Qt.AlignTop)
		self.editTagsGridLayout.addWidget(self.tagDescEditor, 1, 5, 4, 1, alignment=QtCore.Qt.AlignTop)

		self.tagListRenameButton = QtWidgets.QPushButton('Rename')
		self.tagListRenameButton.setFixedWidth(95)
		self.tagListRenameButton.setDisabled(True)
		self.editTagsGridLayout.addWidget(self.tagListRenameButton, 2, 0, alignment=QtCore.Qt.AlignTop)

		self.addTagButton = QtWidgets.QPushButton('Add')
		self.addTagButton.setFixedWidth(95)
		self.addTagButton.setDisabled(True)
		self.moveTagButton = QtWidgets.QPushButton('Move')
		self.moveTagButton.setFixedWidth(95)
		self.moveTagButton.setDisabled(True)
		self.removeTagButton = QtWidgets.QPushButton('Remove')
		self.removeTagButton.setFixedWidth(95)
		self.removeTagButton.setDisabled(True)
		self.renameTagButton = QtWidgets.QPushButton('Rename')
		self.renameTagButton.setFixedWidth(95)
		self.renameTagButton.setDisabled(True)
		self.reposTagUpButton = QtWidgets.QPushButton(u'\u25B2')
		self.reposTagUpButton.setFixedWidth(15)
		self.reposTagUpButton.setDisabled(True)
		self.sortButton = QtWidgets.QPushButton('Sort alphabetically')
		self.sortButton.setFixedWidth(160)
		self.sortButton.setDisabled(True)
		self.reposTagDownButton = QtWidgets.QPushButton(u'\u25BC')
		self.reposTagDownButton.setFixedWidth(15)
		self.reposTagDownButton.setDisabled(True)
		self.editTagsGridLayout.addWidget(self.reposTagUpButton, 3, 1)
		self.editTagsGridLayout.addWidget(self.sortButton, 3, 2, 1, 2)
		self.editTagsGridLayout.addWidget(self.reposTagDownButton, 3, 4)
		self.editTagsGridLayout.addWidget(self.addTagButton, 4, 1, 1, 2)
		self.editTagsGridLayout.addWidget(self.removeTagButton, 4, 3, 1, 2, alignment=QtCore.Qt.AlignRight)
		self.editTagsGridLayout.addWidget(self.moveTagButton, 5, 1, 1, 2)
		self.editTagsGridLayout.addWidget(self.renameTagButton, 5, 3, 1, 2, alignment=QtCore.Qt.AlignRight)

		self.saveDescButton = QtWidgets.QPushButton('Save desc.')
		self.saveDescButton.setFixedWidth(95)
		self.saveDescButton.setDisabled(True)
		self.editTagsGridLayout.addWidget(self.saveDescButton, 3, 5, alignment=QtCore.Qt.AlignRight)

		tm_settings_conn.close()

		# List population
		self.populate_tag_widgets(self.tagTypeListWid)

		# Signals / slots
		self.tagListRenameButton.clicked.connect(lambda: self.rename_tag_buttons('tag type',
		                                                                         self.tagTypeListWid.currentItem().text()))
		self.tagTypeListWid.itemClicked.connect(lambda: self.populate_tag_widgets(self.tagListWid))
		self.tagTypeListWid.itemClicked.connect(lambda: self.enable_tag_buttons(self.tagTypeListWid))
		self.tagListWid.itemClicked.connect(lambda: self.populate_tag_widgets(self.tagDescEditor))
		self.tagListWid.itemClicked.connect(lambda: self.enable_tag_buttons(self.tagListWid))
		self.addTagButton.clicked.connect(self.add_new_tag)
		self.renameTagButton.clicked.connect(lambda: self.rename_tag_buttons('tag',
		                                                                     self.tagListWid.currentItem().text()))
		self.removeTagButton.clicked.connect(self.remove_tag)
		self.moveTagButton.clicked.connect(self.move_tag)
		self.reposTagUpButton.clicked.connect(lambda: self.repos_tag(1))
		self.reposTagDownButton.clicked.connect(lambda: self.repos_tag(-1))
		self.sortButton.clicked.connect(self.sort_tags_alpha)
		self.tagDescEditor.undoAvailable.connect(self.typing_in_desc_editor)
		self.saveDescButton.clicked.connect(self.save_desc_pushed)

	def enable_tag_buttons(self, widget, tab_change=False):
		if widget == self.tagTypeListWid:
			self.removeTagButton.setDisabled(True)
			self.moveTagButton.setDisabled(True)
			self.renameTagButton.setDisabled(True)
			self.saveDescButton.setDisabled(True)
			self.reposTagUpButton.setDisabled(True)
			self.reposTagDownButton.setDisabled(True)

			if tab_change:
				self.tagListRenameButton.setDisabled(True)
				self.addTagButton.setDisabled(True)
				self.sortButton.setDisabled(True)
				self.tagListWid.clear()
				self.tagDescEditor.clear()
			else:
				self.tagListRenameButton.setEnabled(True)
				self.addTagButton.setEnabled(True)
				if self.tagListWid.count() > 1:
					self.sortButton.setEnabled(True)
				else:
					self.sortButton.setDisabled(True)

		elif widget == self.tagListWid:
			self.removeTagButton.setEnabled(True)
			self.moveTagButton.setEnabled(True)
			self.renameTagButton.setEnabled(True)
			self.reposTagUpButton.setEnabled(True)
			self.reposTagDownButton.setEnabled(True)
			if self.tagListWid.count() > 1:
				self.sortButton.setEnabled(True)
			else:
				self.sortButton.setDisabled(True)

	def populate_tag_widgets(self, widget):
		widget.clear()
		tag_type_lookup = common_vars.tag_table_lookup()

		pop_tag_conn = sqlite3.connect(common_vars.video_db())

		if widget == self.tagTypeListWid:
			for tag_type in tag_type_lookup.items():
				self.tagTypeListWid.addItem(tag_type[0])

		elif widget == self.tagListWid:
			tag_list = [tag for tag in pop_tag_conn.execute(
				'SELECT * FROM {}'.format(tag_type_lookup[self.tagTypeListWid.currentItem().text()]))]
			tag_list.sort(key=lambda x: x[2])
			for tag in tag_list:
				self.tagListWid.addItem(tag[0])

			self.tagDescEditor.clear()

		elif widget == self.tagDescEditor:
			tag_name = self.tagListWid.currentItem().text()
			desc = common_vars.tag_desc_lookup(self.tagTypeListWid.currentItem().text())[tag_name]
			self.tagDescEditor.setText(desc)
			self.saveDescButton.setDisabled(True)

		pop_tag_conn.close()

	def rename_tag_buttons(self, label, item_to_rename):
		# TODO: Rename tags throughout database -- all entries with tag must be updated
		# TODO: Rename tags in disable_tags column in corresponding tag database
		rename_tag_conn = sqlite3.connect(common_vars.video_db())
		rename_tag_cursor = rename_tag_conn.cursor()
		user_friendly_tag_table = self.tagTypeListWid.currentItem().text()

		tag_type_list = [key.casefold() for key, val in common_vars.tag_table_lookup().items()]

		if label == 'tag type':
			tag_table = 'tags_lookup'
			tag_field_name = 'user_field_name'
			lookup_field_name = 'user_field_name'
		else:
			tag_table = common_vars.tag_table_lookup()[user_friendly_tag_table]
			tag_field_name = 'tag_name'
			lookup_field_name = 'tag_name'

		rename_window = generic_entry_window.GenericEntryWindow('rename', inp_1=label, inp_2=label,
		                                                        inp_3=item_to_rename)
		if rename_window.exec_():
			new_name = rename_window.textBox.text()
			if new_name.casefold() in tag_type_list:
				dupe_tag_type = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error', 'This tag group already '
				                                                                              'exists. Please choose\n'
				                                                                              'another name.')
				dupe_tag_type.exec_()
			else:
				rename_tag_cursor.execute('UPDATE {} SET {} = ? WHERE {} = ?'.format(tag_table, tag_field_name,
				                                                                        lookup_field_name),
				                             (new_name, item_to_rename))
				rename_tag_conn.commit()

		if label == 'tag type':
			self.populate_tag_widgets(self.tagTypeListWid)
			self.tagListWid.clear()
		else:
			self.populate_tag_widgets(self.tagListWid)

		rename_tag_conn.close()

		self.tagListRenameButton.setDisabled(True)
		self.addTagButton.setDisabled(True)
		self.renameTagButton.setDisabled(True)
		self.removeTagButton.setDisabled(True)
		self.moveTagButton.setDisabled(True)
		self.reposTagUpButton.setDisabled(True)
		self.sortButton.setDisabled(True)
		self.reposTagDownButton.setDisabled(True)

	def add_new_tag(self):
		ant_settings_conn = sqlite3.connect(common_vars.settings_db())
		ant_settings_cursor = ant_settings_conn.cursor()

		ant_tags_conn = sqlite3.connect(common_vars.video_db())
		ant_tags_cursor = ant_tags_conn.cursor()

		tag_table = common_vars.tag_table_lookup()[self.tagTypeListWid.currentItem().text()]
		existing_tags = [tag[0] for tag in ant_tags_conn.execute('SELECT * FROM {}'.format(tag_table))]
		sort_order = [so for so in ant_tags_conn.execute('SELECT sort_order FROM {}'.format(tag_table))]

		if sort_order == []:
			max_sort_order_number = 0
		else:
			max_sort_order_number = max(sort_order)[0]

		add_tag_window = generic_entry_window.GenericEntryWindow('new', inp_1='tag',
		                                                         dupe_check_list=existing_tags)
		if add_tag_window.exec_():
			new_tag = add_tag_window.textBox.text()
			ant_tags_cursor.execute('INSERT INTO {} (tag_name, tag_desc, sort_order) VALUES (?, ?, ?)'.format(tag_table),
			                       (new_tag, '', max_sort_order_number + 1))
			ant_tags_cursor.execute('UPDATE tags_lookup SET in_use = 1 WHERE internal_field_name = ?', (tag_table,))

			entry_field_tag_name = 'Tags - {}'.format(self.tagTypeListWid.currentItem().text())
			ant_settings_cursor.execute('UPDATE search_field_lookup SET field_name_display = ?, in_use = ? WHERE '
			                                   'field_name_internal = ?', (entry_field_tag_name, 1, tag_table))

			ant_tags_conn.commit()
			ant_settings_conn.commit()

		self.populate_tag_widgets(self.tagListWid)
		self.enable_tag_buttons(self.tagListWid)
		self.renameTagButton.setDisabled(True)
		self.removeTagButton.setDisabled(True)
		self.moveTagButton.setDisabled(True)
		self.reposTagUpButton.setDisabled(True)
		self.reposTagDownButton.setDisabled(True)

		ant_tags_conn.close()
		ant_settings_conn.close()

	def remove_tag(self):
		# TODO: Write logic to remove tag from database entries
		rt_settings_conn = sqlite3.connect(common_vars.settings_db())
		rt_settings_cursor = rt_settings_conn.cursor()

		rt_tags_conn = sqlite3.connect(common_vars.video_db())

		tag_table = common_vars.tag_table_lookup()[self.tagTypeListWid.currentItem().text()]
		msgBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Warning',
		                               'Tag [{}] will be removed from the tag list, and from all\n'
		                               'video entries which have it. This is not reversible. Ok to\n'
		                               'proceed?'.format(self.tagListWid.currentItem().text()),
		                               QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
		result = msgBox.exec_()

		if result == QtWidgets.QMessageBox.Yes:
			rt_tags_conn.execute('DELETE FROM {} WHERE tag_name = ?'.format(tag_table),
			                      (self.tagListWid.currentItem().text(),))
			is_empty = rt_tags_conn.execute('SELECT COUNT(*) FROM {}'.format(tag_table))

			if is_empty.fetchall()[0][0] == 0:
				entry_field_tag_name = 'Tags - Not in use'
				rt_tags_conn.execute('UPDATE tags_lookup SET in_use = 0 WHERE internal_field_name = ?', (tag_table,))
				rt_settings_cursor.execute(
					'UPDATE search_field_lookup SET field_name_display = ?, in_use = ? WHERE '
					'field_name_internal = ?', (entry_field_tag_name, 0, tag_table))

			rt_settings_conn.commit()
			rt_tags_conn.commit()

			self.populate_tag_widgets(self.tagListWid)
			self.enable_tag_buttons(self.tagListWid)
			self.renameTagButton.setDisabled(True)
			self.removeTagButton.setDisabled(True)
			self.moveTagButton.setDisabled(True)
			self.reposTagUpButton.setDisabled(True)
			self.reposTagDownButton.setDisabled(True)
		else:
			msgBox.close()

		rt_settings_conn.close()
		rt_tags_conn.close()

	def move_tag(self):
		"""
		Moves tag from one tag group to another
		"""
		move_tm_tag_conn = sqlite3.connect(common_vars.video_db())
		move_tm_tag_cursor = move_tm_tag_conn.cursor()

		origin_table = common_vars.tag_table_lookup()[self.tagTypeListWid.currentItem().text()]
		origin_table_friendly = self.tagTypeListWid.currentItem().text()
		tag_to_move = self.tagListWid.currentItem().text()
		mod_tag_type_table = [typ[0] for typ in move_tm_tag_conn.execute('SELECT user_field_name FROM tags_lookup')]
		mod_tag_type_table.remove(origin_table_friendly)

		move_window = move_tag_window.MoveTagWindow(tag_to_move, origin_table_friendly, mod_tag_type_table)
		if move_window.exec_():
			dest_table = common_vars.tag_table_lookup()[move_window.tableDropdown.currentText()]
			dest_sort_order_list = [so[0] for so in
			                        move_tm_tag_conn.execute('SELECT sort_order FROM {}'.format(dest_table))]
			if dest_sort_order_list == []:
				dest_max_sort_order = 1
			else:
				dest_max_sort_order = max(dest_sort_order_list) + 1


			move_tm_tag_cursor.execute('UPDATE {} SET sort_order = ? WHERE tag_name = ?'.format(origin_table),
			                        (dest_max_sort_order, tag_to_move))
			move_tm_tag_cursor.execute('SELECT * FROM {} WHERE tag_name = ?'.format(origin_table), (tag_to_move,))
			transfer = move_tm_tag_cursor.fetchall()[0]
			move_tm_tag_cursor.execute(
				'INSERT INTO {} (tag_name, tag_desc, sort_order) VALUES (?, ?, ?)'.format(dest_table),
				transfer)
			move_tm_tag_cursor.execute('DELETE FROM {} WHERE tag_name = ?'.format(origin_table), (tag_to_move,))

			move_tm_tag_cursor.execute('SELECT tag_name, sort_order FROM {}'.format(origin_table))
			origin_mod_tags = move_tm_tag_cursor.fetchall()
			origin_mod_tags.sort(key=lambda x: x[1])
			for new_so in range(1, len(origin_mod_tags) + 1):
				move_tm_tag_cursor.execute('UPDATE {} SET sort_order = ? WHERE tag_name = ?'.format(origin_table),
				                        (new_so, origin_mod_tags[new_so - 1][0]))

			move_tm_tag_conn.commit()
			move_tm_tag_conn.close()

			# Reset listviews
			self.populate_tag_widgets(self.tagListWid)
			self.renameTagButton.setDisabled(True)
			self.removeTagButton.setDisabled(True)
			self.moveTagButton.setDisabled(True)
			self.reposTagUpButton.setDisabled(True)
			self.reposTagDownButton.setDisabled(True)

	def repos_tag(self, direction):
		"""
		Changes sort_order field in selected tag to be one greater or one less than current value.
		:param direction: 1 = moving up, -1 = moving down
		"""
		repos_conn = sqlite3.connect(common_vars.video_db())
		repos_cursor = repos_conn.cursor()

		selected_tag = self.tagListWid.currentItem().text()
		tag_table_friendly = self.tagTypeListWid.currentItem().text()
		tag_table_internal = common_vars.tag_table_lookup()[tag_table_friendly]
		repos_cursor.execute('SELECT sort_order FROM {} WHERE tag_name = ?'
		                     .format(tag_table_internal), (selected_tag,))
		selected_tag_pos = repos_cursor.fetchone()[0]
		max_sort_order = max([so for so in repos_conn.execute('SELECT sort_order FROM {}'.format(tag_table_internal))])[0]

		if (selected_tag_pos == max_sort_order and direction == -1) or (selected_tag_pos == 1 and direction == 1):
			warning_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Error',
			                                    'The selected tag cannot be moved in that direction.')
			warning_box.exec_()

		else:
			# Extract tag whose slot selected tag is moving to
			repos_cursor.execute('SELECT * FROM {} WHERE sort_order = ?'.format(tag_table_internal),
			                     (selected_tag_pos - direction,))
			extracted_tag = repos_cursor.fetchone()

			# Delete that tag from database
			repos_cursor.execute('DELETE FROM {} WHERE tag_name = ?'.format(tag_table_internal), (extracted_tag[0],))

			# Update sort_order value of selected tag
			repos_cursor.execute('UPDATE {} SET sort_order = ? WHERE sort_order = ?'.format(tag_table_internal),
			                     (selected_tag_pos - direction, selected_tag_pos))

			# Re-insert tag whose slot selected tag moved into back into database with updated sort_order value
			repos_cursor.execute(
				'INSERT INTO {} (tag_name, tag_desc, sort_order) VALUES (?, ?, ?)'.format(tag_table_internal),
				(extracted_tag[0], extracted_tag[1], selected_tag_pos))

			repos_conn.commit()
			repos_conn.close()

			self.populate_tag_widgets(self.tagListWid)

			if direction == -1:
				self.tagListWid.setCurrentRow(selected_tag_pos)
			else:
				self.tagListWid.setCurrentRow(selected_tag_pos - 2)

			self.populate_tag_widgets(self.tagDescEditor)

	def sort_tags_alpha(self):
		sort_tag_conn = sqlite3.connect(common_vars.video_db())
		sort_tag_cursor = sort_tag_conn.cursor()

		tag_table_friendly = self.tagTypeListWid.currentItem().text()
		tag_table_internal = common_vars.tag_table_lookup()[tag_table_friendly]
		sort_order_list = [so[0] for so in sort_tag_conn.execute('SELECT sort_order FROM {}'.format(tag_table_internal))]
		max_sort_order = max(sort_order_list)
		alpha_tag_list = [tag[0] for tag in sort_tag_conn.execute('SELECT tag_name FROM {}'.format(tag_table_internal))]
		alpha_tag_list.sort(key=lambda x: x.lower())

		for new_so in range(1, max_sort_order + 1):
			sort_tag_cursor.execute('UPDATE {} SET sort_order = ? WHERE tag_name = ?'.format(tag_table_internal),
			                          (new_so, alpha_tag_list[new_so - 1]))


		sort_tag_conn.commit()
		sort_tag_conn.close()
		self.populate_tag_widgets(self.tagListWid)

		self.renameTagButton.setDisabled(True)
		self.removeTagButton.setDisabled(True)
		self.moveTagButton.setDisabled(True)
		self.reposTagUpButton.setDisabled(True)
		self.reposTagDownButton.setDisabled(True)

	def typing_in_desc_editor(self):
		self.saveDescButton.setEnabled(True)

	def save_desc_pushed(self):
		save_desc_tag_conn = sqlite3.connect(common_vars.video_db())
		save_desc_cursor = save_desc_tag_conn.cursor()

		tag_table = common_vars.tag_table_lookup()[self.tagTypeListWid.currentItem().text()]
		desc_text = self.tagDescEditor.toPlainText()
		tag_name = self.tagListWid.currentItem().text()

		save_desc_cursor.execute('UPDATE {} SET tag_desc = ? WHERE tag_name = ?'.format(tag_table),
		                         (desc_text, tag_name))

		save_desc_tag_conn.commit()
		save_desc_tag_conn.close()

		settings_notifications.SettingsNotificationWindow('desc updated', inp_str1=tag_name)
