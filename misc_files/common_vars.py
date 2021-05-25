import os
import datetime
import sqlite3


def year_plus_one():
	"""
	    Returns int indicating next year.
	    :return: Int -> current year + 1
	    """

	next_year = int(datetime.datetime.now().year) + 1
	return next_year


"""def video_db():
	
	#Function used to return video database.
	
	path_to_video_db = os.getcwd() + '\\db_files\\my_database.db'
	return path_to_video_db"""


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
	#tag_db = os.path.dirname(os.getcwd()) + '\\db_files\\tag_db.db'
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
