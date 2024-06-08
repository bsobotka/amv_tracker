import PyQt5.QtWidgets as QtWidgets
import sqlite3
import os

from misc_files import common_vars
from settings import data_management_settings


class SelectOrImport(QtWidgets.QMessageBox):
	def __init__(self):
		super(SelectOrImport, self).__init__()

		self.setWindowTitle('Select DB file or import')
		self.setText('Hello! It looks like this is your first time running AMV Tracker. Before you get started,\n'
					 'you will need to select your working database. You have four options:\n\n'
					 '\u2022 Use the ready-made "my_database.db" file, located in the AMV Tracker/db_files\n'
					 'directory\n'
					 '\u2022 Create and name a new database file\n'
					 '\u2022 Import a database created in a pre-v2 version of AMV Tracker\n'
					 '\u2022 If you have used AMV Tracker v2 before and you are still seeing this message, you can\n'
					 'select it here\n\n'
					 'What would you like to do?')

		self.addButton(QtWidgets.QPushButton('Use my_database.db'), QtWidgets.QMessageBox.YesRole)
		self.addButton(QtWidgets.QPushButton('Create new database'), QtWidgets.QMessageBox.YesRole)
		self.addButton(QtWidgets.QPushButton('Import pre-v2 DB'), QtWidgets.QMessageBox.YesRole)
		self.addButton(QtWidgets.QPushButton('Use existing database'), QtWidgets.QMessageBox.YesRole)


def check_for_db():
	db_check_conn = sqlite3.connect(common_vars.settings_db())
	db_check_cursor = db_check_conn.cursor()
	db_check_cursor.execute('SELECT path_to_db FROM db_settings')
	fname = db_check_cursor.fetchone()[0]

	if fname == '':  # First launch
		select_or_import_win = SelectOrImport().exec_()

		if select_or_import_win == 0:  # Use my_database.db
			db_check_cursor.execute('UPDATE db_settings SET path_to_db = ?, db_name = ?, active_db = 1',
									(os.getcwd() + '\\db_files\\my_database.db', 'my_database'))
			db_check_conn.commit()

			new_db_conn = sqlite3.connect(common_vars.video_db())
			new_db_cursor = new_db_conn.cursor()
			new_thumb_dir = os.getcwd() + '\\thumbnails\\my_database'
			if not os.path.isdir(new_thumb_dir):
				os.makedirs(new_thumb_dir)

			new_db_cursor.execute('UPDATE misc_settings SET value = ? WHERE setting_name = "thumbnail_path"',
								  (new_thumb_dir,))
			new_db_conn.commit()
			new_db_conn.close()

		elif select_or_import_win == 1:  # Create a new DB
			select_dir = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Select directory',
											   'Please select the directory in which you would like to create\n'
											   'the new database.')
			if select_dir.exec_():
				data_management_settings.DataMgmtSettings().create_db()

		elif select_or_import_win == 2:  # Import from pre-v2
			data_management_settings.DataMgmtSettings().import_btn_clicked()

		else:  # Use existing db file
			data_management_settings.DataMgmtSettings().select_db()

	elif not os.path.isfile(fname):
		no_db_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'DB does not exist',
		                                  'No database is currently set. Please select a .db file\n'
		                                  'to set as the current working database.')
		if no_db_win.exec_():
			data_management_settings.DataMgmtSettings().select_db()

	db_check_conn.close()
