import PyQt5.QtWidgets as QtWidgets
import sqlite3
import os

from misc_files import common_vars
from settings import data_management_settings


def check_for_db():
	db_check_conn = sqlite3.connect(common_vars.settings_db())
	db_check_cursor = db_check_conn.cursor()
	db_check_cursor.execute('SELECT path_to_db FROM db_settings')
	fname = db_check_cursor.fetchone()[0]

	if not os.path.isfile(fname):
		no_db_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'DB does not exist',
		                                  'No database is currently set. Please select a .db file\n'
		                                  'to set as the current working database.')
		if no_db_win.exec_():
			data_management_settings.DataMgmtSettings().select_db()