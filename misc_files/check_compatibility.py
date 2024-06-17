import sqlite3
import xlrd


def is_compatible(db_type, inp_file_path):
	if inp_file_path:
		if db_type == 'sqlite':
			conn = sqlite3.connect(inp_file_path)
			cursor = conn.cursor()
			cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
			list_of_tables = [x[0] for x in cursor.fetchall()]
			if 'sub_db_0' in list_of_tables and 'tags_1' in list_of_tables and 'db_name_lookup' in list_of_tables:
				compatible = True
			else:
				compatible = False

			conn.close()

		else:
			book = xlrd.open_workbook(inp_file_path)
			sheet = book.sheet_by_index(0)
			list_of_col_names = [sheet.cell_value(0, col) for col in range(0, sheet.ncols)]
			if len(list_of_col_names) == 21 and 'Sequence' in list_of_col_names and 'Date entered (Y/M/D)' in list_of_col_names:
				compatible = True
			else:
				compatible = False

		return compatible
