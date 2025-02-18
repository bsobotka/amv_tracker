import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import sqlite3

from misc_files import common_vars, generic_entry_window
from settings import custom_tag_logic_window, move_tag_window, mut_excl_tags_window, settings_notifications


class TagManagement(QtWidgets.QWidget):
    def __init__(self):
        super(TagManagement, self).__init__()

        ## Tag management ##
        self.tagsVLayoutMaster = QtWidgets.QVBoxLayout()
        self.vLayoutT_L = QtWidgets.QVBoxLayout()
        self.vLayoutT_L.setAlignment(QtCore.Qt.AlignTop)
        self.vLayoutT_C = QtWidgets.QVBoxLayout()
        self.vLayoutT_C.setAlignment(QtCore.Qt.AlignTop)
        self.vLayoutT_R = QtWidgets.QVBoxLayout()
        self.vLayoutT_R.setAlignment(QtCore.Qt.AlignTop)
        self.gridLayoutT_C = QtWidgets.QGridLayout()
        self.hLayoutT = QtWidgets.QHBoxLayout()
        self.vLayoutBottom = QtWidgets.QVBoxLayout()
        self.vLayoutBottom.setAlignment(QtCore.Qt.AlignTop)
        
        # Font
        self.tagEditHeaderFont = QtGui.QFont()
        self.tagEditHeaderFont.setBold(True)
        self.tagEditHeaderFont.setUnderline(True)
        self.tagEditHeaderFont.setPixelSize(14)

        # Tag groups
        self.tagGroupLabel = QtWidgets.QLabel()
        self.tagGroupLabel.setText('Tag groups')
        self.tagGroupLabel.setFont(self.tagEditHeaderFont)

        self.tagGroupListWid = QtWidgets.QListWidget()
        self.tagGroupListWid.setFixedSize(100, 140)

        self.tagGroupRenameButton = QtWidgets.QPushButton('Rename')
        self.tagGroupRenameButton.setFixedWidth(95)
        self.tagGroupRenameButton.setDisabled(True)

        # Tags
        self.tagsLabel = QtWidgets.QLabel()
        self.tagsLabel.setText('Tags')
        self.tagsLabel.setFont(self.tagEditHeaderFont)

        self.tagListWid = QtWidgets.QListWidget()
        self.tagListWid.setFixedSize(200, 450)

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

        # QFrame
        self.frame1 = QtWidgets.QFrame()
        self.frame1.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Sunken)
        self.frame1.setLineWidth(0)
        self.frame1.setMidLineWidth(1)
        
        # Other tag buttons
        self.setMutExclTags = QtWidgets.QPushButton('Set mutually exclusive tags')
        self.setMutExclTags.setFixedWidth(160)
        self.setMutExclTags.setToolTip('Identify tags within a single tag group to be "mutually exclusive" to help\n'
                                       'make tag selection consistent as you enter videos into your database.')

        self.customTagLogic = QtWidgets.QPushButton('Custom tag logic')
        self.customTagLogic.setFixedWidth(160)
        self.customTagLogic.setToolTip('Help automate tagging by creating your own logic, which will auto-check tags\n'
                                       'if conditions you specify are met elsewhere in the video entry fields.')

        # Tag description
        self.tagDescLabel = QtWidgets.QLabel()
        self.tagDescLabel.setText('Tag description')
        self.tagDescLabel.setFont(self.tagEditHeaderFont)

        self.tagDescEditor = QtWidgets.QTextEdit()
        self.tagDescEditor.setFixedSize(200, 300)
        self.tagDescEditor.setDisabled(True)

        self.saveDescButton = QtWidgets.QPushButton('Save desc.')
        self.saveDescButton.setFixedWidth(95)
        self.saveDescButton.setDisabled(True)
        
        # Layouts
        self.vLayoutT_L.addWidget(self.tagGroupLabel, alignment=QtCore.Qt.AlignCenter)
        self.vLayoutT_L.addWidget(self.tagGroupListWid, alignment=QtCore.Qt.AlignCenter)
        self.vLayoutT_L.addWidget(self.tagGroupRenameButton, alignment=QtCore.Qt.AlignCenter)
        
        self.vLayoutT_C.addWidget(self.tagsLabel, alignment=QtCore.Qt.AlignCenter)
        self.vLayoutT_C.addWidget(self.tagListWid, alignment=QtCore.Qt.AlignCenter)
        
        self.gridLayoutT_C.addWidget(self.reposTagUpButton, 0, 0)
        self.gridLayoutT_C.addWidget(self.sortButton, 0, 1, 1, 2)
        self.gridLayoutT_C.addWidget(self.reposTagDownButton, 0, 3)
        self.gridLayoutT_C.addWidget(self.addTagButton, 1, 0, 1, 2)
        self.gridLayoutT_C.addWidget(self.removeTagButton, 1, 2, 1, 2)
        self.gridLayoutT_C.addWidget(self.moveTagButton, 2, 0, 1, 2)
        self.gridLayoutT_C.addWidget(self.renameTagButton, 2, 2, 1, 2)
        self.vLayoutT_C.addLayout(self.gridLayoutT_C)
        
        self.vLayoutT_R.addWidget(self.tagDescLabel, alignment=QtCore.Qt.AlignCenter)
        self.vLayoutT_R.addWidget(self.tagDescEditor, alignment=QtCore.Qt.AlignCenter)
        self.vLayoutT_R.addWidget(self.saveDescButton, alignment=QtCore.Qt.AlignRight)
        
        self.hLayoutT.addLayout(self.vLayoutT_L)
        self.hLayoutT.addLayout(self.vLayoutT_C)
        self.hLayoutT.addSpacing(7)
        self.hLayoutT.addLayout(self.vLayoutT_R)
        
        self.vLayoutBottom.addWidget(self.setMutExclTags, alignment=QtCore.Qt.AlignLeft)
        self.vLayoutBottom.addWidget(self.customTagLogic, alignment=QtCore.Qt.AlignLeft)
        
        self.tagsVLayoutMaster.addLayout(self.hLayoutT)
        self.tagsVLayoutMaster.addSpacing(10)
        self.tagsVLayoutMaster.addWidget(self.frame1)
        self.tagsVLayoutMaster.addSpacing(10)
        self.tagsVLayoutMaster.addLayout(self.vLayoutBottom)

        # List population
        self.populate_tag_widgets(self.tagGroupListWid)

        # Signals / slots
        self.tagGroupRenameButton.clicked.connect(lambda: self.rename_tag_buttons('tag type',
                                                                                 self.tagGroupListWid.currentItem().text()))
        self.tagGroupListWid.itemClicked.connect(lambda: self.populate_tag_widgets(self.tagListWid))
        self.tagGroupListWid.itemClicked.connect(lambda: self.enable_tag_buttons(self.tagGroupListWid))
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

        self.setMutExclTags.clicked.connect(self.set_mut_excl_tags_clicked)
        self.customTagLogic.clicked.connect(self.custom_tag_logic_clicked)

    def enable_tag_buttons(self, widget, tab_change=False):
        if widget == self.tagGroupListWid:
            self.removeTagButton.setDisabled(True)
            self.moveTagButton.setDisabled(True)
            self.renameTagButton.setDisabled(True)
            self.tagDescEditor.setDisabled(True)
            self.saveDescButton.setDisabled(True)
            self.reposTagUpButton.setDisabled(True)
            self.reposTagDownButton.setDisabled(True)

            if tab_change:
                self.tagGroupRenameButton.setDisabled(True)
                self.addTagButton.setDisabled(True)
                self.sortButton.setDisabled(True)
                self.tagListWid.clear()
                self.tagDescEditor.clear()
            else:
                self.tagGroupRenameButton.setEnabled(True)
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
            self.tagDescEditor.setEnabled(True)
            if self.tagListWid.count() > 1:
                self.sortButton.setEnabled(True)
            else:
                self.sortButton.setDisabled(True)

    def populate_tag_widgets(self, widget):
        widget.clear()
        tag_type_lookup = common_vars.tag_table_lookup()

        pop_tag_conn = sqlite3.connect(common_vars.video_db())

        if widget == self.tagGroupListWid:
            for tag_type in tag_type_lookup.items():
                self.tagGroupListWid.addItem(tag_type[0])

        elif widget == self.tagListWid:
            tag_list = [tag for tag in pop_tag_conn.execute(
                'SELECT * FROM {}'.format(tag_type_lookup[self.tagGroupListWid.currentItem().text()]))]
            tag_list.sort(key=lambda x: x[2])
            for tag in tag_list:
                self.tagListWid.addItem(tag[0])

            self.tagDescEditor.clear()

        elif widget == self.tagDescEditor:
            tag_name = self.tagListWid.currentItem().text()
            desc = common_vars.tag_desc_lookup(self.tagGroupListWid.currentItem().text())[tag_name]
            self.tagDescEditor.setText(desc)
            self.saveDescButton.setDisabled(True)

        pop_tag_conn.close()

    def rename_tag_buttons(self, label, item_to_rename):
        rename_tag_settings_conn = sqlite3.connect(common_vars.settings_db())
        rename_tag_settings_cursor = rename_tag_settings_conn.cursor()
        rename_tag_conn = sqlite3.connect(common_vars.video_db())
        rename_tag_cursor = rename_tag_conn.cursor()

        user_friendly_tag_table = self.tagGroupListWid.currentItem().text()
        internal_tag_table = common_vars.tag_table_lookup()[user_friendly_tag_table]
        subdb_dict = common_vars.sub_db_lookup()

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
                    rename_tag_settings_cursor.execute('UPDATE search_field_lookup SET field_name_display = ? WHERE '
                                                       'field_name_internal = ?', ('Tags - ' + new_name,
                                                                                   internal_tag_table))
                    rename_tag_settings_conn.commit()

                # Rename tags throughout video sub-dbs
                for subdb_user, subdb_int in subdb_dict.items():
                    rename_tag_cursor.execute('SELECT video_id, {} FROM {} WHERE {} LIKE "%"||?||"%"'
                                              .format(internal_tag_table, subdb_int, internal_tag_table),
                                              (item_to_rename,))
                    curr_tags_dict = {x[0]: x[1].split('; ') for x in rename_tag_cursor.fetchall() if x[1] is not None}
                    curr_tags_dict_new = {vidid: '; '.join(sorted([new_name.lower() if t == item_to_rename.lower() else
                                                                   t for t in taglist], key=lambda x: x.lower()))
                                          for vidid, taglist in curr_tags_dict.items()}
                    for v_id, tags in curr_tags_dict_new.items():
                        rename_tag_cursor.execute('UPDATE {} SET {} = ? WHERE video_id = ?'
                                                  .format(subdb_int, internal_tag_table), (curr_tags_dict_new[v_id],
                                                                                           v_id))

                # Rename disable_tags in tag tables
                rename_tag_cursor.execute('SELECT tag_name, disable_tags FROM {} WHERE disable_tags LIKE "%"||?||"%"'
                                          .format(internal_tag_table), (item_to_rename,))
                dis_tags_dict = {x[0]: x[1].split('; ') for x in rename_tag_cursor.fetchall() if x[1] is not None}
                dis_tags_dict_new = {tag_name: '; '.join(sorted([new_name if t.lower() == item_to_rename.lower() else
                                                                 t for t in dis_tags], key=lambda x: x.lower()))
                                     for tag_name, dis_tags in dis_tags_dict.items()}
                for tag, d_tags in dis_tags_dict_new.items():
                    rename_tag_cursor.execute('UPDATE {} SET disable_tags = ? WHERE tag_name = ?'
                                              .format(internal_tag_table), (d_tags, tag))

                rename_tag_conn.commit()

                # Rename tags in custom tag logic
                rename_tag_cursor.execute('SELECT ctlr_id, {} FROM custom_tag_logic WHERE {} LIKE "%"||?||"%"'.
                                          format(internal_tag_table, internal_tag_table), (item_to_rename,))
                ctlr_dict = {x[0]: x[1].split('; ') for x in rename_tag_cursor.fetchall() if x[1] is not None}
                for k, v in ctlr_dict.items():
                    v_2 = [new_name.casefold() if x == item_to_rename.casefold() else x for x in v]
                    v_2.sort(key=lambda x: x.casefold())
                    v_2 = '; '.join(v_2)
                    rename_tag_cursor.execute('UPDATE custom_tag_logic SET {} = ? WHERE ctlr_id = ?'.
                                              format(internal_tag_table), (v_2, k))
                rename_tag_conn.commit()

                rename_succ_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Success',
                                                        'Tag <b>{}</b> has been successfully renamed to <b>{}</b>.'
                                                        .format(item_to_rename, new_name))
                rename_succ_win.exec_()

        if label == 'tag type':
            self.populate_tag_widgets(self.tagGroupListWid)
            self.tagListWid.clear()
        else:
            self.populate_tag_widgets(self.tagListWid)

        self.tagGroupRenameButton.setDisabled(True)
        self.addTagButton.setDisabled(True)
        self.renameTagButton.setDisabled(True)
        self.removeTagButton.setDisabled(True)
        self.moveTagButton.setDisabled(True)
        self.reposTagUpButton.setDisabled(True)
        self.sortButton.setDisabled(True)
        self.reposTagDownButton.setDisabled(True)

        rename_tag_conn.close()
        rename_tag_settings_conn.close()

    def add_new_tag(self):
        ant_settings_conn = sqlite3.connect(common_vars.settings_db())
        ant_settings_cursor = ant_settings_conn.cursor()

        ant_tags_conn = sqlite3.connect(common_vars.video_db())
        ant_tags_cursor = ant_tags_conn.cursor()

        tag_table = common_vars.tag_table_lookup()[self.tagGroupListWid.currentItem().text()]
        existing_tags = [tag[0] for tag in ant_tags_conn.execute('SELECT * FROM {}'.format(tag_table))]
        sort_order = [so for so in ant_tags_conn.execute('SELECT sort_order FROM {}'.format(tag_table))]

        if not sort_order:
            max_sort_order_number = 0
        else:
            max_sort_order_number = max(sort_order)[0]

        add_tag_window = generic_entry_window.GenericEntryWindow('new', inp_1='tag',
                                                                 dupe_check_list=existing_tags)
        if add_tag_window.exec_():
            new_tag = add_tag_window.textBox.text()
            ant_tags_cursor.execute(
                'INSERT INTO {} (tag_name, tag_desc, sort_order, disable_tags) VALUES (?, ?, ?, ?)'.format(tag_table),
                (new_tag, '', max_sort_order_number + 1, ''))
            ant_tags_cursor.execute('UPDATE tags_lookup SET in_use = 1 WHERE internal_field_name = ?', (tag_table,))

            entry_field_tag_name = 'Tags - {}'.format(self.tagGroupListWid.currentItem().text())
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

    def remove_tag(self, move_tag_entry=False):
        # TODO: Fix sort order after tag has been deleted
        rt_settings_conn = sqlite3.connect(common_vars.settings_db())
        rt_settings_cursor = rt_settings_conn.cursor()
        rt_tags_conn = sqlite3.connect(common_vars.video_db())
        rt_tags_cursor = rt_tags_conn.cursor()

        sub_db_list = [v for k, v in common_vars.sub_db_lookup().items()]
        tag_to_del = self.tagListWid.currentItem().text()
        tag_table = common_vars.tag_table_lookup()[self.tagGroupListWid.currentItem().text()]

        msgBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Warning',
                                       'Tag <b>{}</b> will be removed from the tag list, and from all<br>'
                                       'video entries which have it. This is not reversible. Ok to<br>'
                                       'proceed?'.format(self.tagListWid.currentItem().text()),
                                       QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
        if not move_tag_entry:
            result = msgBox.exec_()
        else:
            result = msgBox.No

        if result == QtWidgets.QMessageBox.Yes or move_tag_entry:
            rt_tags_conn.execute('DELETE FROM {} WHERE tag_name = ?'.format(tag_table), (tag_to_del,))
            is_empty = rt_tags_conn.execute('SELECT COUNT(*) FROM {}'.format(tag_table))

            # If tag list is empty, update in_use to 0
            if is_empty.fetchall()[0][0] == 0:
                rt_tags_conn.execute('UPDATE tags_lookup SET in_use = 0 WHERE internal_field_name = ?', (tag_table,))
                rt_settings_cursor.execute(
                    'UPDATE search_field_lookup SET in_use = ? WHERE field_name_internal = ?', (0, tag_table))

            # Delete tag from existing videos
            for subdb in sub_db_list:
                rt_tags_cursor.execute('SELECT video_id, {} FROM {} WHERE {} LIKE "%"||?||"%"'.format(tag_table, subdb,
                                                                                                      tag_table),
                                       (tag_to_del.lower(),))
                del_tag_dict = {x[0]: x[1].split('; ') for x in rt_tags_cursor.fetchall() if x[1] is not None}
                del_tag_dict_new = {vidid: '; '.join(sorted([t for t in tags if t != tag_to_del.lower()],
                                                            key=lambda x: x.lower()))
                                    for vidid, tags in del_tag_dict.items()}
                for v_id, tag_str in del_tag_dict_new.items():
                    rt_tags_cursor.execute('UPDATE {} SET {} = ? WHERE video_id = ?'.format(subdb, tag_table),
                                           (tag_str, v_id))

            # Delete tag from disable_tag column in tag table
            rt_tags_cursor.execute('SELECT tag_name, disable_tags FROM {} WHERE disable_tags LIKE "%"||?||"%"'
                                   .format(tag_table), (tag_to_del,))
            dis_tag_dict = {x[0]: x[1].split('; ') for x in rt_tags_cursor.fetchall() if x[1] is not None}
            dis_tag_dict_new = {tag_name: '; '.join(sorted([t for t in dis_tags if t.lower() != tag_to_del.lower()],
                                                           key=lambda x: x.lower()))
                                for tag_name, dis_tags in dis_tag_dict.items()}
            for tag, d_tags in dis_tag_dict_new.items():
                rt_tags_cursor.execute('UPDATE {} SET disable_tags = ? WHERE tag_name = ?'.format(tag_table),
                                       (d_tags, tag))

            # Delete tag from custom tag logic
            rt_tags_cursor.execute('SELECT ctlr_id, {} FROM custom_tag_logic WHERE {} LIKE "%"||?||"%"'.
                                   format(tag_table, tag_table), (tag_to_del,))
            ctlr_dict = {x[0]: x[1].split('; ') for x in rt_tags_cursor.fetchall()}
            for k, v in ctlr_dict.items():
                v.remove(tag_to_del.casefold())
                new_str = '; '.join(v)
                rt_tags_cursor.execute('UPDATE custom_tag_logic SET {} = ? WHERE ctlr_id = ?'.
                                       format(tag_table), (new_str, k))

            rt_settings_conn.commit()
            rt_tags_conn.commit()

            del_tag_succ_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Success',
                                                     'Tag <b>{}</b> has been successfully removed from the database.'
                                                     .format(tag_to_del))
            if not move_tag_entry:
                del_tag_succ_win.exec_()

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
        move_tm_settings_conn = sqlite3.connect(common_vars.settings_db())
        move_tm_settings_cursor = move_tm_settings_conn.cursor()
        move_tm_tag_conn = sqlite3.connect(common_vars.video_db())
        move_tm_tag_cursor = move_tm_tag_conn.cursor()

        subdb_list = [v for k, v in common_vars.sub_db_lookup().items()]
        origin_table = common_vars.tag_table_lookup()[self.tagGroupListWid.currentItem().text()]
        origin_table_friendly = self.tagGroupListWid.currentItem().text()
        tag_to_move = self.tagListWid.currentItem().text()
        mod_tag_type_table = [typ[0] for typ in move_tm_tag_conn.execute('SELECT user_field_name FROM tags_lookup')]
        mod_tag_type_table.remove(origin_table_friendly)

        move_window = move_tag_window.MoveTagWindow(tag_to_move, origin_table_friendly, mod_tag_type_table)
        if move_window.exec_():
            # Move tag from origin tag table to destination tag table
            dest_table = common_vars.tag_table_lookup()[move_window.tableDropdown.currentText()]
            dest_sort_order_list = [so[0] for so in
                                    move_tm_tag_conn.execute('SELECT sort_order FROM {}'.format(dest_table))]
            if not dest_sort_order_list:
                dest_max_sort_order = 1
            else:
                dest_max_sort_order = max(dest_sort_order_list) + 1

            move_tm_tag_cursor.execute('UPDATE {} SET sort_order = ? WHERE tag_name = ?'.format(origin_table),
                                       (dest_max_sort_order, tag_to_move))
            move_tm_tag_cursor.execute('SELECT tag_name, tag_desc, sort_order, disable_tags FROM {} WHERE tag_name = ?'
                                       .format(origin_table), (tag_to_move,))
            transfer = move_tm_tag_cursor.fetchall()[0]

            move_tm_tag_cursor.execute(
                'INSERT INTO {} (tag_name, tag_desc, sort_order, disable_tags) VALUES (?, ?, ?, ?)'.format(dest_table),
                transfer)
            move_tm_tag_cursor.execute('DELETE FROM {} WHERE tag_name = ?'.format(origin_table), (tag_to_move,))

            move_tm_tag_cursor.execute('SELECT tag_name, sort_order FROM {}'.format(origin_table))
            origin_mod_tags = move_tm_tag_cursor.fetchall()
            origin_mod_tags.sort(key=lambda x: x[1])
            for new_so in range(1, len(origin_mod_tags) + 1):
                move_tm_tag_cursor.execute('UPDATE {} SET sort_order = ? WHERE tag_name = ?'.format(origin_table),
                                           (new_so, origin_mod_tags[new_so - 1][0]))

            # Insert tag into new column in custom_tag_logic
            move_tm_tag_cursor.execute('SELECT ctlr_id, {} FROM custom_tag_logic WHERE {} LIKE "%"||?||"%"'.
                                       format(dest_table, origin_table), (tag_to_move,))
            ctlr_dict = {x[0]: x[1].split('; ') for x in move_tm_tag_cursor.fetchall()}

            for k, v in ctlr_dict.items():
                v.append(tag_to_move.lower())
                v.sort(key=lambda x: x.casefold())
                if '' in v:
                    v.remove('')
                new_str = '; '.join(v)
                move_tm_tag_cursor.execute('UPDATE custom_tag_logic SET {} = ?'.format(dest_table), (new_str,))

            # Delete any existing disable_tags data
            move_tm_tag_cursor.execute('UPDATE {} SET disable_tags = "" WHERE tag_name = ?'.format(dest_table),
                                       (tag_to_move,))

            # Move selected tag in sub-DBs to destination tag column
            for sdb in subdb_list:
                move_tm_tag_cursor.execute('SELECT video_id, {} FROM {} WHERE {} LIKE "%"||?||"%"'
                                           .format(dest_table, sdb, origin_table), (tag_to_move.lower(),))
                new_tag_col_dict = {x[0]: sorted(x[1].split('; ') + [tag_to_move.lower()], key=lambda x: x.lower())
                if x[1] is not None else [tag_to_move.lower()] for x in move_tm_tag_cursor.fetchall()}
                for k, v in new_tag_col_dict.items():
                    if '' in v:
                        v.remove('')
                new_tag_col_dict_new = {vidid: '; '.join(tag_str) for vidid, tag_str in new_tag_col_dict.items()}
                for v_id, t_str in new_tag_col_dict_new.items():
                    move_tm_tag_cursor.execute('UPDATE {} SET {} = ? WHERE video_id = ?'.format(sdb, dest_table),
                                               (t_str, v_id))

            move_tm_tag_conn.execute('UPDATE tags_lookup SET in_use = 1 WHERE internal_field_name = ?', (dest_table,))
            move_tm_settings_cursor.execute(
                'UPDATE search_field_lookup SET in_use = 1 WHERE field_name_internal = ?', (dest_table,))

            move_tm_settings_conn.commit()
            move_tm_settings_conn.close()
            move_tm_tag_conn.commit()
            move_tm_tag_conn.close()

            # Delete tag from origin column
            self.remove_tag(move_tag_entry=True)

            move_tag_succ_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Success',
                                                      'Tag <b>{}</b> has successfully been moved from tag group <b>{}</b><br>'
                                                      'to tag group <b>{}</b>.'.format(tag_to_move, origin_table_friendly,
                                                                                  move_window.tableDropdown.currentText()))
            move_tag_succ_win.exec_()

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
        tag_table_friendly = self.tagGroupListWid.currentItem().text()
        tag_table_internal = common_vars.tag_table_lookup()[tag_table_friendly]
        repos_cursor.execute('SELECT sort_order FROM {} WHERE tag_name = ?'
                             .format(tag_table_internal), (selected_tag,))
        selected_tag_pos = repos_cursor.fetchone()[0]
        max_sort_order = max([so for so in repos_conn.execute('SELECT sort_order FROM {}'.format(tag_table_internal))])[
            0]

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
                'INSERT INTO {} (tag_name, tag_desc, sort_order, disable_tags) VALUES (?, ?, ?, ?)'.format(tag_table_internal),
                (extracted_tag[0], extracted_tag[1], selected_tag_pos, extracted_tag[3]))

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

        tag_table_friendly = self.tagGroupListWid.currentItem().text()
        tag_table_internal = common_vars.tag_table_lookup()[tag_table_friendly]
        sort_order_list = [so[0] for so in
                           sort_tag_conn.execute('SELECT sort_order FROM {}'.format(tag_table_internal))]
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

        tag_table = common_vars.tag_table_lookup()[self.tagGroupListWid.currentItem().text()]
        desc_text = self.tagDescEditor.toPlainText()
        tag_name = self.tagListWid.currentItem().text()

        save_desc_cursor.execute('UPDATE {} SET tag_desc = ? WHERE tag_name = ?'.format(tag_table),
                                 (desc_text, tag_name))

        save_desc_tag_conn.commit()
        save_desc_tag_conn.close()

        settings_notifications.SettingsNotificationWindow('desc updated', inp_str1=tag_name)

    def set_mut_excl_tags_clicked(self):
        self.mut_excl_win = mut_excl_tags_window.MutuallyExclTagsWindow()
        self.mut_excl_win.show()

    def custom_tag_logic_clicked(self):
        self.ctlr_mgmt_win = custom_tag_logic_window.TagLogicMgmt()
        self.ctlr_mgmt_win.show()
