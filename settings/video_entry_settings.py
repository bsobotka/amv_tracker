import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import configparser
import sqlite3

from misc_files import common_vars


class VideoEntrySettings(QtWidgets.QWidget):
	def __init__(self):
		super(VideoEntrySettings, self).__init__()

		self.config = configparser.ConfigParser()
		self.config.read('config.ini')

		self.settings_conn = sqlite3.connect(common_vars.settings_db())
		self.settings_cursor = self.settings_conn.cursor()

		self.tag_conn = sqlite3.connect(common_vars.tag_db())
		self.tag_cursor = self.tag_conn.cursor()
		self.tagTableNames = common_vars.tag_table_lookup(reverse=True)

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.vLayoutMaster.setAlignment(QtCore.Qt.AlignTop)
		self.vLayout1 = QtWidgets.QVBoxLayout()
		self.vLayout2 = QtWidgets.QVBoxLayout()
		self.vLayout3 = QtWidgets.QVBoxLayout()
		self.hLayout1 = QtWidgets.QHBoxLayout()
		self.hLayout2 = QtWidgets.QHBoxLayout()

		self.gridLayout = QtWidgets.QGridLayout()
		self.gridLayout.setAlignment(QtCore.Qt.AlignLeft)
		self.gridLayout.setColumnMinimumWidth(1, 20)
		self.gridLayout.setRowMinimumHeight(7, 20)

		self.dataCheckLabel = QtWidgets.QLabel()
		self.dataCheckLabel.setText('Check that data exists\nin these fields:')

		self.checkReleaseDate = QtWidgets.QCheckBox('Release date')
		self.checkVideoFootage = QtWidgets.QCheckBox('Video footage')
		self.checkSongArtist = QtWidgets.QCheckBox('Song artist')
		self.checkSongTitle = QtWidgets.QCheckBox('Song title')
		self.checkSongGenre = QtWidgets.QCheckBox('Song genre')
		self.checkVideoLength = QtWidgets.QCheckBox('Video length')
		self.checkVideoDesc = QtWidgets.QCheckBox('Video description')
		self.checkMyRating = QtWidgets.QCheckBox('My rating')
		self.checkTags1 = QtWidgets.QCheckBox('Tags - ' + self.tagTableNames['tags_1'])
		self.checkTags2 = QtWidgets.QCheckBox('Tags - ' + self.tagTableNames['tags_2'])
		self.checkTags3 = QtWidgets.QCheckBox('Tags - ' + self.tagTableNames['tags_3'])
		self.checkTags4 = QtWidgets.QCheckBox('Tags - ' + self.tagTableNames['tags_4'])
		self.checkTags5 = QtWidgets.QCheckBox('Tags - ' + self.tagTableNames['tags_5'])
		self.checkTags6 = QtWidgets.QCheckBox('Tags - ' + self.tagTableNames['tags_6'])

		self.checkboxDict = {self.checkReleaseDate: 'check_release_date',
		                     self.checkVideoFootage: 'check_video_footage',
		                     self.checkSongArtist: 'check_song_artist',
		                     self.checkSongTitle: 'check_song_title',
		                     self.checkSongGenre: 'check_song_genre',
		                     self.checkVideoLength: 'check_video_length',
		                     self.checkVideoDesc: 'check_video_desc',
		                     self.checkMyRating: 'check_my_rating',
		                     self.checkTags1: 'check_tags_1',
		                     self.checkTags2: 'check_tags_2',
		                     self.checkTags3: 'check_tags_3',
		                     self.checkTags4: 'check_tags_4',
		                     self.checkTags5: 'check_tags_5',
		                     self.checkTags6: 'check_tags_6'
		                     }

		# Checkbox checked status
		for key, val in self.checkboxDict.items():
			self.settings_cursor.execute('SELECT value FROM entry_settings WHERE setting_name = ?', (val,))
			setting_val = self.settings_cursor.fetchone()
			if int(setting_val[0]) == 1:
				key.setChecked(True)
			else:
				key.setChecked(False)

		self.tagChkboxList = [self.checkTags1, self.checkTags2, self.checkTags3, self.checkTags4,
		                      self.checkTags5, self.checkTags6]

		# Disable/uncheck tag checkboxes if not in use
		for ind in range(0, len(self.tagChkboxList)):
			self.tag_cursor.execute('SELECT * FROM tags_{}'.format(ind + 1))
			table_result = self.tag_cursor.fetchone()
			if table_result is None:
				self.tagChkboxList[ind].setDisabled(True)
				self.tagChkboxList[ind].setChecked(False)
				self.settings_cursor.execute('UPDATE entry_settings SET value = ? WHERE setting_name = ?',
				                             (0, 'check_tags_{}'.format(ind + 1)))
				self.settings_conn.commit()

		# Link profiles
		self.linkProfilesChkbox = QtWidgets.QCheckBox(
			'Populate editor profile URLs if they exist in editor\'s existing entries')
		self.settings_cursor.execute('SELECT value FROM entry_settings WHERE setting_name = ?', ('link_profiles',))
		self.check_profile_val = int(self.settings_cursor.fetchone()[0])
		if self.check_profile_val == 1:
			self.linkProfilesChkbox.setChecked(True)
		else:
			self.linkProfilesChkbox.setChecked(False)

		# Checks enabled setting
		self.checksEnabledDefaultLabel = QtWidgets.QLabel()
		self.checksEnabledDefaultLabel.setText('\'Checks enabled\' default setting:')
		self.checksEnabledDropdown = QtWidgets.QComboBox()
		self.checksEnabledDropdown.setFixedWidth(80)
		self.checksEnabledDropdown.addItem('Unchecked')
		self.checksEnabledDropdown.addItem('Checked')

		self.settings_cursor.execute('SELECT value FROM entry_settings WHERE setting_name = ?',
		                             ('checks_enabled_default',))
		self.checks_en_val = int(self.settings_cursor.fetchone()[0])
		self.checksEnabledDropdown.setCurrentIndex(self.checks_en_val)

		# Other buttons
		self.setMutExclTags = QtWidgets.QPushButton('Set mutually exclusive tags')
		self.saveButton = QtWidgets.QPushButton('Save')

		self.gridLayout.addWidget(self.dataCheckLabel, 0, 0, 2, 1, alignment=QtCore.Qt.AlignTop)
		self.gridLayout.addWidget(self.checkReleaseDate, 0, 2)
		self.gridLayout.addWidget(self.checkVideoFootage, 1, 2)
		self.gridLayout.addWidget(self.checkSongArtist, 2, 2)
		self.gridLayout.addWidget(self.checkSongTitle, 3, 2)
		self.gridLayout.addWidget(self.checkSongGenre, 4, 2)
		self.gridLayout.addWidget(self.checkVideoLength, 5, 2)
		self.gridLayout.addWidget(self.checkVideoDesc, 6, 2)

		self.gridLayout.addWidget(self.checkMyRating, 0, 3)
		self.gridLayout.addWidget(self.checkTags1, 1, 3)
		self.gridLayout.addWidget(self.checkTags2, 2, 3)
		self.gridLayout.addWidget(self.checkTags3, 3, 3)
		self.gridLayout.addWidget(self.checkTags4, 4, 3)
		self.gridLayout.addWidget(self.checkTags5, 5, 3)
		self.gridLayout.addWidget(self.checkTags6, 6, 3)

		self.gridLayout.addWidget(self.checksEnabledDefaultLabel, 8, 0, 1, 2)
		self.gridLayout.addWidget(self.checksEnabledDropdown, 8, 2, 1, 2)

		self.gridLayout.addWidget(self.linkProfilesChkbox, 9, 0, 1, 4)

		self.gridLayout.addWidget(self.setMutExclTags, 10, 0, 1, 2)

		self.vLayoutMaster.addSpacing(20)
		self.vLayoutMaster.addLayout(self.gridLayout)
		self.vLayoutMaster.addSpacing(150)
		self.vLayoutMaster.addWidget(self.saveButton, alignment=QtCore.Qt.AlignRight)

		# Signals/slots
		self.saveButton.clicked.connect(lambda: self.save_button_clicked())

	def save_button_clicked(self):
		# Save checkbox states
		for chk, text in self.checkboxDict.items():
			if chk.isChecked():
				cbox_val = 1
			else:
				cbox_val = 0

			self.settings_cursor.execute('UPDATE entry_settings SET value = ? WHERE setting_name = ?', (cbox_val, text))

		# Save state of profile link checkbox
		if self.linkProfilesChkbox.isChecked():
			link_val = 1
		else:
			link_val = 0

		self.settings_cursor.execute('UPDATE entry_settings SET value = ? WHERE setting_name = ?',
		                             (link_val, 'link_profiles'))

		# Save state of 'Checks Enabled' dropdown
		self.settings_cursor.execute('UPDATE entry_settings SET value = ? WHERE setting_name = ?',
		                             (self.checksEnabledDropdown.currentIndex(), 'checks_enabled_default'))

		# Commit all changes to settings.db
		self.settings_conn.commit()

		settings_saved_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Settings saved',
		                                           'Video entry settings\nhave been saved.')
		settings_saved_box.exec_()
