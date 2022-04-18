import datetime
import os
import pickle

import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import sqlite3
import xlrd

from os import getcwd, listdir
from shutil import copyfile

from misc_files import checkbox_list_window, common_vars, check_compatibility, generic_entry_window


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(str, int, int)

    def __init__(self, f_path):
        super(Worker, self).__init__()
        self.f_path = f_path

    def run(self):
        conn = sqlite3.connect(common_vars.video_db())
        cursor = conn.cursor()
        book = xlrd.open_workbook(self.f_path)

        # Move data
        for sht_ind in range(0, book.nsheets):
            sheet = book.sheet_by_index(sht_ind)
            tn = 'sub_db_{}'.format(sht_ind)
            list_of_tup =[]

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
                '"date_entered"	TEXT, "play_count"	INTEGER, "vid_thumb_path" TEXT, PRIMARY KEY("video_id"))'.format(sht_ind))

            cursor.execute('INSERT OR IGNORE INTO db_name_lookup (table_name, user_subdb_name) VALUES (?, ?)',
                           (tn, sheet.name))
            conn.commit()

            for row in range(1, sheet.nrows):
                field_dict = dict()
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
                    rel_date = xlrd.xldate_as_datetime(int(sheet.cell_value(row, 5)), 0).isoformat()[:10].replace('-', '/')
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
                field_dict['tags_4'] = ''
                field_dict['tags_5'] = ''
                field_dict['tags_6'] = ''
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
                field_dict['play_count'] = 0
                field_dict['vid_thumb_path'] = ''
                field_dict['awards_won'] = ''
                field_dict['video_description'] = ''
                field_dict['editor_youtube_channel_url'] = ''
                field_dict['editor_org_profile_url'] = ''
                field_dict['editor_amvnews_profile_url'] = ''
                field_dict['editor_other_profile_url'] = ''

                lst_of_vals = []
                for key, val in common_vars.entry_dict().items():
                    lst_of_vals.append(field_dict[key])

                list_of_tup.append(tuple(lst_of_vals))

                self.progress.emit(book.sheet_names()[sht_ind], row, sheet.nrows)

            cursor.executemany('INSERT INTO {} VALUES({})'
                               .format(tn,
                                       ', '.join(['?' for x in range(0, len(common_vars.entry_dict()))])),
                               list_of_tup)
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
        self.gridLayout.setHorizontalSpacing(10)

        self.verticalSpacer = QtWidgets.QSpacerItem(10, 10)

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

        self.gridLayout.addWidget(self.importButton, grid_v_index, 0, alignment=QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.importDrop, grid_v_index, 1, 1, 2, alignment=QtCore.Qt.AlignLeft)
        grid_v_index += 1

        self.gridLayout.setRowMinimumHeight(grid_v_index, 20)
        grid_v_index += 1

        self.dbOperationsLabel = QtWidgets.QLabel()
        self.dbOperationsLabel.setText('Database operations')
        self.dbOperationsLabel.setFont(self.boldFont)
        self.gridLayout.addWidget(self.dbOperationsLabel, grid_v_index, 0, alignment=QtCore.Qt.AlignCenter)

        self.CLOperationsLabel = QtWidgets.QLabel()
        self.CLOperationsLabel.setText('Custom List operations')
        self.CLOperationsLabel.setFont(self.boldFont)
        self.gridLayout.addWidget(self.CLOperationsLabel, grid_v_index, 1, alignment=QtCore.Qt.AlignCenter)
        grid_v_index += 1

        self.newDBButton = QtWidgets.QPushButton('Create new database')
        self.newDBButton.setFixedWidth(150)
        self.gridLayout.addWidget(self.newDBButton, grid_v_index, 0, alignment=QtCore.Qt.AlignCenter)

        self.importCLButton = QtWidgets.QPushButton('Import Custom Lists')
        self.importCLButton.setFixedWidth(150)
        self.importCLButton.setToolTip('Import Custom Lists from a previous version\nof AMV Tracker.')
        self.gridLayout.addWidget(self.importCLButton, grid_v_index, 1, alignment=QtCore.Qt.AlignCenter)
        grid_v_index += 1

        self.changeCurrDBButton = QtWidgets.QPushButton('Select working database')
        self.changeCurrDBButton.setFixedWidth(150)
        self.gridLayout.addWidget(self.changeCurrDBButton, grid_v_index, 0, alignment=QtCore.Qt.AlignCenter)

        self.createCustomListButton = QtWidgets.QPushButton('Create new Custom List')
        self.createCustomListButton.setFixedWidth(150)
        self.gridLayout.addWidget(self.createCustomListButton, grid_v_index, 1, alignment=QtCore.Qt.AlignCenter)
        grid_v_index += 1

        self.createBackupButton = QtWidgets.QPushButton('Create backup')
        self.createBackupButton.setFixedWidth(150)
        self.gridLayout.addWidget(self.createBackupButton, grid_v_index, 0, alignment=QtCore.Qt.AlignCenter)

        self.renameCustomListButton = QtWidgets.QPushButton('Rename Custom List')
        self.renameCustomListButton.setFixedWidth(150)
        self.gridLayout.addWidget(self.renameCustomListButton, grid_v_index, 1, alignment=QtCore.Qt.AlignCenter)
        grid_v_index += 1

        self.restoreBackupButton = QtWidgets.QPushButton('Restore backup')
        self.restoreBackupButton.setFixedWidth(150)
        self.gridLayout.addWidget(self.restoreBackupButton, grid_v_index, 0, alignment=QtCore.Qt.AlignCenter)

        self.deleteCustomListButton = QtWidgets.QPushButton('Delete Custom Lists')
        self.deleteCustomListButton.setFixedWidth(150)
        self.gridLayout.addWidget(self.deleteCustomListButton, grid_v_index, 1, alignment=QtCore.Qt.AlignCenter)
        grid_v_index += 1

        self.deleteBackupsButton = QtWidgets.QPushButton('Delete backups')
        self.deleteBackupsButton.setFixedWidth(150)
        self.deleteBackupsButton.setToolTip('Delete old and unneeded backup files.')
        self.gridLayout.addWidget(self.deleteBackupsButton, grid_v_index, 0, alignment=QtCore.Qt.AlignCenter)
        grid_v_index += 1

        self.gridLayout.setRowMinimumHeight(grid_v_index, 20)
        grid_v_index += 1

        self.subDBOperationsLabel = QtWidgets.QLabel()
        self.subDBOperationsLabel.setText('Sub-database operations')
        self.subDBOperationsLabel.setFont(self.boldFont)
        self.gridLayout.addWidget(self.subDBOperationsLabel, grid_v_index, 0, alignment=QtCore.Qt.AlignCenter)
        grid_v_index += 1

        self.addSubDBButton = QtWidgets.QPushButton('Add sub-DB')
        self.addSubDBButton.setFixedWidth(150)
        self.gridLayout.addWidget(self.addSubDBButton, grid_v_index, 0, alignment=QtCore.Qt.AlignCenter)
        grid_v_index += 1

        self.renameSubDBsButton = QtWidgets.QPushButton('Rename sub-DB')
        self.renameSubDBsButton.setFixedWidth(150)
        self.gridLayout.addWidget(self.renameSubDBsButton, grid_v_index, 0, alignment=QtCore.Qt.AlignCenter)
        grid_v_index += 1

        self.deleteSubDBButton = QtWidgets.QPushButton('Delete sub-DB')
        self.deleteSubDBButton.setFixedWidth(150)
        self.gridLayout.addWidget(self.deleteSubDBButton, grid_v_index, 0, alignment=QtCore.Qt.AlignCenter)
        grid_v_index += 1

        self.clearAllDataButton = QtWidgets.QPushButton('Clear all data')
        self.clearAllDataButton.setFixedWidth(150)
        self.clearAllDataButton.setToolTip('Delete all data from a sub-DB, but\nkeep the sub-DB.')
        self.gridLayout.addWidget(self.clearAllDataButton, grid_v_index, 0, alignment=QtCore.Qt.AlignCenter)
        grid_v_index += 1

        self.clearSelectDataButton = QtWidgets.QPushButton('Clear select data')
        self.clearSelectDataButton.setFixedWidth(150)
        self.clearSelectDataButton.setToolTip('Delete selected data from all entries in selected sub-DBs.')
        self.gridLayout.addWidget(self.clearSelectDataButton, grid_v_index, 0, alignment=QtCore.Qt.AlignCenter)
        grid_v_index += 1

        ## Signals/slots
        # DB operations
        self.importButton.clicked.connect(lambda: self.reset_tag_settings())
        self.importButton.clicked.connect(lambda: self.import_btn_clicked())
        self.newDBButton.clicked.connect(lambda: self.create_db())
        self.changeCurrDBButton.clicked.connect(lambda: self.select_db())
        self.createBackupButton.clicked.connect(lambda: self.backup('create'))
        self.restoreBackupButton.clicked.connect(lambda: self.backup('restore'))
        self.deleteBackupsButton.clicked.connect(lambda: self.backup('delete'))

        # Sub-DB operations
        self.addSubDBButton.clicked.connect(lambda: self.add_subdb())
        self.renameSubDBsButton.clicked.connect(lambda: self.rename_subdb())
        self.deleteSubDBButton.clicked.connect(lambda: self.delete_subdb())
        self.clearAllDataButton.clicked.connect(lambda: self.clear_data(del_all=True))
        self.clearSelectDataButton.clicked.connect(lambda: self.clear_data())

        # Custom List operations
        self.importCLButton.clicked.connect(lambda: self.import_custom_lists())
        self.createCustomListButton.clicked.connect(lambda: self.cust_list_ops('add'))
        self.renameCustomListButton.clicked.connect(lambda: self.cust_list_ops('rename'))
        self.deleteCustomListButton.clicked.connect(lambda: self.cust_list_ops('delete'))

    def import_btn_clicked(self):
        # TODO: Make sure tag settings/settings db are reset
        if self.importDrop.currentText() == 'Previous AMV Tracker version':
            import_expl_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Import file',
                                                    'Please select a database file from an old (pre-v2) version\n'
                                                    'of AMV Tracker, and all the entries will be imported into a\n'
                                                    'new database compatible with v2. Ok to proceed?',
                                                    QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
            if import_expl_win.exec_() == QtWidgets.QMessageBox.Yes:
                f_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select AMVT database', '',
                                                               'Spreadsheet file (*xls)')[0]
                import_compat = check_compatibility.is_compatible('xl', f_path)

                if f_path != '' and import_compat:
                    alert_to_user = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Must create new db',
                                                          'Video entries imported from a previous version of AMV Tracker must\n'
                                                          'be put in a new database. Please select the directory in which you\n'
                                                          'would like to save this new database, and name it.')
                    if alert_to_user.exec_():
                        self.create_db(import_old=True)

                        self.thrd = QtCore.QThread()
                        self.worker = Worker(f_path)
                        self.worker.moveToThread(self.thrd)

                        self.pBar.show()

                        self.thrd.started.connect(self.worker.run)
                        self.worker.finished.connect(self.thrd.quit)
                        self.worker.finished.connect(self.worker.deleteLater)
                        self.thrd.finished.connect(self.thrd.deleteLater)
                        self.worker.progress.connect(self.show_import_progress)
                        self.thrd.finished.connect(self.pBar.close)

                        self.thrd.start()

                    self.reset_tag_settings()

                elif f_path != '':
                    incompat_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Incompatible file',
                                                         'This is not a valid AMV Tracker database. No action\n'
                                                         'has been taken')
                    incompat_win.exec_()

        else:  # CSV document
            # TODO: Import CSV
            print('csv')

    def show_import_progress(self, sub_db_name, n, total):
        self.pBar.setFormat('Importing from [{}]: Entry {} of {}'.format(sub_db_name, n, total - 1))
        self.pBar.setMaximum(total - 1)
        self.pBar.setValue(n)

    def create_db(self, import_old=False):
        create_db_settings_conn = sqlite3.connect(common_vars.settings_db())
        create_db_settings_cursor = create_db_settings_conn.cursor()
        if import_old:
            template_path = '/db_files/db_template - import ver.db'
        else:
            template_path = '/db_files/db_template.db'

        db_template_src = getcwd() + template_path

        f_dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select the directory in which to create the new '
                                                                 'database...')
        if f_dir:
            existing_files = listdir(f_dir)
            name_db_window = generic_entry_window.GenericEntryWindow('name_db', inp_1=f_dir,
                                                                     dupe_check_list=existing_files)

            if name_db_window.exec_():
                set_cwd = False
                full_dir = f_dir + '/' + name_db_window.textBox.text() + '.db'
                copyfile(db_template_src, full_dir)

                if import_old is False:
                    set_default_window = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Database created',
                                                               'Database {} has been created. Would you like to set it as\n'
                                                               'the current working database?'
                                                               .format(name_db_window.textBox.text()),
                                                               QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
                    if set_default_window.exec_() == QtWidgets.QMessageBox.Yes:
                        set_cwd = True

                if import_old is True or set_cwd is True:
                    create_db_settings_cursor.execute('UPDATE db_settings SET path_to_db = ?, db_name = ?',
                                                      (full_dir, name_db_window.textBox.text()))
                    create_db_settings_conn.commit()

                    db_set_window = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Working database set',
                                                          '{} has been set as the current working database.'
                                                          .format(name_db_window.textBox.text() + '.db'))
                    db_set_window.exec_()

                new_thumb_path = getcwd() + '\\thumbnails\\{}'.format(name_db_window.textBox.text())
                if not os.path.isdir(new_thumb_path):
                    os.mkdir(new_thumb_path)

                new_db_conn = sqlite3.connect(full_dir)
                new_db_cursor = new_db_conn.cursor()
                new_db_cursor.execute('UPDATE misc_settings SET value = ? WHERE setting_name = ?', (new_thumb_path,
                                                                                                    'thumbnail_path'))
                new_db_conn.commit()
                new_db_conn.close()

        create_db_settings_conn.close()
        self.reset_tag_settings()

    def select_db(self):
        # Change current working database
        select_db_settings_conn = sqlite3.connect(common_vars.settings_db())
        select_db_settings_cursor = select_db_settings_conn.cursor()

        template_path = (getcwd() + '/db_files/db_template.db').replace('\\', '/')
        new_db_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select database file', '', 'Database files (*db)')
        compatible = check_compatibility.is_compatible('sqlite', new_db_path[0])

        if new_db_path[0] != '':
            if template_path != new_db_path[0].replace('\\', '/') and compatible:
                file_name = new_db_path[0].replace('\\', '/').split('/')[-1]
                select_db_settings_cursor.execute('UPDATE db_settings SET path_to_db = ?, db_name = ?',
                                                  (new_db_path[0], file_name[:-3]))
                select_db_settings_conn.commit()

                db_path_updated_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Working database set',
                                                            '{} has been set as the current working database.'
                                                            .format(file_name))
                db_path_updated_win.exec_()

            else:
                invalid_selection_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Invalid selection',
                                                              'This is not a valid AMV Tracker database. No action\n'
                                                              'has been taken.')
                invalid_selection_win.exec_()

        select_db_settings_conn.close()
        self.reset_tag_settings()

    def reset_tag_settings(self):
        # Used to reset tag data in search_field_lookup table in settings.db based on tags_lookup table in cwd; used
        # when switching to a new db or importing one

        res_tag_subdb_conn = sqlite3.connect(common_vars.video_db())
        res_tag_subdb_cursor = res_tag_subdb_conn.cursor()
        res_tag_settings_conn = sqlite3.connect(common_vars.settings_db())
        res_tag_settings_cursor = res_tag_settings_conn.cursor()

        res_tag_subdb_cursor.execute('SELECT internal_field_name, user_field_name, in_use FROM tags_lookup')
        tags_master_data = res_tag_subdb_cursor.fetchall()
        for data_grp in tags_master_data:
            res_tag_settings_cursor.execute('UPDATE search_field_lookup SET field_name_display = ?, in_use = ? WHERE '
                                            'field_name_internal = ?', ('Tags - ' + data_grp[1], data_grp[2],
                                                                        data_grp[0]))

        res_tag_settings_conn.commit()
        res_tag_subdb_conn.close()
        res_tag_settings_conn.close()

    def add_subdb(self):
        add_subdb_conn = sqlite3.connect(common_vars.video_db())
        add_subdb_cursor = add_subdb_conn.cursor()
        existing_subdb_list = [key for key, val in common_vars.sub_db_lookup().items()]
        query = common_vars.sqlite_queries('create table')

        name_subdb_window = generic_entry_window.GenericEntryWindow('new_subdb',
                                                                    dupe_check_list=existing_subdb_list)

        if name_subdb_window.exec_():
            new_subdb_name = name_subdb_window.textBox.text()
            new_subdb_number = add_subdb_cursor.execute('SELECT COUNT(*) FROM db_name_lookup').fetchone()[0]

            add_subdb_cursor.execute('INSERT OR IGNORE INTO db_name_lookup VALUES (?, ?)',
                                     ('sub_db_{}'.format(new_subdb_number), new_subdb_name))
            add_subdb_cursor.execute(query.format(str(new_subdb_number)))

            add_subdb_conn.commit()

            subdb_added_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Sub-DB added',
                                                    'Sub-DB [{}] has successfully been added to\nthe database.'
                                                    .format(new_subdb_name))
            subdb_added_win.exec_()

        add_subdb_conn.close()

    def rename_subdb(self):
        rename_subdb_conn = sqlite3.connect(common_vars.video_db())
        rename_subdb_cursor = rename_subdb_conn.cursor()
        subdb_dict = common_vars.sub_db_lookup()
        subdb_name_list = [key for key, val in subdb_dict.items() if key != 'Main database']

        if subdb_name_list:
            subdb_name_list.sort(key=lambda x: x.casefold())
            rename_subdb_window = generic_entry_window.GenericEntryWindowWithDrop('rename',
                                                                                  subdb_name_list,
                                                                                  inp_str1='sub-DB',
                                                                                  dupe_list=subdb_name_list)
            if rename_subdb_window.exec_():
                db_to_rename = common_vars.sub_db_lookup()[rename_subdb_window.drop.currentText()]
                rename_subdb_cursor.execute('UPDATE db_name_lookup SET user_subdb_name = ? WHERE table_name = ?',
                                            (rename_subdb_window.textBox.text(), db_to_rename))
                rename_subdb_conn.commit()

                subdb_renamed_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Sub-DB renamed',
                                                          'Sub-DB {} has been renamed to {}.'
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

        if subdb_name_list:  # If database has sub-DBs
            subdb_cbox_win = checkbox_list_window.CheckboxListWindow('del sub db', subdb_name_list)
            if subdb_cbox_win.exec_():
                if not subdb_cbox_win.get_checked_boxes():  # If no sub-DB selected
                    nothing_selected = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Nothing selected',
                                                             'No sub-DBs selected -- no action has been taken.')
                    nothing_selected.exec_()
                else:  # Delete the sub-DB table itself and the sub-DB reference in db_name_lookup
                    for subdb in subdb_cbox_win.get_checked_boxes():
                        # Delete table from db file
                        delete_subdb_cursor.execute('DROP TABLE IF EXISTS {}'.format(subdb_dict[subdb]))
                        delete_subdb_cursor.execute('DELETE FROM db_name_lookup WHERE user_subdb_name = ?', (subdb,))
                    delete_subdb_conn.commit()

                    # Remove db lookup reference from db_name_lookup, and re-number table_name entries
                    # All these steps are necessary to ensure that the db_name_lookup table properly references the
                    # correct tables.
                    remaining_subdbs_dict = common_vars.sub_db_lookup(reverse=True)  # {old sub_db_# : subdb name}
                    subdbs_ref_dict = {}  # {old sub_db_# : new sub_db_#}
                    subdb_ind = 0
                    for k, v in remaining_subdbs_dict.items():
                        subdbs_ref_dict[k] = 'sub_db_{}'.format(str(subdb_ind))
                        subdb_ind += 1

                    new_mapping = {}  # {new sub_db_# : subdb name}
                    for k, v in subdbs_ref_dict.items():
                        new_mapping[v] = remaining_subdbs_dict[k]

                    delete_subdb_cursor.execute('DELETE FROM db_name_lookup')
                    delete_subdb_conn.commit()

                    for k, v in new_mapping.items():
                        delete_subdb_cursor.execute(
                            'INSERT OR IGNORE INTO db_name_lookup (table_name, user_subdb_name) '
                            'VALUES (?, ?)', (k, v))

                    delete_subdb_conn.commit()
                    # Rename the sub-db tables to be properly numbered to line up with the reference table
                    # db_name_lookup
                    for k, v in subdbs_ref_dict.items():
                        delete_subdb_cursor.execute('ALTER TABLE {} RENAME TO {}'.format(k, 's' + v[-1]))

                    delete_subdb_conn.commit()

                    for k, v in subdbs_ref_dict.items():
                        delete_subdb_cursor.execute('ALTER TABLE {} RENAME TO {}'.format('s' + v[-1], v))

                    delete_subdb_conn.commit()

                    deleted_subdbs_str = ''
                    for sdb in subdb_cbox_win.get_checked_boxes():
                        deleted_subdbs_str += '\u2022 ' + sdb + '\n'

                    operation_compl_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Completed',
                                                                'Following sub-DB(s) deleted successfully:\n\n' +
                                                                deleted_subdbs_str)
                    operation_compl_win.exec_()

        else:  # If database has no sub-DBs
            no_subdbs_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'No sub-dbs',
                                                  'This database currently has no sub-databases to delete.\n'
                                                  'No action has been taken.')
            no_subdbs_win.exec_()

        delete_subdb_conn.close()

    def clear_data(self, del_all=False):
        clear_data_conn = sqlite3.connect(common_vars.video_db())
        clear_data_cursor = clear_data_conn.cursor()

        subdb_dict = common_vars.sub_db_lookup()
        subdb_name_list = [key for key, val in subdb_dict.items() if key != 'Main database']
        subdb_name_list.sort(key=lambda x: x.casefold())
        subdb_name_list.insert(0, 'Main database')

        field_name_list = [key for key, val in common_vars.video_field_lookup(filt='user_can_mass_upd').items() if
                           (key != 'Primary editor username' and key != 'Video title')]
        field_name_list.sort(key=lambda x: x.casefold())

        if del_all:
            cbox_win = checkbox_list_window.CheckboxListWindow('clear all', subdb_name_list)
            if cbox_win.exec_():
                if cbox_win.get_checked_boxes() == []:
                    nothing_checked_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Nothing selected',
                                                                'No sub-DBs selected -- no action has been taken.')
                    nothing_checked_win.exec_()
                else:
                    for subdb in cbox_win.get_checked_boxes():
                        clear_data_cursor.execute('DELETE FROM {}'.format(subdb_dict[subdb]))

                    clear_data_conn.commit()
                    cleared_sdb_str = ''
                    for sdb in cbox_win.get_checked_boxes():
                        cleared_sdb_str += '\u2022 ' + sdb + '\n'

                    all_data_cleared_succ = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'All data cleared',
                                                                  'All data has been cleared from the following sub-DB:\n\n' +
                                                                  cleared_sdb_str)
                    all_data_cleared_succ.exec_()

        else:
            drop_and_cbox_win = checkbox_list_window.CheckboxListWindow('clear selected', field_name_list,
                                                                        drop_list=subdb_name_list)
            if drop_and_cbox_win.exec_():
                if drop_and_cbox_win.get_checked_boxes() == []:
                    no_field_sel_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Nothing selected',
                                                             'No fields were selected to clear -- no action has been '
                                                             'taken.')
                    no_field_sel_win.exec_()
                else:
                    sel_subdb_int = common_vars.sub_db_lookup()[drop_and_cbox_win.drop.currentText()]
                    sel_fields = drop_and_cbox_win.get_checked_boxes()

                    for field in sel_fields:
                        if field == 'release_date_unknown' or field == 'notable' or field == 'favorite':
                            cleared_data = 0
                        else:
                            cleared_data = ''
                        int_field = common_vars.video_field_lookup()[field]
                        clear_data_cursor.execute('UPDATE {} SET {} = ?'.format(sel_subdb_int, int_field),
                                                  (cleared_data,))
                    clear_data_conn.commit()
                    sel_data_cleared_succ = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                                                  'Selected data cleared',
                                                                  'Selected data has been cleared from\n'
                                                                  'sub-DB {}.'.format(
                                                                      drop_and_cbox_win.drop.currentText()))
                    sel_data_cleared_succ.exec_()

        clear_data_conn.close()

    def backup(self, operation):
        backup_conn = sqlite3.connect(common_vars.settings_db())
        backup_cursor = backup_conn.cursor()
        backup_cursor.execute('SELECT path_to_db FROM db_settings')
        curr_db_fpath = backup_cursor.fetchone()[0]
        curr_db_name = curr_db_fpath.replace('\\', '/').split('/')[-1][:-3]

        # Datestamp formatting
        if len(str(datetime.date.today().month)) == 1:
            month = '0' + str(datetime.date.today().month)
        else:
            month = str(datetime.date.today().month)

        if len(str(datetime.date.today().day)) == 1:
            day = '0' + str(datetime.date.today().day)
        else:
            day = str(datetime.date.today().day)

        datestamp = '[' + str(datetime.date.today().year) + '-' + month + '-' + day + ']'
        backup_dir = os.getcwd() + '\\db_files\\backups'
        backup_db_name = curr_db_name + '__BACKUP_' + datestamp
        new_backup_fpath = '{}\\{}.db'.format(backup_dir, backup_db_name)

        files_in_backup_dir = os.listdir(backup_dir)

        if operation == 'restore':  # Restoring backup
            file_check = curr_db_name + '__'
            existing_backups = [f for f in files_in_backup_dir if file_check in f]
            existing_backups.sort(key=lambda x: x.casefold(), reverse=True)
            if existing_backups:
                choose_backup = generic_entry_window.GenericDropWindow('restore backup', existing_backups,
                                                                       label_2_text=curr_db_name)
                if choose_backup.exec_():
                    copyfile(os.getcwd() + '\\db_files\\backups\\' + choose_backup.drop.currentText(), curr_db_fpath)
                    backup_restored_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Backup restored',
                                                                'Selected backup has been restored.')
                    backup_restored_win.exec_()

            else:
                no_backups_exist_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'No backups exist',
                                                             'No backups have been created for this\n'
                                                             'database. No action has been taken.')
                no_backups_exist_win.exec_()

        elif operation == 'create':  # Creating backup
            if (backup_db_name + '.db') in files_in_backup_dir:
                file_exists_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question, 'Backup exists',
                                                        'A backup created today for this database already exists.\n'
                                                        'Would you like to overwrite the existing backup?',
                                                        QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
                if file_exists_win.exec_() == QtWidgets.QMessageBox.Yes:
                    copyfile(curr_db_fpath, new_backup_fpath)

                    backup_created_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Backup created',
                                                               'Existing backup file has been overwritten.')
                    backup_created_win.exec_()

            else:
                copyfile(curr_db_fpath, new_backup_fpath)
                backup_created_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Backup created',
                                                           'Backup file has been created.')
                backup_created_win.exec_()

        elif operation == 'delete':  # Deleting existing backup files
            del_backups_win = checkbox_list_window.CheckboxListWindow('del backups', files_in_backup_dir)
            if del_backups_win.exec_():
                if not del_backups_win.get_checked_boxes():
                    no_backups_sel_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Nothing selected',
                                                               'No files selected. No action has been taken.')
                    no_backups_sel_win.exec_()

                else:
                    for backup in del_backups_win.get_checked_boxes():
                        os.remove(os.getcwd() + '\\db_files\\backups\\' + backup)
                    backups_deleted_succ = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Completed',
                                                                 'Selected backup files have been deleted.')
                    backups_deleted_succ.exec_()

        backup_conn.close()

    def import_custom_lists(self):
        import_cl_conn = sqlite3.connect(common_vars.video_db())
        import_cl_cursor = import_cl_conn.cursor()
        import_cl_cursor.execute('SELECT list_name FROM custom_lists')
        list_of_cls = [x[0].casefold() for x in import_cl_cursor.fetchall()]

        import_expl_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Import Custom Lists',
                                                'This function is used to import any Custom Lists created in a\n'
                                                'previous version of AMV Tracker. After clicking "OK", locate\n'
                                                'the file in the directory of the old version of AMV Tracker\n'
                                                'called "cust_lists.p". AMV Tracker will then import all the\n'
                                                'Custom List data automatically.\n\n'
                                                'If there are any conflicts between the name of an old Custom\n'
                                                'List and one that you\'ve created here, AMV Tracker will append\n'
                                                '"-old ver" to the imported Custom List. You can then rename it\n'
                                                'using AMV Tracker\'s "Rename Custom List" function.',
                                                QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
        if import_expl_win.exec_() == import_expl_win.Ok:
            fpath = QtWidgets.QFileDialog.getOpenFileName(self, 'Locate cust_lists.p', '', '.p file (*cust_lists.p)')[0]
            if fpath:
                infile = open(fpath, 'rb')
                old_cl_dict = pickle.load(infile)
                infile.close()

                for key, val in old_cl_dict.items():
                    cl_id = common_vars.id_generator('cust list')
                    if key.casefold() in list_of_cls:
                        key += '-old ver'
                    vid_ids = '; '.join(val)
                    import_cl_cursor.execute('INSERT OR IGNORE INTO custom_lists VALUES (?, ?, ?)',
                                             (cl_id, key, vid_ids))

                import_cl_conn.commit()
                cl_import_success_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Import complete',
                                                              'Custom Lists have successfully been imported.')
                cl_import_success_win.exec_()

        import_cl_conn.close()

    def cust_list_ops(self, operation):
        cl_conn = sqlite3.connect(common_vars.video_db())
        cl_cursor = cl_conn.cursor()
        cl_cursor.execute('SELECT list_name FROM custom_lists')
        list_of_cls = [x[0] for x in cl_cursor.fetchall()]
        list_of_cls.sort(key=lambda x: x.casefold())

        if operation == 'rename':  # Rename existing Custom List
            rename_cl_win = generic_entry_window.GenericEntryWindowWithDrop('rename', list_of_cls,
                                                                            inp_str1='Custom List',
                                                                            dupe_list=list_of_cls)
            if rename_cl_win.exec_():
                sel_cl_id = common_vars.custom_list_lookup()[rename_cl_win.drop.currentText()]
                cl_cursor.execute('UPDATE custom_lists SET list_name = ? WHERE cl_id = ?',
                                  (rename_cl_win.textBox.text(), sel_cl_id))
                cl_conn.commit()

                cl_renamed_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Custom List renamed',
                                                       'Custom List [{}] successfully renamed to [{}].'
                                                       .format(rename_cl_win.drop.currentText(),
                                                               rename_cl_win.textBox.text()))
                cl_renamed_win.exec_()

        elif operation == 'add':  # Add new Custom List
            new_cl_win = generic_entry_window.GenericEntryWindow('new_cl', dupe_check_list=list_of_cls)
            if new_cl_win.exec_():
                new_cl_id = common_vars.id_generator('cust list')
                new_cl_name = new_cl_win.textBox.text()
                cl_cursor.execute('INSERT OR IGNORE INTO custom_lists VALUES (?, ?, ?)',
                                  (new_cl_id, new_cl_name, ''))
                cl_conn.commit()

                cl_added_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Custom List added',
                                                     'Custom List [{}] has been created.'.format(new_cl_name))
                cl_added_win.exec_()

        elif operation == 'delete':
            del_cl_win = checkbox_list_window.CheckboxListWindow('del cust lists', list_of_cls)
            if del_cl_win.exec_():
                if len(del_cl_win.get_checked_boxes()) == 0:
                    nothing_selected = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Nothing selected',
                                                             'No custom lists were selected, therefore no\n'
                                                             'action has been taken.')
                    nothing_selected.exec_()

                else:
                    for cbox in del_cl_win.get_checked_boxes():
                        cl_cursor.execute('DELETE FROM custom_lists WHERE list_name = ?', (cbox,))

                    cl_conn.commit()
                    cl_del_succ_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Success',
                                                            'The selected Custom List(s) have been deleted.')
                    cl_del_succ_win.exec_()

        cl_conn.close()
