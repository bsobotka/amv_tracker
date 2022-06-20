import os
import datetime
import sqlite3

from random import randint


def sqlite_queries(query_type):
	if query_type == 'create table':
		query = 'CREATE TABLE IF NOT EXISTS "sub_db_{}" (	"video_id"	,"primary_editor_username"	TEXT, ' \
				'"primary_editor_pseudonyms"	TEXT, "addl_editors"	TEXT, "studio"	TEXT, "video_title"	TEXT,' \
				'"release_date"	TEXT, "release_date_unknown"  INTEGER, "star_rating"	REAL, ' \
				'"video_footage"	TEXT, "song_artist"	TEXT, ' \
				'"song_title"	TEXT, "song_genre"	TEXT, "video_length"	INTEGER, "contests_entered"	TEXT,' \
				'"awards_won"	TEXT, "video_description"	TEXT, "my_rating"	REAL, "notable"	INTEGER, ' \
				'"favorite"	INTEGER, "tags_1"	TEXT, "tags_2"	TEXT, "tags_3"	TEXT, "tags_4"	TEXT, ' \
				'"tags_5"	TEXT, "tags_6"	TEXT, "comments"	TEXT, "video_youtube_url"	TEXT, ' \
				'"video_org_url"	TEXT, "video_amvnews_url"	TEXT, "video_other_url"	TEXT, "local_file"	TEXT, ' \
				'"editor_youtube_channel_url"	TEXT, "editor_org_profile_url"	TEXT, ' \
				'"editor_amvnews_profile_url"	TEXT, "editor_other_profile_url"	TEXT, "sequence"	INTEGER, ' \
				'"date_entered"	TEXT, "play_count"	INTEGER, "vid_thumb_path" TEXT, "sub_db" TEXT, PRIMARY KEY("video_id"))'

	else:
		query = 'check your inputs'

	return query


def year_plus_one():
	"""
	Returns int indicating next year.
    :return: Int -> current year + 1
    """
	next_year = int(datetime.datetime.now().year) + 1
	return next_year


def current_date():
	"""
	:return: Current date as a string --> YYYY/MM/DD
	"""
	now = datetime.datetime.now()
	yr = str(now.year)
	if now.month < 10:
		mon = '0' + str(now.month)
	else:
		mon = str(now.month)

	if now.day < 10:
		day = '0' + str(now.day)
	else:
		day = str(now.day)

	today = yr + '/' + mon + '/' + day
	return today


def settings_db():
	"""
	Function used to return Entry Field DB.
	"""
	path_to_entry_field_db = os.getcwd() + '\\db_files\\settings.db'
	return path_to_entry_field_db


def video_db():
	"""
	:return: String pointing to active db location
	"""

	conn = sqlite3.connect(settings_db())
	cursor = conn.cursor()
	cursor.execute('SELECT path_to_db FROM db_settings WHERE active_db = ?', (1,))

	return cursor.fetchone()[0]


def video_table_lookup():
	"""
	:return: Sub-db lookup dictionary --> {user_friendly_name : internal_db_name}
	"""
	video_db_file = video_db()
	conn = sqlite3.connect(video_db_file)
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM db_name_lookup')
	lookup = cursor.fetchall()

	sub_db_lookup_dict = {}
	for pair in lookup:
		sub_db_lookup_dict[pair[1]] = pair[0]

	return sub_db_lookup_dict


def tag_db():
	"""
	Function used to return tag database.
	"""

	# Note: Retaining this function (even though it is redundant) for the sake of readability through the rest of AMV
	# Tracker

	return video_db()


def sub_db_lookup(reverse=False):
	"""
	:return: db name lookup dictionary --> {user_friendly_name : internal_db_name}
			 If reverse is True --> {internal_db_name : user_friendly_name}
	"""
	my_database = video_db()

	conn = sqlite3.connect(my_database)
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM db_name_lookup')
	lookup = cursor.fetchall()

	subdb_table_lookup_dict = {}
	if reverse:
		for lookup_pair in lookup:
			subdb_table_lookup_dict[lookup_pair[0]] = lookup_pair[1]
	else:
		for lookup_pair in lookup:
			subdb_table_lookup_dict[lookup_pair[1]] = lookup_pair[0]

	return subdb_table_lookup_dict


def tag_table_lookup(reverse=False):
	"""
	:return: Tag table lookup dictionary --> {user_friendly_name : internal_db_name}
			 If reverse is True --> {internal_db_name : user_friendly_name}
	"""

	tag_db = video_db()

	conn = sqlite3.connect(tag_db)
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM tags_lookup')
	lookup = cursor.fetchall()

	tag_table_lookup_dict = {}
	if reverse:
		for lookup_pair in lookup:
			tag_table_lookup_dict[lookup_pair[0]] = lookup_pair[1]
	else:
		for lookup_pair in lookup:
			tag_table_lookup_dict[lookup_pair[1]] = lookup_pair[0]

	return tag_table_lookup_dict


def thumb_path():
	"""
	:return: Thumbnail path (string)
	"""
	vid_db = video_db()

	conn = sqlite3.connect(vid_db)
	cursor = conn.cursor()
	cursor.execute('SELECT value FROM misc_settings WHERE setting_name = ?', ('thumbnail_path',))
	th_path = cursor.fetchone()[0]

	return th_path


def tag_group_w_tag_names(k):
	"""
	:param k: str --> 'user' or 'internal'
	:return: If k == 'user' --> {tag_group_user_name_1 : [list_of_tags]...}
			 If k == 'internal' --> {tag_group_internal_name_1 : [list_of_tags]...}
	"""
	tag_db = video_db()
	conn = sqlite3.connect(tag_db)
	cursor = conn.cursor()

	tag_table_dict = tag_table_lookup()
	output_dict = {}
	for key, val in tag_table_dict.items():
		cursor.execute('SELECT tag_name FROM {}'.format(val))
		if k == 'user':
			output_dict[key] = [x[0] for x in cursor.fetchall()]
		else:
			output_dict[val] = [x[0] for x in cursor.fetchall()]

	return output_dict


def tag_desc_lookup(tag_table):
	"""
	:param tag_table: User-friendly tag table name to be accessed.
	:return: Tag desc lookup dict --> {tag_1_name : tag_1_description, tag_2_name : tag_2_description...}
	"""
	tag_db = video_db()

	tag_table_name = tag_table_lookup()[tag_table]

	conn = sqlite3.connect(tag_db)
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM {}'.format(tag_table_name))
	lookup = cursor.fetchall()

	tag_desc_lookup_dict = {}
	for lookup_pair in lookup:
		tag_desc_lookup_dict[lookup_pair[0]] = lookup_pair[1]

	return tag_desc_lookup_dict


def video_field_lookup(reverse=True, filt=None, filt_val=1):
	"""
	:return: Video field lookup dict --> {internal_name : user_friendly_name}
			 If reverse is True --> {user_friendly_name : internal_name}
	"""

	conn = sqlite3.connect(os.getcwd() + '\\db_files\\settings.db')
	cursor = conn.cursor()
	if filt:
		cursor.execute('SELECT field_name_display, field_name_internal FROM search_field_lookup WHERE {} = ?'
					   .format(filt), (filt_val,))
	else:
		cursor.execute('SELECT field_name_display, field_name_internal FROM search_field_lookup')

	if reverse:
		lookup_dict = {k: v for (k, v) in cursor.fetchall()}
	else:
		lookup_dict = {v: k for (k, v) in cursor.fetchall()}

	return lookup_dict


def custom_list_lookup(reverse=True):
	"""
	:return:  Custom List lookup dict --> {user_friendly_name : cl_id}
			  If reverse is True --? {cl_id : user_friendly_name}
	"""
	db = video_db()
	conn = sqlite3.connect(db)
	cursor = conn.cursor()
	cursor.execute('SELECT cl_id, list_name FROM custom_lists')

	if reverse:
		lookup_dict = {v: k for (k, v) in cursor.fetchall()}
	else:
		lookup_dict = {k: v for (k, v) in cursor.fetchall()}

	return lookup_dict


def get_all_vid_info(subdb_int, vidid):
	"""
	:param subdb_int: Internal sub-db name
	:param vidid: Video ID
	:return: Dict with all video info: {field_name: field_value}
	"""
	get_info_conn = sqlite3.connect(video_db())
	get_info_cursor = get_info_conn.cursor()
	get_info_cursor.execute('SELECT * FROM {} WHERE video_id = ?'.format(subdb_int), (vidid,))
	vid_tup = get_info_cursor.fetchone()
	vid_dict = {
		'video_id': vid_tup[0],
		'primary_editor_username': vid_tup[1],
		'primary_editor_pseudonyms': vid_tup[2],
		'addl_editors': vid_tup[3],
		'studio': vid_tup[4],
		'video_title': vid_tup[5],
		'release_date': vid_tup[6],
		'release_date_unknown': vid_tup[7],
		'star_rating': vid_tup[8],
		'video_footage': vid_tup[9],
		'song_artist': vid_tup[10],
		'song_title': vid_tup[11],
		'song_genre': vid_tup[12],
		'video_length': vid_tup[13],
		'contests_entered': vid_tup[14],
		'awards_won': vid_tup[15],
		'video_description': vid_tup[16],
		'my_rating': vid_tup[17],
		'notable': vid_tup[18],
		'favorite': vid_tup[19],
		'tags_1': vid_tup[20],
		'tags_2': vid_tup[21],
		'tags_3': vid_tup[22],
		'tags_4': vid_tup[23],
		'tags_5': vid_tup[24],
		'tags_6': vid_tup[25],
		'comments': vid_tup[26],
		'video_youtube_url': vid_tup[27],
		'video_org_url': vid_tup[28],
		'video_amvnews_url': vid_tup[29],
		'video_other_url': vid_tup[30],
		'local_file': vid_tup[31],
		'editor_youtube_channel_url': vid_tup[32],
		'editor_org_profile_url': vid_tup[33],
		'editor_amvnews_profile_url': vid_tup[34],
		'editor_other_profile_url': vid_tup[35],
		'sequence': vid_tup[36],
		'date_entered': vid_tup[37],
		'play_count': vid_tup[38],
		'vid_thumb_path': vid_tup[39],
		'sub_db': vid_tup[40]
	}
	return vid_dict


def entry_dict():
	"""
	:return: dict with all internal field names for video db as keys and empty or zero values
	"""

	out_dict = {
		'video_id': '',
		'primary_editor_username': '',
		'primary_editor_pseudonyms': '',
		'addl_editors': '',
		'studio': '',
		'video_title': '',
		'release_date': '',
		'release_date_unknown': 0,
		'star_rating': '',
		'video_footage': '',
		'song_artist': '',
		'song_title': '',
		'song_genre': '',
		'video_length': '',
		'contests_entered': '',
		'awards_won': '',
		'video_description': '',
		'my_rating': '',
		'notable': 0,
		'favorite': 0,
		'tags_1': '',
		'tags_2': '',
		'tags_3': '',
		'tags_4': '',
		'tags_5': '',
		'tags_6': '',
		'comments': '',
		'video_youtube_url': '',
		'video_org_url': '',
		'video_amvnews_url': '',
		'video_other_url': '',
		'local_file': '',
		'editor_youtube_channel_url': '',
		'editor_org_profile_url': '',
		'editor_amvnews_profile_url': '',
		'editor_other_profile_url': '',
		'sequence': '',
		'date_entered': '',
		'play_count': 0,
		'vid_thumb_path': '',
		'sub_db': ''
	}

	return out_dict


def max_sequence_dict(internal=False):
	"""
	:param internal: If True, will return a dict --> {subdb1_internal_name: max_sequence...}
	                 If False, will return a dict --> {subdb1_friendly_name: max_sequence...}
	:return: {subdb: max_sequence}
	"""
	max_seq_conn = sqlite3.connect(video_db())
	max_seq_cursor = max_seq_conn.cursor()
	subdbs = sub_db_lookup()
	output_dict = dict()

	for k, v in subdbs.items():
		max_seq_cursor.execute('SELECT COUNT(*) FROM {}'.format(v))
		num_rows = max_seq_cursor.fetchone()[0]
		if num_rows == 0:
			sequence = 1
		else:
			sequence = num_rows + 1

		if internal:
			output_dict[v] = sequence
		else:
			output_dict[k] = sequence

	return output_dict


def obtain_subdb_dict():
	"""
	:return: Dictionary --> {vidid_1: sub_db, vidid_2: sub_db...}
	"""
	get_subdb_conn = sqlite3.connect(video_db())
	get_subdb_cursor = get_subdb_conn.cursor()
	list_of_subdbs = [v for k, v in sub_db_lookup().items()]
	sdb_dict = dict()

	for sdb in list_of_subdbs:
		get_subdb_cursor.execute('SELECT video_id, sub_db FROM {}'.format(sdb))
		for tup in get_subdb_cursor.fetchall():
			if tup[0] not in sdb_dict:
				sdb_dict[tup[0]] = tup[1]

	get_subdb_conn.close()
	return sdb_dict


def id_generator(id_type):
	def gen():
		if id_type == 'video':
			prefix = ''
		elif id_type == 'cust list':
			prefix = 'CL_'
		elif id_type == 'CTLR':
			prefix = 'CTLR_'
		else:
			prefix = ''

		id_final = prefix
		for dig in range(0, 10):
			rand_list = [str(randint(0, 9)), chr(randint(65, 90)), chr(randint(97, 122))]
			id_final += rand_list[randint(0, 2)]

		return id_final

	generator_conn = sqlite3.connect(video_db())
	generator_cursor = generator_conn.cursor()

	list_of_subdbs = [v for k, v in sub_db_lookup().items()]
	list_of_vidids = []
	for subdb in list_of_subdbs:
		generator_cursor.execute('SELECT video_id FROM {}'.format(subdb))
		for v_id in generator_cursor.fetchall():
			list_of_vidids.append(v_id)

	generator_cursor.execute('SELECT cl_id FROM custom_lists')
	list_of_cl_ids = [x[0] for x in generator_cursor.fetchall()]

	new_id = gen()
	if id_type == 'video':
		while new_id in list_of_vidids:
			new_id = gen()
		else:
			return new_id

	else:
		while new_id in list_of_cl_ids:
			new_id = gen()
		else:
			return new_id
