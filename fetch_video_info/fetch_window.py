import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import requests
import sqlite3

from os import getcwd
from pytube import Channel, Playlist, YouTube

from bs4 import BeautifulSoup as beautifulsoup
from fetch_video_info import failed_fetches, fetch_vid_info
from misc_files import common_vars, download_yt_thumb
from video_entry import update_video_entry


class AddToCustomList(QtWidgets.QDialog):
	def __init__(self, vidid_list, mass_add=False):
		super(AddToCustomList, self).__init__()

		atcl_conn = sqlite3.connect(common_vars.video_db())
		atcl_cursor = atcl_conn.cursor()
		atcl_cursor.execute('SELECT * FROM custom_lists')

		self.vididList = vidid_list
		self.mass_add = mass_add
		self.custLists = atcl_cursor.fetchall()
		self.custListNames = [x[1] for x in self.custLists]
		self.custListNames.sort(key=lambda x: x.casefold())

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayout = QtWidgets.QHBoxLayout()

		if self.mass_add:
			label_text = 'Please select the custom list you would like to\nadd these videos to.'
			btn_text = 'Back'
		else:
			label_text = 'If you would like to add these videos to an existing custom list, please\nchoose it below.'
			btn_text = 'Skip'

		self.label = QtWidgets.QLabel()
		self.label.setText(label_text)

		self.custListDrop = QtWidgets.QComboBox()
		self.custListDrop.setFixedWidth(260)
		for name in self.custListNames:
			self.custListDrop.addItem(name)

		self.skipButton = QtWidgets.QPushButton(btn_text)
		self.skipButton.setFixedWidth(125)
		self.addButton = QtWidgets.QPushButton('Add')
		self.addButton.setFixedWidth(125)

		# Layouts
		self.vLayoutMaster.addWidget(self.label)
		self.vLayoutMaster.addSpacing(10)
		self.vLayoutMaster.addWidget(self.custListDrop, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addSpacing(20)
		self.hLayout.addWidget(self.skipButton)
		self.hLayout.addWidget(self.addButton)
		self.vLayoutMaster.addLayout(self.hLayout)

		# Signals / slots
		self.skipButton.clicked.connect(self.reject)
		self.addButton.clicked.connect(self.add_to_cust_lists)

		# Window
		self.setLayout(self.vLayoutMaster)
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Add to custom list')
		self.setFixedSize(self.sizeHint())
		self.show()

		atcl_conn.close()

	def add_to_cust_lists(self):
		add_conn = sqlite3.connect(common_vars.video_db())
		add_cursor = add_conn.cursor()

		add_cursor.execute('SELECT vid_ids FROM custom_lists WHERE list_name = ?', (self.custListDrop.currentText(),))
		cl_vidids = add_cursor.fetchone()[0].split('; ')
		for v_id in self.vididList:
			if v_id not in cl_vidids:
				cl_vidids.append(v_id)

		if '' in cl_vidids:
			cl_vidids.remove('')
		new_vidid_str = '; '.join(cl_vidids)
		add_cursor.execute('UPDATE custom_lists SET vid_ids = ? WHERE list_name = ?', (new_vidid_str,
																					   self.custListDrop.currentText()))
		add_conn.commit()
		add_conn.close()
		self.accept()


class Worker(QtCore.QObject):
	finished = QtCore.pyqtSignal()
	progress = QtCore.pyqtSignal(str, int, int, list, list)

	def __init__(self, url, url_type, subdb, overwrite, dl_thumbs):
		super(Worker, self).__init__()
		self.url = url
		self.url_type = url_type
		self.subdb = subdb
		self.overwrite = overwrite
		self.dl_thumbs = dl_thumbs

		self.subdb_int = common_vars.sub_db_lookup()[self.subdb]

	def run(self):
		fetch_conn = sqlite3.connect(common_vars.video_db())
		fetch_cursor = fetch_conn.cursor()
		vid_entry_dict = common_vars.entry_dict()
		new_entries = []
		matching_entries = []
		vidids = []
		failed_urls = []

		# Define the list of video URLs to use
		if self.url_type == 'org':
			r = requests.get(self.url)
			soup = beautifulsoup(r.content, 'html5lib')

			video_urls_html = soup.find('ul', {'class': 'resultsList'}).find_all('a', attrs={'class': 'title'})
			video_urls = ['https://www.animemusicvideos.org' + vid_lnk.get('href') for vid_lnk in video_urls_html]

		elif self.url_type == 'youtube':
			chan = Channel(self.url)
			video_urls = chan.video_urls

		else:  # Playlist
			video_urls = Playlist(self.url).video_urls

		fetch_ctr = 0
		for lnk in video_urls:
			fetch_success = True
			if self.url_type == 'playlist':
				try:
					vid_data = fetch_vid_info.download_data(lnk, 'youtube')
				except:
					fetch_success = False
					yt = YouTube(lnk)
					ed = yt.author
					title = yt.title
					failed_urls.append('{} - {}: {}'.format(ed, title, lnk))
			else:
				try:
					vid_data = fetch_vid_info.download_data(lnk, self.url_type)
				except:
					fetch_success = False
					yt = YouTube(lnk)
					ed = yt.author
					title = yt.title
					failed_urls.append('{} - {}: {}'.format(ed, title, lnk))

			if fetch_success:
				editor = vid_data['primary_editor_username']
				vid_title = vid_data['video_title']

				# Checks if video already exists somewhere in import sub-DB
				fetch_cursor.execute('SELECT COUNT(*) FROM {}'.format(self.subdb_int))
				subdb_num_entries = fetch_cursor.fetchone()[0]
				if subdb_num_entries > 0:
					fetch_cursor.execute('SELECT video_id FROM {} WHERE primary_editor_username = ? COLLATE NOCASE AND '
										 'video_title = ? COLLATE NOCASE'
										 .format(self.subdb_int), (editor, vid_title))
					matching_vidid = fetch_cursor.fetchone()

					if matching_vidid:
						matching_entries.append((matching_vidid[0], vid_data))
					else:
						new_entries.append(vid_data)
				else:
					new_entries.append(vid_data)

			else:
				failed_urls.append(lnk)

			fetch_ctr += 1
			self.progress.emit('Fetching data: {} - {}'.format(editor, vid_title), fetch_ctr, len(video_urls), [], [])

		if new_entries:
			new_entr_ctr = 0
			for dct in new_entries:
				for k, v in dct.items():
					if k == 'release_date':
						if self.url_type == 'youtube' or self.url_type == 'playlist':
							vid_entry_dict['release_date'] = dct['release_date']

						else:
							if dct['release_date'][1] == 0 or dct['release_date'][2] == 0:
								vid_entry_dict['release_date'] = ''
								vid_entry_dict['release_date_unknown'] = 1
							else:
								if dct['release_date'][1] <= 9:
									mo = '0' + str(dct['release_date'][1])
								else:
									mo = str(dct['release_date'][1])

								if dct['release_date'][2] <= 9:
									day = '0' + str(dct['release_date'][2])
								else:
									day = str(dct['release_date'][2])
								vid_entry_dict['release_date'] = dct['release_date'][0] + '/' + mo + '/' + day

					elif k == 'video_footage':
						ftg_fixed = '; '.join(dct['video_footage'])
						vid_entry_dict['video_footage'] = ftg_fixed

					elif k == 'video_length':
						if self.url_type == 'youtube' or self.url_type == 'playlist':
							vid_entry_dict['video_length'] = dct['video_length']

						else:
							if dct['video_length'][0] == -1 or dct['video_length'] == -1:
								vid_entry_dict['video_length'] = ''
							else:
								vid_entry_dict['video_length'] = (60 * dct['video_length'][0]) + dct['video_length'][1]

					else:
						vid_entry_dict[k] = v

				vid_entry_dict['video_id'] = common_vars.id_generator('video')
				vid_entry_dict['sequence'] = common_vars.max_sequence_dict()[self.subdb]
				vid_entry_dict['date_entered'] = common_vars.current_date()

				if self.dl_thumbs:
					thumb_path = download_yt_thumb.download(vid_entry_dict['video_id'], dct['video_youtube_url'], bypass_check=True)
					vid_entry_dict['vid_thumb_path'] = thumb_path

				update_video_entry.update_video_entry(vid_entry_dict, [self.subdb])
				vidids.append(vid_entry_dict['video_id'])

				new_entr_ctr += 1
				prog_bar_label_ne = 'Importing new video data'.format(dct['primary_editor_username'],
																			   dct['video_title'])
				self.progress.emit(prog_bar_label_ne, new_entr_ctr, len(new_entries), [], [])

		if matching_entries and self.overwrite:
			matching_entr_ctr = 0
			for tup in matching_entries:
				existing_entry = common_vars.get_all_vid_info(self.subdb_int, tup[0])
				dct = tup[1]
				for k, v in tup[1].items():
					if k == 'release_date':
						if self.url_type == 'youtube' or self.url_type == 'playlist':
							existing_entry['release_date'] = dct['release_date']

						else:
							if dct['release_date'][1] == 0 or dct['release_date'][2] == 0:
								existing_entry['release_date'] = ''
								existing_entry['release_date_unknown'] = 1
							else:
								if dct['release_date'][1] <= 9:
									mo = '0' + str(dct['release_date'][1])
								else:
									mo = str(dct['release_date'][1])

								if dct['release_date'][2] <= 9:
									day = '0' + str(dct['release_date'][2])
								else:
									day = str(dct['release_date'][2])
								existing_entry['release_date'] = dct['release_date'][0] + '/' + mo + '/' + day

					elif k == 'video_footage':
						ftg_fixed = '; '.join(dct['video_footage'])
						existing_entry['video_footage'] = ftg_fixed

					elif k == 'video_length':
						if self.url_type == 'youtube' or self.url_type:
							existing_entry['video_length'] = dct['video_length']

						else:
							if dct['video_length'][0] == -1 or dct['video_length'] == -1:
								existing_entry['video_length'] = ''
							else:
								existing_entry['video_length'] = (60 * dct['video_length'][0]) + dct['video_length'][1]
					
					else:
						existing_entry[k] = v

				if self.dl_thumbs:
					thumb_path = download_yt_thumb.download(tup[0], dct['video_youtube_url'], bypass_check=True)
					print(thumb_path)
					existing_entry['vid_thumb_path'] = thumb_path

				update_video_entry.update_video_entry(existing_entry, [self.subdb], vid_id=tup[0])
				matching_entr_ctr += 1

				prog_bar_label_me = 'Updating existing entry'.format(tup[1]['primary_editor_username'],
																			  tup[1]['video_title'])
				self.progress.emit(prog_bar_label_me, matching_entr_ctr, len(matching_entries), [], [])
				vidids.append(existing_entry['video_id'])

		if self.url_type == 'playlist':
			if failed_urls:
				self.progress.emit('Done!', 1, 1, vidids, failed_urls)
			else:
				self.progress.emit('Done!', 1, 1, vidids, [])
		else:
			if failed_urls:
				self.progress.emit('Done!', 1, 1, [], failed_urls)
			else:
				self.progress.emit('Done!', 1, 1, [], [])

		fetch_conn.close()


class FetchWindow(QtWidgets.QMainWindow):
	def __init__(self, window_type='profile'):
		super(FetchWindow, self).__init__()
		self.window_type = window_type
		self.subDBs = common_vars.sub_db_lookup()

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.vLayoutMaster.setAlignment(QtCore.Qt.AlignCenter)
		self.hLayout1 = QtWidgets.QHBoxLayout()
		self.hLayout2 = QtWidgets.QHBoxLayout()

		if self.window_type == 'profile':
			msg = 'Below you can enter either the URL to an editor\'s AnimeMusicVideos.org\n' \
				  'profile or their YouTube channel, and AMV Tracker will download all the\n' \
				  'data it can for all of their videos.\n\n' \
				  'PLEASE NOTE: For YouTube profiles, AMV Tracker cannot differentiate\n' \
				  'between AMVs and any non-AMV videos uploaded to the editor\'s channel,\n' \
				  'so it will download data for non-AMVs if any are on the provided channel.'
			url_label = 'Editor profile/channel URL:'

		elif self.window_type == 'playlist':
			msg = 'Below you can enter the URL to a public YouTube playlist, and AMV Tracker\n' \
				  'will download all the data it can for all videos in the playlist. You will\n' \
				  'also be asked if you\'d like to enter these videos into any of your existing\n' \
				  'custom lists, if you have any.'
			url_label = 'Public YouTube playlist URL:'

		else:
			msg = 'Error'
			url_label = 'Error'

		self.label = QtWidgets.QLabel()
		self.label.setText(msg)

		self.urlLabel = QtWidgets.QLabel()
		self.urlLabel.setText(url_label)

		self.urlTextBox = QtWidgets.QLineEdit()
		self.urlTextBox.setFixedWidth(210)

		self.importIntoLabel = QtWidgets.QLabel()
		self.importIntoLabel.setText('Import video data into...')

		self.subDBDropdown = QtWidgets.QComboBox()
		self.subDBDropdown.setFixedWidth(200)
		for subdb in self.subDBs:
			self.subDBDropdown.addItem(subdb)

		self.overwriteExisting = QtWidgets.QCheckBox('Overwrite existing entries')
		self.overwriteExisting.setToolTip('If checked and a video that AMV Tracker locates is already in the\n'
										  'selected sub-DB, it will overwrite any information it finds. Fields\n'
										  'that are not represented on the video\'s .org or YouTube entry (i.e.\n'
										  'ratings, tags, personal comments, etc.) will not be touched.\n\n'
										  'If unchecked and the video already exists in the sub-DB, it will\n'
										  'be ignored and no data will be downloaded.')

		self.downloadThumbs = QtWidgets.QCheckBox('Download thumbnails')
		self.downloadThumbs.setToolTip('If checked, AMV Tracker will download the corresponding thumbnails for each\n'
									   'video. Please note that this will overwrite any existing thumbnails for matching\n'
									   'entries ONLY IF the "Overwrite existing entries" checkbox is also checked.')
		self.downloadThumbs.setDisabled(True)

		self.pBar = QtWidgets.QProgressBar()
		self.pBar.setInvertedAppearance(False)
		self.pBar.setTextVisible(True)
		self.pBar.setFixedWidth(300)
		self.pBar.setAlignment(QtCore.Qt.AlignCenter)

		self.backButton = QtWidgets.QPushButton('Back')
		self.backButton.setFixedWidth(125)
		self.downloadButton = QtWidgets.QPushButton('Download data')
		self.downloadButton.setFixedWidth(125)
		self.downloadButton.setDisabled(True)

		# Layouts
		self.vLayoutMaster.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addSpacing(10)
		self.hLayout1.addWidget(self.urlLabel)
		self.hLayout1.addWidget(self.urlTextBox)
		self.vLayoutMaster.addLayout(self.hLayout1)
		self.vLayoutMaster.addSpacing(10)
		self.vLayoutMaster.addWidget(self.importIntoLabel, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addWidget(self.subDBDropdown, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addWidget(self.overwriteExisting, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addWidget(self.downloadThumbs, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addSpacing(10)
		self.vLayoutMaster.addWidget(self.pBar, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addSpacing(10)
		self.hLayout2.addWidget(self.backButton)
		self.hLayout2.addWidget(self.downloadButton)
		self.vLayoutMaster.addLayout(self.hLayout2)

		# Signals / slots
		self.urlTextBox.textChanged.connect(self.check_url)
		self.downloadButton.clicked.connect(self.download_video_data)
		self.backButton.clicked.connect(self.close)

		# Widget
		self.wid = QtWidgets.QWidget()
		self.wid.setLayout(self.vLayoutMaster)
		self.setCentralWidget(self.wid)
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Download video data')
		self.setFixedSize(self.sizeHint())
		self.wid.show()

	def check_url(self):
		if self.window_type == 'profile':
			if 'www.animemusicvideos.org/members/members_myprofile.php?user_id=' in self.urlTextBox.text() or \
					'www.a-m-v.org/members/members_myprofile.php?user_id=' in self.urlTextBox.text() or \
					'www.youtube.com/channel/' in self.urlTextBox.text() or \
					'www.youtube.com/c/' in self.urlTextBox.text() or \
					'www.youtube.com/@' in self.urlTextBox.text():
				self.downloadButton.setEnabled(True)
			else:
				self.downloadButton.setDisabled(True)

		elif self.window_type == 'playlist':
			if ('www.youtube.com/watch?v=' in self.urlTextBox.text() and '&list=' in self.urlTextBox.text()) or \
					'www.youtube.com/playlist?' in self.urlTextBox.text():
				self.downloadButton.setEnabled(True)
			else:
				self.downloadButton.setDisabled(True)

		if 'www.youtube.com/' in self.urlTextBox.text():
			self.downloadThumbs.setEnabled(True)
		else:
			self.downloadThumbs.setDisabled(True)

	def download_video_data(self):
		self.backButton.setDisabled(True)
		self.downloadButton.setDisabled(True)
		if self.window_type == 'profile':
			if 'youtube' in self.urlTextBox.text():
				url_type = 'youtube'
			else:
				url_type = 'org'
		else:
			url_type = 'playlist'

		self.thrd = QtCore.QThread()
		self.worker = Worker(self.urlTextBox.text(), url_type, self.subDBDropdown.currentText(),
							 self.overwriteExisting.isChecked(), self.downloadThumbs.isChecked())
		self.worker.moveToThread(self.thrd)

		self.pBar.show()

		self.thrd.start()
		self.thrd.started.connect(self.worker.run)
		self.worker.finished.connect(self.thrd.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.worker.progress.connect(self.show_dl_progress)
		self.thrd.finished.connect(self.thrd.deleteLater)

	def show_dl_progress(self, label, n, total, vidid_list, failed_vids=None):
		if label == 'Done!':
			self.pBar.setFormat(label)
			self.thrd.quit()
			self.pBar.close()
			self.backButton.setEnabled(True)
			self.downloadButton.setEnabled(True)
			compl_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Done!',
											  'Video data has been successfully added to your database.')
			compl_win.exec_()

			if failed_vids:
				self.fail_notif = failed_fetches.FailedFetchesWin(failed_vids)
				self.fail_notif.exec_()
		else:
			self.pBar.setFormat(label + ' (' + str(n) + '/' + str(total) + ')')

		self.pBar.setMaximum(total - 1)
		self.pBar.setValue(n)

		if vidid_list:
			pl_conn = sqlite3.connect(common_vars.video_db())
			pl_cursor = pl_conn.cursor()
			pl_cursor.execute('SELECT COUNT(*) FROM custom_lists')
			if pl_cursor.fetchone()[0] != 0:
				cl_win = AddToCustomList(vidid_list)
				if cl_win.exec_():
					succ_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Success',
													 'Video(s) successfully added to the selected custom list.')
					succ_win.exec_()

			pl_conn.close()

