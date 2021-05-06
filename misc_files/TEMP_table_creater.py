import sqlite3
from amvtracker.misc_files import common_vars

def table_creator():
	vid_db = common_vars.video_db()
	conn = sqlite3.connect('C:\\Users\\Ben\Dropbox\\AMV Tracker source (v2)\\AMVTracker-2.0.0\\amvtracker\\db_files\\my_database.db')
	cursor = conn.cursor()

	cursor.execute('CREATE TABLE IF NOT EXISTS "sub_db_3" (	"video_id"	,"primary_editor_username"	TEXT,'
	               '"primary_editor_pseudonyms"	TEXT, "addl_editors"	TEXT, "studio"	TEXT, "video_title"	TEXT,'
	               '"release_date"	TEXT, "star_rating"	REAL, "video_footage"	TEXT, "song_artist"	TEXT,'
	               '"song_title"	TEXT, "song_genre"	TEXT, "video_length"	INTEGER, "contests_entered"	TEXT,'
	               '"awards_won"	TEXT, "video_description"	TEXT, "my_rating"	REAL, "notable"	INTEGER, '
	               '"favorite"	INTEGER, "tags_1"	TEXT, "tags_2"	TEXT, "tags_3"	TEXT, "tags_4"	TEXT, '
	               '"tags_5"	TEXT, "tags_6"	TEXT, "comments"	TEXT, "video_youtube_url"	TEXT, '
	               '"video_org_url"	TEXT, "video_amvnews_url"	TEXT, "video_other_url"	TEXT, "local_file"	TEXT, '
	               '"editor_youtube_channel_url"	TEXT, "editor_org_profile_url"	TEXT, '
	               '"editor_amvnews_profile_url"	TEXT, "editor_other_profile_url"	TEXT, "sequence"	INTEGER, '
	               '"date_entered"	TEXT, PRIMARY KEY("video_id"))')

	cursor.close()

table_creator()