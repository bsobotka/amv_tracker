import sqlite3

from misc_files import common_vars


def update_video_entry(inp_dict, tables, seq_dict, custom_lists=None, vid_id=None):
	video_db = common_vars.video_db()
	conn = sqlite3.connect(video_db)
	cursor = conn.cursor()
	tables_internal = [val for key, val in common_vars.video_table_lookup().items() if key in tables]

	if vid_id:  # This is an update to an existing entry
		pass
	else:  # This is a new entry into the database
		for table_name in tables_internal:
			inp_dict['sequence'] = seq_dict[table_name]
			update_list = [val for key, val in inp_dict.items()]
			cursor.execute('INSERT OR IGNORE INTO {tn} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '
			               '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
			               .format(tn=table_name), update_list)

	if custom_lists:  # Video needs to be added to custom list(s)
		pass

	conn.commit()
	conn.close()
