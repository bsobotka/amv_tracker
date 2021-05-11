import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import configparser
import sqlite3

from settings import settings_notifications, settings_window
from misc_files import common_vars, generic_one_line_entry_window


class VideoEntrySettings(QtWidgets.QWidget):
	def __init__(self):
		super(VideoEntrySettings, self).__init__()

		self.config = configparser.ConfigParser()
		self.config.read('config.ini')

		self.conn = sqlite3.connect(common_vars.tag_db())
		self.cursor = self.conn.cursor()
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
		if int(self.config['VIDEO_ENTRY']['check_release_date']) == 1:
			self.checkReleaseDate.setChecked(True)

		self.checkVideoFootage = QtWidgets.QCheckBox('Video footage')
		if int(self.config['VIDEO_ENTRY']['check_video_footage']) == 1:
			self.checkVideoFootage.setChecked(True)

		self.checkSongArtist = QtWidgets.QCheckBox('Song artist')
		if int(self.config['VIDEO_ENTRY']['check_song_artist']) == 1:
			self.checkSongArtist.setChecked(True)

		self.checkSongTitle = QtWidgets.QCheckBox('Song title')
		if int(self.config['VIDEO_ENTRY']['check_song_title']) == 1:
			self.checkSongTitle.setChecked(True)

		self.checkSongGenre = QtWidgets.QCheckBox('Song genre')
		if int(self.config['VIDEO_ENTRY']['check_song_genre']) == 1:
			self.checkSongGenre.setChecked(True)

		self.checkVideoLength = QtWidgets.QCheckBox('Video length')
		if int(self.config['VIDEO_ENTRY']['check_video_length']) == 1:
			self.checkVideoLength.setChecked(True)

		self.checkVideoDesc = QtWidgets.QCheckBox('Video description')
		if int(self.config['VIDEO_ENTRY']['check_video_desc']) == 1:
			self.checkVideoDesc.setChecked(True)

		self.checkMyRating = QtWidgets.QCheckBox('My rating')
		if int(self.config['VIDEO_ENTRY']['check_my_rating']) == 1:
			self.checkMyRating.setChecked(True)

		self.checkTags1 = QtWidgets.QCheckBox('Tags - ' + self.tagTableNames['tags_1'])
		if int(self.config['VIDEO_ENTRY']['check_tags_1']) == 1:
			self.checkTags1.setChecked(True)

		self.checkTags2 = QtWidgets.QCheckBox('Tags - ' + self.tagTableNames['tags_2'])
		if int(self.config['VIDEO_ENTRY']['check_tags_2']) == 1:
			self.checkTags2.setChecked(True)

		self.checkTags3 = QtWidgets.QCheckBox('Tags - ' + self.tagTableNames['tags_3'])
		if int(self.config['VIDEO_ENTRY']['check_tags_3']) == 1:
			self.checkTags3.setChecked(True)

		self.checkTags4 = QtWidgets.QCheckBox('Tags - ' + self.tagTableNames['tags_4'])
		if int(self.config['VIDEO_ENTRY']['check_tags_4']) == 1:
			self.checkTags4.setChecked(True)

		self.checkTags5 = QtWidgets.QCheckBox('Tags - ' + self.tagTableNames['tags_5'])
		if int(self.config['VIDEO_ENTRY']['check_tags_5']) == 1:
			self.checkTags5.setChecked(True)

		self.checkTags6 = QtWidgets.QCheckBox('Tags - ' + self.tagTableNames['tags_6'])
		if int(self.config['VIDEO_ENTRY']['check_tags_6']) == 1:
			self.checkTags6.setChecked(True)

		self.checkboxList = {self.checkReleaseDate: 'check_release_date',
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

		self.tagChkboxList = [self.checkTags1, self.checkTags2, self.checkTags3, self.checkTags4,
		                      self.checkTags5, self.checkTags6]

		for ind in range(0, len(self.tagChkboxList)):
			self.cursor.execute('SELECT * FROM tags_{}'.format(ind + 1))
			table_result = self.cursor.fetchone()
			if table_result is None:
				self.tagChkboxList[ind].setDisabled(True)
				self.tagChkboxList[ind].setChecked(False)
				self.config['VIDEO_ENTRY']['check_tags_{}'.format(ind + 1)] = '0'

		self.linkProfilesChkbox = QtWidgets.QCheckBox('Populate editor profile URLs if they exist in editor\'s existing entries')
		if int(self.config['VIDEO_ENTRY']['link_profiles']) == 1:
			self.linkProfilesChkbox.setChecked(True)

		self.checksEnabledDefaultLabel = QtWidgets.QLabel()
		self.checksEnabledDefaultLabel.setText('\'Checks enabled\' default setting:')

		self.checksEnabledDropdown = QtWidgets.QComboBox()
		self.checksEnabledDropdown.addItem('Unchecked')
		self.checksEnabledDropdown.addItem('Checked')
		self.checksEnabledDropdown.setCurrentIndex(int(self.config['VIDEO_ENTRY']['checks_enabled_default']))
		self.checksEnabledDropdown.setFixedWidth(80)

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
		for chk in self.checkboxList.items():
			if chk[0].isChecked():
				self.config['VIDEO_ENTRY'][chk[1]] = '1'
			else:
				self.config['VIDEO_ENTRY'][chk[1]] = '0'

		if self.linkProfilesChkbox.isChecked():
			self.config['VIDEO_ENTRY']['link_profiles'] = '1'
		else:
			self.config['VIDEO_ENTRY']['link_profiles'] = '0'

		self.config['VIDEO_ENTRY']['checks_enabled_default'] = str(self.checksEnabledDropdown.currentIndex())

		with open('config.ini', 'w') as configfile:
			self.config.write(configfile)

		settings_saved_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Settings saved',
		                                    'Video entry settings\nhave been saved.')
		settings_saved_box.exec_()
