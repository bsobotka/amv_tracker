import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import sqlite3

from misc_files import common_vars
from settings import custom_tag_logic_window, mut_excl_tags_window


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

		self.headerFont = QtGui.QFont()
		self.headerFont.setUnderline(True)
		self.headerFont.setBold(True)
		self.headerFont.setPixelSize(14)

		self.gridLayout = QtWidgets.QGridLayout()
		self.gridLayout.setAlignment(QtCore.Qt.AlignLeft)
		self.gridLayout.setColumnMinimumWidth(1, 20)
		self.gridLayout.setRowMinimumHeight(7, 20)

		self.checkDataHeader = QtWidgets.QLabel()
		self.checkDataHeader.setText('Data checking')
		self.checkDataHeader.setFont(self.headerFont)

		self.dataCheckLabel = QtWidgets.QLabel()
		self.dataCheckLabel.setText('Check that data exists\nin these fields:')
		self.dataCheckLabel.setToolTip('If you have the "Checks enabled" box checked on the data entry\n'
									   'screen (in the "Submission rules" tab), any fields that you have\n'
									   'checked to the right will need to be populated before the video\n'
									   'can be entered into the database.')

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

		# Checks enabled setting
		self.checksEnabledDefaultLabel = QtWidgets.QLabel()
		self.checksEnabledDefaultLabel.setText('\'Checks enabled\' default setting:')
		self.checksEnabledDropdown = QtWidgets.QComboBox()
		self.checksEnabledDropdown.setFixedWidth(80)
		self.checksEnabledDropdown.addItem('Unchecked')
		self.checksEnabledDropdown.addItem('Checked')
		self.checksEnabledDropdown.setCurrentIndex(self.ve_settings_init_dict['checks_enabled_default'])

		# Entry automation header
		self.automationHeader = QtWidgets.QLabel()
		self.automationHeader.setText('Video entry automation')
		self.automationHeader.setFont(self.headerFont)

		# Link pseudonyms
		self.linkPseudoChkbox = QtWidgets.QCheckBox('Link pseudonyms to existing entries')
		self.linkPseudoChkbox.setToolTip('If checked, whenever you submit a video, AMV Tracker will automatically\n'
										 'update the new entry with any pseudonyms identified on any existing entries\n'
										 'from the editor, and will also update any existing entries with any new\n'
										 'pseudonyms identified in the new entry.')
		if self.ve_settings_init_dict['link_pseudonyms'] == 1:
			self.linkPseudoChkbox.setChecked(True)
		else:
			self.linkPseudoChkbox.setChecked(False)

		# Auto-populate genre
		self.autopopGenreChkbox = QtWidgets.QCheckBox('Auto-populate song genre')
		self.autopopGenreChkbox.setToolTip('If checked, whenever you enter a song artist on a video entry, AMV\n'
										   'Tracker will check for existing entries with the same song artist\n'
										   'and will automatically populate the Song Genre field with the most-\n'
										   'used genre for that artist.')
		if self.ve_settings_init_dict['autopop_genre'] == 1:
			self.autopopGenreChkbox.setChecked(True)
		else:
			self.autopopGenreChkbox.setChecked(False)

		# Auto-generate thumbnails
		self.autoGenThumbs = QtWidgets.QCheckBox('Auto-generate thumbnails')
		self.autoGenThumbs.setToolTip('If checked, when you identify a local video file on manual video entry,\n'
									  'AMV Tracker will automatically generate a random thumbnail from the video\n'
									  'file. You can always have AMV Tracker generate other thumbnails if you\n'
									  'don\'t like the one it auto-generates.')
		if self.ve_settings_init_dict['auto_gen_thumbs'] == 1:
			self.autoGenThumbs.setChecked(True)
		else:
			self.autoGenThumbs.setChecked(False)

		# Other buttons
		self.setMutExclTags = QtWidgets.QPushButton('Set mutually exclusive tags')
		self.customTagLogic = QtWidgets.QPushButton('Custom tag logic')
		self.customTagLogic.setToolTip('Help automate tagging by creating your own logic, which will auto-check tags\n'
									   'if conditions you specify are met elsewhere in the video entry fields.')
		self.saveButton = QtWidgets.QPushButton('Save')

		self.gridLayout.addWidget(self.checkDataHeader, 0, 0, alignment=QtCore.Qt.AlignTop)
		self.gridLayout.addWidget(self.dataCheckLabel, 1, 0, 2, 1, alignment=QtCore.Qt.AlignTop)
		self.gridLayout.addWidget(self.checkReleaseDate, 1, 2)
		self.gridLayout.addWidget(self.checkVideoFootage, 2, 2)
		self.gridLayout.addWidget(self.checkSongArtist, 3, 2)
		self.gridLayout.addWidget(self.checkSongTitle, 4, 2)
		self.gridLayout.addWidget(self.checkSongGenre, 5, 2)
		self.gridLayout.addWidget(self.checkVideoLength, 6, 2)
		self.gridLayout.addWidget(self.checkVideoDesc, 7, 2)

		self.gridLayout.addWidget(self.checkMyRating, 1, 3)
		self.gridLayout.addWidget(self.checkTags1, 2, 3)
		self.gridLayout.addWidget(self.checkTags2, 3, 3)
		self.gridLayout.addWidget(self.checkTags3, 4, 3)
		self.gridLayout.addWidget(self.checkTags4, 5, 3)
		self.gridLayout.addWidget(self.checkTags5, 6, 3)
		self.gridLayout.addWidget(self.checkTags6, 7, 3)

		self.gridLayout.setRowMinimumHeight(8, 15)
		self.gridLayout.addWidget(self.checksEnabledDefaultLabel, 9, 0, 1, 2)
		self.gridLayout.addWidget(self.checksEnabledDropdown, 9, 2, 1, 2)

		self.gridLayout.setRowMinimumHeight(10, 15)
		self.gridLayout.addWidget(self.automationHeader, 11, 0, 1, 4)
		self.gridLayout.addWidget(self.linkPseudoChkbox, 12, 0, 1, 4)
		self.gridLayout.addWidget(self.autopopGenreChkbox, 13, 0, 1, 4)
		self.gridLayout.addWidget(self.autoGenThumbs, 14, 0, 1, 4)

		self.gridLayout.addWidget(self.setMutExclTags, 15, 0, 1, 2)
		self.gridLayout.addWidget(self.customTagLogic, 16, 0, 1, 2)

		self.vLayoutMaster.addSpacing(20)
		self.vLayoutMaster.addLayout(self.gridLayout)
		self.vLayoutMaster.addSpacing(150)
		self.vLayoutMaster.addWidget(self.saveButton, alignment=QtCore.Qt.AlignRight)

		# Signals/slots
		self.setMutExclTags.clicked.connect(self.set_mut_excl_tags_clicked)
		self.customTagLogic.clicked.connect(self.custom_tag_logic_clicked)
		self.saveButton.clicked.connect(self.save_button_clicked)

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

	def custom_tag_logic_clicked(self):
		self.ctlr_mgmt_win = custom_tag_logic_window.TagLogicMgmt()
		self.ctlr_mgmt_win.show()

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

		save_settings_cursor.execute('UPDATE entry_settings SET value = ? WHERE setting_name = "link_pseudonyms"',
		                             (link_pseudo_val,))

		# Save state of autopopulate genre checkbox
		if self.autopopGenreChkbox.isChecked():
			autopop_genre_val = 1
		else:
			autopop_genre_val = 0

		save_settings_cursor.execute('UPDATE entry_settings SET value = ? WHERE setting_name = "autopop_genre"',
									 (autopop_genre_val,))

		# Save state of auto-gen thumbnails checkbox
		if self.autoGenThumbs.isChecked():
			autogen_thumbs_val = 1
		else:
			autogen_thumbs_val = 0

		save_settings_cursor.execute('UPDATE entry_settings SET value = ? WHERE setting_name = "auto_gen_thumbs"',
									 (autogen_thumbs_val,))

		# Save state of 'Checks Enabled' dropdown
		save_settings_cursor.execute('UPDATE entry_settings SET value = ? WHERE setting_name = ?',
		                             (self.checksEnabledDropdown.currentIndex(), 'checks_enabled_default'))

		# Commit all changes to settings.db
		save_settings_conn.commit()
		save_settings_conn.close()

		ve_settings_saved_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Settings saved',
		                                              'Video entry settings have been saved.')
		ve_settings_saved_box.exec_()
