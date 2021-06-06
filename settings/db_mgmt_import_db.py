import xlrd
import sqlite3

from misc_files import common_vars


def Import_DB(f_path, type):
	conn = sqlite3.connect(common_vars.video_db())
	cursor = conn.cursor()

	if type == 'amvt':  # Old AMV Tracker version database
		book = xlrd.open_workbook(f_path)
		create_table_query = common_vars.sqlite_queries('create table')

		# Check that selected spreadsheet is compatible
		# TODO: Check that spreadsheet chosen is compatible

		# Move data
		for sht_ind in range(0, book.nsheets):
			sheet = book.sheet_by_index(sht_ind)
			tn = 'sub_db_{}'.format(sht_ind)

			cursor.execute(create_table_query.format(sht_ind))

			cursor.execute('INSERT OR IGNORE INTO db_name_lookup (table_name, user_subdb_name) VALUES (?, ?)',
			               (tn, sheet.name))

			for row in range(1, sheet.nrows):
				field_dict = {}
				field_dict['video_org_url'] = None
				field_dict['video_youtube_url'] = None
				field_dict['video_amvnews_url'] = None
				field_dict['video_other_url'] = None

				field_dict['primary_editor_username'] = str(sheet.cell_value(row, 0))
				field_dict['video_title'] = str(sheet.cell_value(row, 1))
				field_dict['my_rating'] = float(sheet.cell_value(row, 2))
				field_dict['star_rating'] = float(sheet.cell_value(row, 3))
				field_dict['tags_1'] = str(sheet.cell_value(row, 4)).replace(', ', '; ').lower()
				if str(sheet.cell_value(row, 5)) == '?':
					field_dict['release_date'] = ''
					field_dict['release_date_unknown'] = 1
				else:
					rel_date = xlrd.xldate_as_datetime(int(sheet.cell_value(row, 5)), 0).isoformat()[:7]
					field_dict['release_date'] = rel_date
					field_dict['release_date_unknown'] = 0
				field_dict['video_footage'] = str(sheet.cell_value(row, 6)).replace(' // ', '; ')
				field_dict['song_artist'] = str(sheet.cell_value(row, 7))
				field_dict['song_title'] = str(sheet.cell_value(row, 8))
				field_dict['song_genre'] = str(sheet.cell_value(row, 9))
				if str(sheet.cell_value(row, 10)) == '':
					field_dict['video_length'] = ''
				else:
					field_dict['video_length'] = int(sheet.cell_value(row, 10))
				field_dict['tags_2'] = str(sheet.cell_value(row, 11)).replace(', ', '; ').lower()
				field_dict['tags_3'] = str(sheet.cell_value(row, 12)).replace(', ', '; ').lower()
				field_dict['comments'] = str(sheet.cell_value(row, 13))
				if 'animemusicvideos.org' in str(sheet.cell_value(row, 14)):
					field_dict['video_org_url'] = str(sheet.cell_value(row, 14))
				elif 'yout' in str(sheet.cell_value(row, 14)):
					field_dict['video_youtube_url'] = str(sheet.cell_value(row, 14))
				elif 'amvnews' in str(sheet.cell_value(row, 14)):
					field_dict['video_amvnews_url'] = str(sheet.cell_value(row, 14))
				else:
					field_dict['video_other_url'] = str(sheet.cell_value(row, 14))
				field_dict['primary_editor_pseudonyms'] = str(sheet.cell_value(row, 15)).replace(', ', '; ')
				field_dict['local_file'] = str(sheet.cell_value(row, 16))
				field_dict['contests_entered'] = str(sheet.cell_value(row, 17))
				field_dict['video_id'] = str(sheet.cell_value(row, 18))
				if str(sheet.cell_value(row, 19)) == '':
					field_dict['sequence'] = ''
				else:
					field_dict['sequence'] = int(sheet.cell_value(row, 19))
				field_dict['date_entered'] = str(sheet.cell_value(row, 20))
				field_dict['notable'] = 0
				field_dict['favorite'] = 0

				cursor.execute('INSERT OR IGNORE INTO sub_db_{} (video_id) VALUES (?)'.format(sht_ind),
				               (field_dict['video_id'],))
				conn.commit()

				cursor.execute('UPDATE sub_db_{} SET (primary_editor_username, video_title, my_rating, star_rating, '
				               'tags_1, release_date, release_date_unknown, video_footage, song_artist, song_title, '
				               'song_genre, video_length, tags_2, tags_3, comments, video_org_url, video_youtube_url, '
				               'video_amvnews_url, video_other_url, primary_editor_pseudonyms, local_file, '
				               'contests_entered, sequence, date_entered, notable, favorite) = (?, ?, ?, ?, ?, ?, ?, '
				               '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) WHERE video_id = ?'.format(
					sht_ind), (field_dict['primary_editor_username'], field_dict['video_title'], field_dict[
					'my_rating'], field_dict['star_rating'], field_dict['tags_1'], field_dict['release_date'],
				               field_dict['release_date_unknown'], field_dict['video_footage'], field_dict[
					                                              'song_artist'], field_dict['song_title'],
				               field_dict['song_genre'], field_dict['video_length'], field_dict['tags_2'], field_dict[
					                                              'tags_3'], field_dict['comments'], field_dict[
					                                              'video_org_url'], field_dict['video_youtube_url'],
				               field_dict['video_amvnews_url'], field_dict['video_other_url'], field_dict[
					                                              'primary_editor_pseudonyms'], field_dict[
					                                              'local_file'], field_dict['contests_entered'],
				               field_dict['sequence'], field_dict['date_entered'], field_dict['notable'], field_dict[
					                                              'favorite'], field_dict['video_id']))

		conn.commit()
		conn.close()

	else:  # CSV document
		print('csv')