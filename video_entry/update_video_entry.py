import sqlite3

from misc_files import common_vars


def update_video_entry(inp_dict, tables, seq_dict=None, custom_lists=None, vid_id=None):
	"""
	:param inp_dict: Dictionary containing all table fields and corresponding values
	:param tables: List of tables (friendly sub-DB names) that the video is going into
	:param seq_dict: {subdb_name_internal: max sequence number}
	:param custom_lists:
	:param vid_id: Video ID, if entry is being updated
	"""
	video_db = common_vars.video_db()
	conn = sqlite3.connect(video_db)
	cursor = conn.cursor()
	tables_internal = [val for key, val in common_vars.video_table_lookup().items() if key in tables]

	if vid_id:  # This is an update to an existing entry
		for k, v in inp_dict.items():
			cursor.execute('UPDATE {} SET {} = ? WHERE video_id = ?'.format(tables_internal[0], k), (v, vid_id))

	else:  # This is a new entry into the database
		for table_name in tables_internal:
			unique_vidid = common_vars.id_generator('video')
			inp_dict['video_id'] = unique_vidid
			if seq_dict:
				inp_dict['sequence'] = seq_dict[table_name]
			update_list = [val for key, val in inp_dict.items()]
			cursor.execute('INSERT OR IGNORE INTO {tn} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '
			               '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
			               .format(tn=table_name), update_list)

	if custom_lists:  # TODO: Video needs to be added to custom list(s)
		pass

	conn.commit()
	conn.close()
