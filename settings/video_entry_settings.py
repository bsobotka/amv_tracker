import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import sqlite3

from misc_files import common_vars
from settings import mut_excl_tags_window


class VideoEntrySettings(QtWidgets.QWidget):
	def __init__(self):
		super(VideoEntrySettings, self).__init__()

		ve_settings_conn = sqlite3.connect(common_vars.settings_db())
		ve_settings_cursor = ve_settings_conn.cursor()

		self.tagTableNames = common_vars.tag_table_lookup(reverse=True)

		self.ve_settings_init_dict = {}
		ve_settings_cursor.execute('SELECT setting_name, value FROM entry_settings')
		for setting_pair in ve_settings_cursor.fetchall():
			self.ve_settings_init_dict[setting_pair[0]] = int(setting_pair[1])

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

		# Link profiles
		self.linkProfilesChkbox = QtWidgets.QCheckBox(
			'Populate editor profile URLs if they exist in editor\'s existing entries')
		if self.ve_settings_init_dict['link_profiles'] == 1:
			self.linkProfilesChkbox.setChecked(True)
		else:
			self.linkProfilesChkbox.setChecked(False)

		# Link pseudonyms
		self.linkPseudoChkbox = QtWidgets.QCheckBox('Link pseudonyms to existing entries')
		self.linkPseudoChkbox.setToolTip('If checked, whenever you submit a video with a pseudonym entered,\n'
		                                 'AMV Tracker will update all of the editor\'s existing videos with '
		                                 'any new\npseudonyms identified.')
		if self.ve_settings_init_dict['link_pseudonyms'] == 1:
			self.linkPseudoChkbox.setChecked(True)
		else:
			self.linkPseudoChkbox.setChecked(False)

		# Checks enabled setting
		self.checksEnabledDefaultLabel = QtWidgets.QLabel()
		self.checksEnabledDefaultLabel.setText('\'Checks enabled\' default setting:')
		self.checksEnabledDropdown = QtWidgets.QComboBox()
		self.checksEnabledDropdown.setFixedWidth(80)
		self.checksEnabledDropdown.addItem('Unchecked')
		self.checksEnabledDropdown.addItem('Checked')
		self.checksEnabledDropdown.setCurrentIndex(self.ve_settings_init_dict['checks_enabled_default'])

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

		self.gridLayout.addWidget(self.linkPseudoChkbox, 9, 0, 1, 4)
		self.gridLayout.addWidget(self.linkProfilesChkbox, 10, 0, 1, 4)

		self.gridLayout.addWidget(self.setMutExclTags, 11, 0, 1, 2)

		self.vLayoutMaster.addSpacing(20)
		self.vLayoutMaster.addLayout(self.gridLayout)
		self.vLayoutMaster.addSpacing(150)
		self.vLayoutMaster.addWidget(self.saveButton, alignment=QtCore.Qt.AlignRight)

		# Signals/slots
		self.saveButton.clicked.connect(lambda: self.save_button_clicked())
		self.setMutExclTags.clicked.connect(lambda: self.set_mut_excl_tags_clicked())

	def refresh_checkboxes(self):
		# Checkbox checked status
		entry_settings_dict_for_refr = {}
		refresh_settings_conn = sqlite3.connect(common_vars.settings_db())
		refresh_settings_cursor = refresh_settings_conn.cursor()
		refresh_settings_cursor.execute('SELECT setting_name, value FROM entry_settings')

		refresh_tag_conn = sqlite3.connect(common_vars.tag_db())
		refresh_tag_cursor = refresh_tag_conn.cursor()

		for setting_pair in refresh_settings_cursor.fetchall():
			entry_settings_dict_for_refr[setting_pair[0]] = int(setting_pair[1])

		for key, val in self.checkboxDict.items():
			if entry_settings_dict_for_refr[val] == 1:
				key.setChecked(True)
			else:
				key.setChecked(False)

		tagChkboxList = [self.checkTags1, self.checkTags2, self.checkTags3, self.checkTags4,
		                      self.checkTags5, self.checkTags6]

		# Disable/uncheck tag checkboxes if not in use
		for ind in range(0, len(tagChkboxList)):
			refresh_tag_cursor.execute('SELECT * FROM tags_{}'.format(ind + 1))
			table_result = refresh_tag_cursor.fetchone()
			if table_result is None:
				tagChkboxList[ind].setDisabled(True)
				tagChkboxList[ind].setChecked(False)
				refresh_settings_cursor.execute('UPDATE entry_settings SET value = ? WHERE setting_name = ?',
				                                (0, 'check_tags_{}'.format(ind + 1)))
				refresh_settings_conn.commit()
			else:
				tagChkboxList[ind].setEnabled(True)

		# Update tag checkbox labels
		tag_group_names = common_vars.tag_table_lookup(reverse=True)
		self.checkTags1.setText('Tags - ' + tag_group_names['tags_1'])
		self.checkTags2.setText('Tags - ' + tag_group_names['tags_2'])
		self.checkTags3.setText('Tags - ' + tag_group_names['tags_3'])
		self.checkTags4.setText('Tags - ' + tag_group_names['tags_4'])
		self.checkTags5.setText('Tags - ' + tag_group_names['tags_5'])
		self.checkTags6.setText('Tags - ' + tag_group_names['tags_6'])

		refresh_settings_conn.close()
		refresh_tag_conn.close()

	def set_mut_excl_tags_clicked(self):
		self.mut_excl_win = mut_excl_tags_window.MutuallyExclTagsWindow()
		self.mut_excl_win.show()

	def save_button_clicked(self):
		save_settings_conn = sqlite3.connect(common_vars.settings_db())
		save_settings_cursor = save_settings_conn.cursor()

		# Save checkbox states
		for chk, text in self.checkboxDict.items():
			if chk.isChecked():
				cbox_val = 1
			else:
				cbox_val = 0

			save_settings_cursor.execute('UPDATE entry_settings SET value = ? WHERE setting_name = ?', (cbox_val, text))

		# Save state of link pseudonyms checkbox
		if self.linkPseudoChkbox.isChecked():
			link_pseudo_val = 1
		else:
			link_pseudo_val = 0

		save_settings_cursor.execute('UPDATE entry_settings SET value = ? WHERE setting_name = ?',
		                             (link_pseudo_val, 'link_pseudonyms'))

		# Save state of profile link checkbox
		if self.linkProfilesChkbox.isChecked():
			link_profile_val = 1
		else:
			link_profile_val = 0

		save_settings_cursor.execute('UPDATE entry_settings SET value = ? WHERE setting_name = ?',
		                             (link_profile_val, 'link_profiles'))

		# Save state of 'Checks Enabled' dropdown
		save_settings_cursor.execute('UPDATE entry_settings SET value = ? WHERE setting_name = ?',
		                             (self.checksEnabledDropdown.currentIndex(), 'checks_enabled_default'))

		# Commit all changes to settings.db
		save_settings_conn.commit()
		save_settings_conn.close()

		ve_settings_saved_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Settings saved',
		                                           'Video entry settings\nhave been saved.')
		ve_settings_saved_box.exec_()
