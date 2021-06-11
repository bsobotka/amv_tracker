import os
import datetime
import sqlite3


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
		        '"date_entered"	TEXT, PRIMARY KEY("video_id"))'

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


def video_field_lookup(reverse=True):
	"""
	:return: Video field lookup dict --> {user_friendly_name : internal_name}
			 If reverse is True --> {internal_name : user_friendly_name}
	"""

	conn = sqlite3.connect(os.getcwd() + '\\db_files\\settings.db')
	cursor = conn.cursor()
	cursor.execute('SELECT field_name_display, field_name_internal FROM search_field_lookup')
	if reverse:
		lookup_dict = {k: v for (k, v) in cursor.fetchall()}
	else:
		lookup_dict = {v: k for (k, v) in cursor.fetchall()}

	return lookup_dict

