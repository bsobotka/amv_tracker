import sqlite3
import xlrd


def convert():
	book = xlrd.open_workbook('db.xls')
	conn = sqlite3.connect('test_database.db')
	cursor = conn.cursor()

	cursor.execute('CREATE TABLE IF NOT EXISTS db_name_lookup (table_name      PRIMARY KEY,\
	                                             user_subdb_name TEXT         NOT NULL)')

	for sub_db_ind in range(0, book.nsheets):
		sheet = book.sheet_by_index(sub_db_ind)
		tn = 'sub_db_{}'.format(sub_db_ind)

		cursor.execute("CREATE TABLE IF NOT EXISTS sub_db_{} (Video_ID PRIMARY KEY, Editor TEXT, Video_Title TEXT, My_Rating REAL, \
		Star_Rating REAL, Genres TEXT, Date_released TEXT, Anime TEXT, Artist TEXT, Song_title TEXT, Song_genre TEXT, \
		Duration INT, General_tags TEXT, FX_Tags TEXT, Comments TEXT, URL TEXT, Pseudonyms TEXT, \
		Local_file TEXT, Contests TEXT, Sequence INT, Date_entered TEXT)".format(sub_db_ind))

		cursor.execute('INSERT OR IGNORE INTO db_name_lookup (table_name, user_subdb_name) VALUES (?, ?)', (tn, sheet.name))

		for row in range(1, sheet.nrows):
			vid_info = (sheet.cell_value(row, 18),)
			for col in range(0, sheet.ncols):
				if col == 5:
					if sheet.cell_value(row, col) != '?':
						date = xlrd.xldate_as_tuple(sheet.cell_value(row, col), 0)
						yr = str(date[0])
						if len(str(date[1])) == 1:
							mo = '0'+str(date[1])
						else:
							mo = str(date[1])
						date_formatted = yr + '-' + mo
						vid_info += (date_formatted,)
					else:
						vid_info += ('?',)

				elif col != 18:
					vid_info += (sheet.cell_value(row, col),)
			cursor.execute('INSERT OR IGNORE INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,\
			               ?, ?, ?, ?, ?, ?)'.format(tn), vid_info)

	conn.commit()
	conn.close()


convert()
