import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import sqlite3

from os import getcwd

from main_window import mainwindow
from misc_files import common_vars, tag_checkboxes
from settings import data_import


class MassEditWindow(QtWidgets.QMainWindow):
	def __init__(self, inp_vidids, subdb):
		super(MassEditWindow, self).__init__()
		settings_conn = sqlite3.connect(common_vars.settings_db())
		settings_cursor = settings_conn.cursor()
		settings_cursor.execute('SELECT field_name_display, in_use FROM search_field_lookup WHERE tag_field = 1')
		tag_name_list_all = [(x[0], x[1]) for x in settings_cursor.fetchall()]
		tag_name_list_in_use = [x[0] for x in tag_name_list_all if x[1] == 1]
		tag_name_list_in_use.sort(key=lambda x: x.casefold())
		tag_name_list_not_in_use = [x[0] for x in tag_name_list_all if x[1] == 0]
		tag_name_list_not_in_use.sort(key=lambda x: x.casefold())
		tag_name_list_all_for_use = tag_name_list_in_use + tag_name_list_not_in_use

		v_ind = 0
		self.inpVidids = inp_vidids
		self.subdb = subdb
		self.boldFont = QtGui.QFont()
		self.boldFont.setPixelSize(16)
		self.boldFont.setBold(False)

		self.scrollWidget = QtWidgets.QWidget()
		self.scrollArea = QtWidgets.QScrollArea()

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.topRowHLayout = QtWidgets.QHBoxLayout()
		self.bottomBtnHLayout = QtWidgets.QHBoxLayout()
		self.bottomBtnHLayout.setAlignment(QtCore.Qt.AlignRight)
		self.favHLayout = QtWidgets.QHBoxLayout()
		self.notableHLayout = QtWidgets.QHBoxLayout()
		self.myRatingHLayout = QtWidgets.QHBoxLayout()
		self.starRatingHLayout = QtWidgets.QHBoxLayout()
		self.tags1HLayout = QtWidgets.QHBoxLayout()
		self.tags2HLayout = QtWidgets.QHBoxLayout()
		self.tags3HLayout = QtWidgets.QHBoxLayout()
		self.tags4HLayout = QtWidgets.QHBoxLayout()
		self.tags5HLayout = QtWidgets.QHBoxLayout()
		self.tags6HLayout = QtWidgets.QHBoxLayout()
		self.gridLayout = QtWidgets.QGridLayout()

		self.dlYTThumbsBtn = QtWidgets.QPushButton('DL thumbs from YT')
		self.dlYTThumbsBtn.setFixedWidth(125)
		self.dlYTThumbsBtn.setToolTip('Download thumbnails for filtered videos which have a YouTube\n'
									  'video profile URL provided.')

		self.generateThumbsBtn = QtWidgets.QPushButton('Generate thumbs')
		self.generateThumbsBtn.setFixedWidth(125)
		self.generateThumbsBtn.setToolTip('Generate thumbnails from local video files for\nfiltered videos.')

		self.deleteIcon = QtGui.QIcon(getcwd() + '\\icons\\delete_icon.png')
		self.deleteButton = QtWidgets.QPushButton()
		self.deleteButton.setToolTip('Delete all filtered videos from AMV Tracker')
		self.deleteButton.setFixedSize(25, 25)
		self.deleteButton.setIconSize(QtCore.QSize(15, 15))
		self.deleteButton.setIcon(self.deleteIcon)

		self.helpButton = QtWidgets.QPushButton('?')
		self.helpButton.setFixedSize(25, 25)
		self.helpButton.setToolTip('Help')
		self.helpButton.setFont(self.boldFont)

		self.addlEditorsLabel = QtWidgets.QLabel()
		self.addlEditorsLabel.setText('Additional editors: ')

		self.addlEditorsTextBox = QtWidgets.QLineEdit()
		self.addlEditorsTextBox.setFixedWidth(320)
		self.addlEditorsTextBox.setPlaceholderText('Separate multiple editors with "; " (semicolon plus space)')

		self.addlEditorsNoAction = QtWidgets.QRadioButton('No action')
		self.addlEditorsNoAction.setChecked(True)
		self.addlEditorsOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.addlEditorsAdd = QtWidgets.QRadioButton('Add to')
		self.addlEditorsDelete = QtWidgets.QRadioButton('Clear field')
		self.addlEditorsBtnGrp = QtWidgets.QButtonGroup()
		self.addlEditorsBtnGrp.setExclusive(True)
		self.addlEditorsBtnGrp.addButton(self.addlEditorsNoAction)
		self.addlEditorsBtnGrp.addButton(self.addlEditorsOverwrite)
		self.addlEditorsBtnGrp.addButton(self.addlEditorsAdd)
		self.addlEditorsBtnGrp.addButton(self.addlEditorsDelete)

		self.gridLayout.addWidget(self.addlEditorsLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.addlEditorsTextBox, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.addlEditorsNoAction, v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.addlEditorsOverwrite, v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.addlEditorsAdd, v_ind, 4, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.addlEditorsDelete, v_ind, 5, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.editorPseudLabel = QtWidgets.QLabel()
		self.editorPseudLabel.setText('Primary editor pseudonyms: ')

		self.editorPseudTextBox = QtWidgets.QLineEdit()
		self.editorPseudTextBox.setFixedWidth(320)
		self.editorPseudTextBox.setPlaceholderText('Separate multiple pseudonyms with "; " (semicolon plus space)')

		self.editorPseudNoAction = QtWidgets.QRadioButton('No action')
		self.editorPseudNoAction.setChecked(True)
		self.editorPseudOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.editorPseudAdd = QtWidgets.QRadioButton('Add to')
		self.editorPseudDelete = QtWidgets.QRadioButton('Clear field')
		self.editorPseudBtnGrp = QtWidgets.QButtonGroup()
		self.editorPseudBtnGrp.setExclusive(True)
		self.editorPseudBtnGrp.addButton(self.editorPseudNoAction)
		self.editorPseudBtnGrp.addButton(self.editorPseudOverwrite)
		self.editorPseudBtnGrp.addButton(self.editorPseudAdd)
		self.editorPseudBtnGrp.addButton(self.editorPseudDelete)

		self.gridLayout.addWidget(self.editorPseudLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.editorPseudTextBox, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorPseudNoAction, v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorPseudOverwrite, v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorPseudAdd, v_ind, 4, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorPseudDelete, v_ind, 5, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.studioLabel = QtWidgets.QLabel()
		self.studioLabel.setText('Studio: ')

		self.studioTextBox = QtWidgets.QLineEdit()
		self.studioTextBox.setFixedWidth(320)

		self.studioNoAction = QtWidgets.QRadioButton('No action')
		self.studioNoAction.setChecked(True)
		self.studioOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.studioDelete = QtWidgets.QRadioButton('Clear field')
		self.studioBtnGrp = QtWidgets.QButtonGroup()
		self.studioBtnGrp.setExclusive(True)
		self.studioBtnGrp.addButton(self.studioNoAction)
		self.studioBtnGrp.addButton(self.studioOverwrite)
		self.studioBtnGrp.addButton(self.studioDelete)

		self.gridLayout.addWidget(self.studioLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.studioTextBox, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.studioNoAction, v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.studioOverwrite, v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.studioDelete, v_ind, 4, 1, 2, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.gridLayout.setRowMinimumHeight(v_ind, 10)
		v_ind += 1

		self.vidDescLabel = QtWidgets.QLabel()
		self.vidDescLabel.setText('Video description: ')

		self.vidDescTextBox = QtWidgets.QTextEdit()
		self.vidDescTextBox.setFixedSize(320, 60)

		self.vidDescNoAction = QtWidgets.QRadioButton('No action')
		self.vidDescNoAction.setChecked(True)
		self.vidDescOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.vidDescAdd = QtWidgets.QRadioButton('Add to')
		self.vidDescDelete = QtWidgets.QRadioButton('Clear field')
		self.vidDescBtnGrp = QtWidgets.QButtonGroup()
		self.vidDescBtnGrp.setExclusive(True)
		self.vidDescBtnGrp.addButton(self.vidDescNoAction)
		self.vidDescBtnGrp.addButton(self.vidDescOverwrite)
		self.vidDescBtnGrp.addButton(self.vidDescAdd)
		self.vidDescBtnGrp.addButton(self.vidDescDelete)

		self.gridLayout.addWidget(self.vidDescLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.vidDescTextBox, v_ind, 1)
		self.gridLayout.addWidget(self.vidDescNoAction, v_ind, 2)
		self.gridLayout.addWidget(self.vidDescOverwrite, v_ind, 3)
		self.gridLayout.addWidget(self.vidDescAdd, v_ind, 4)
		self.gridLayout.addWidget(self.vidDescDelete, v_ind, 5)
		v_ind += 1

		self.commentsLabel = QtWidgets.QLabel()
		self.commentsLabel.setText('Comments: ')

		self.commentsTextBox = QtWidgets.QTextEdit()
		self.commentsTextBox.setFixedSize(320, 60)

		self.commentsNoAction = QtWidgets.QRadioButton('No action')
		self.commentsNoAction.setChecked(True)
		self.commentsOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.commentsAdd = QtWidgets.QRadioButton('Add to')
		self.commentsDelete = QtWidgets.QRadioButton('Clear field')
		self.commentsBtnGrp = QtWidgets.QButtonGroup()
		self.commentsBtnGrp.setExclusive(True)
		self.commentsBtnGrp.addButton(self.commentsNoAction)
		self.commentsBtnGrp.addButton(self.commentsOverwrite)
		self.commentsBtnGrp.addButton(self.commentsAdd)
		self.commentsBtnGrp.addButton(self.commentsDelete)

		self.gridLayout.addWidget(self.commentsLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.commentsTextBox, v_ind, 1)
		self.gridLayout.addWidget(self.commentsNoAction, v_ind, 2)
		self.gridLayout.addWidget(self.commentsOverwrite, v_ind, 3)
		self.gridLayout.addWidget(self.commentsAdd, v_ind, 4)
		self.gridLayout.addWidget(self.commentsDelete, v_ind, 5)
		v_ind += 1

		self.contestLabel = QtWidgets.QLabel()
		self.contestLabel.setText('Contests entered: ')

		self.contestTextBox = QtWidgets.QTextEdit()
		self.contestTextBox.setFixedSize(320, 60)

		self.contestNoAction = QtWidgets.QRadioButton('No action')
		self.contestNoAction.setChecked(True)
		self.contestOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.contestAdd = QtWidgets.QRadioButton('Add to')
		self.contestDelete = QtWidgets.QRadioButton('Clear field')
		self.contestBtnGrp = QtWidgets.QButtonGroup()
		self.contestBtnGrp.setExclusive(True)
		self.contestBtnGrp.addButton(self.contestNoAction)
		self.contestBtnGrp.addButton(self.contestOverwrite)
		self.contestBtnGrp.addButton(self.contestAdd)
		self.contestBtnGrp.addButton(self.contestDelete)

		self.gridLayout.addWidget(self.contestLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.contestTextBox, v_ind, 1)
		self.gridLayout.addWidget(self.contestNoAction, v_ind, 2)
		self.gridLayout.addWidget(self.contestOverwrite, v_ind, 3)
		self.gridLayout.addWidget(self.contestAdd, v_ind, 4)
		self.gridLayout.addWidget(self.contestDelete, v_ind, 5)
		v_ind += 1

		self.gridLayout.setRowMinimumHeight(v_ind, 10)
		v_ind += 1

		self.editorYTChannelURLLabel = QtWidgets.QLabel()
		self.editorYTChannelURLLabel.setText('Editor profile URL - YouTube: ')

		self.editorYTChannelURLTextBox = QtWidgets.QLineEdit()
		self.editorYTChannelURLTextBox.setFixedWidth(320)

		self.editorYTChannelURLNoAction = QtWidgets.QRadioButton('No action')
		self.editorYTChannelURLNoAction.setChecked(True)
		self.editorYTChannelURLOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.editorYTChannelURLDelete = QtWidgets.QRadioButton('Clear field')
		self.editorYTChannelURLBtnGrp = QtWidgets.QButtonGroup()
		self.editorYTChannelURLBtnGrp.setExclusive(True)
		self.editorYTChannelURLBtnGrp.addButton(self.editorYTChannelURLNoAction)
		self.editorYTChannelURLBtnGrp.addButton(self.editorYTChannelURLOverwrite)
		self.editorYTChannelURLBtnGrp.addButton(self.editorYTChannelURLDelete)

		self.gridLayout.addWidget(self.editorYTChannelURLLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.editorYTChannelURLTextBox, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorYTChannelURLNoAction, v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorYTChannelURLOverwrite, v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorYTChannelURLDelete, v_ind, 4, 1, 2, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.editorAMVOrgChannelURLLabel = QtWidgets.QLabel()
		self.editorAMVOrgChannelURLLabel.setText('Editor profile URL - amv.org: ')

		self.editorAMVOrgChannelURLTextBox = QtWidgets.QLineEdit()
		self.editorAMVOrgChannelURLTextBox.setFixedWidth(320)

		self.editorAMVOrgChannelURLNoAction = QtWidgets.QRadioButton('No action')
		self.editorAMVOrgChannelURLNoAction.setChecked(True)
		self.editorAMVOrgChannelURLOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.editorAMVOrgChannelURLDelete = QtWidgets.QRadioButton('Clear field')
		self.editorAMVOrgChannelURLBtnGrp = QtWidgets.QButtonGroup()
		self.editorAMVOrgChannelURLBtnGrp.setExclusive(True)
		self.editorAMVOrgChannelURLBtnGrp.addButton(self.editorAMVOrgChannelURLNoAction)
		self.editorAMVOrgChannelURLBtnGrp.addButton(self.editorAMVOrgChannelURLOverwrite)
		self.editorAMVOrgChannelURLBtnGrp.addButton(self.editorAMVOrgChannelURLDelete)

		self.gridLayout.addWidget(self.editorAMVOrgChannelURLLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.editorAMVOrgChannelURLTextBox, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorAMVOrgChannelURLNoAction, v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorAMVOrgChannelURLOverwrite, v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorAMVOrgChannelURLDelete, v_ind, 4, 1, 2, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.editorAmvnewsChannelURLLabel = QtWidgets.QLabel()
		self.editorAmvnewsChannelURLLabel.setText('Editor profile URL - amvnews: ')

		self.editorAmvnewsChannelURLTextBox = QtWidgets.QLineEdit()
		self.editorAmvnewsChannelURLTextBox.setFixedWidth(320)

		self.editorAmvnewsChannelURLNoAction = QtWidgets.QRadioButton('No action')
		self.editorAmvnewsChannelURLNoAction.setChecked(True)
		self.editorAmvnewsChannelURLOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.editorAmvnewsChannelURLDelete = QtWidgets.QRadioButton('Clear field')
		self.editorAmvnewsChannelURLBtnGrp = QtWidgets.QButtonGroup()
		self.editorAmvnewsChannelURLBtnGrp.setExclusive(True)
		self.editorAmvnewsChannelURLBtnGrp.addButton(self.editorAmvnewsChannelURLNoAction)
		self.editorAmvnewsChannelURLBtnGrp.addButton(self.editorAmvnewsChannelURLOverwrite)
		self.editorAmvnewsChannelURLBtnGrp.addButton(self.editorAmvnewsChannelURLDelete)

		self.gridLayout.addWidget(self.editorAmvnewsChannelURLLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.editorAmvnewsChannelURLTextBox, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorAmvnewsChannelURLNoAction, v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorAmvnewsChannelURLOverwrite, v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorAmvnewsChannelURLDelete, v_ind, 4, 1, 2, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.editorOtherChannelURLLabel = QtWidgets.QLabel()
		self.editorOtherChannelURLLabel.setText('Editor profile URL - other: ')

		self.editorOtherChannelURLTextBox = QtWidgets.QLineEdit()
		self.editorOtherChannelURLTextBox.setFixedWidth(320)

		self.editorOtherChannelURLNoAction = QtWidgets.QRadioButton('No action')
		self.editorOtherChannelURLNoAction.setChecked(True)
		self.editorOtherChannelURLOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.editorOtherChannelURLDelete = QtWidgets.QRadioButton('Clear field')
		self.editorOtherChannelURLBtnGrp = QtWidgets.QButtonGroup()
		self.editorOtherChannelURLBtnGrp.setExclusive(True)
		self.editorOtherChannelURLBtnGrp.addButton(self.editorOtherChannelURLNoAction)
		self.editorOtherChannelURLBtnGrp.addButton(self.editorOtherChannelURLOverwrite)
		self.editorOtherChannelURLBtnGrp.addButton(self.editorOtherChannelURLDelete)

		self.gridLayout.addWidget(self.editorOtherChannelURLLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.editorOtherChannelURLTextBox, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorOtherChannelURLNoAction, v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorOtherChannelURLOverwrite, v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.editorOtherChannelURLDelete, v_ind, 4, 1, 2, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.gridLayout.setRowMinimumHeight(v_ind, 10)
		v_ind += 1

		self.favoriteLabel = QtWidgets.QLabel()
		self.favoriteLabel.setText('Favorite: ')

		self.favoriteNoAction = QtWidgets.QRadioButton('No action')
		self.favoriteNoAction.setChecked(True)
		self.favoriteSetChecked = QtWidgets.QRadioButton('Set checked')
		self.favoriteSetUnchecked = QtWidgets.QRadioButton('Set unchecked')
		self.favoriteBtnGrp = QtWidgets.QButtonGroup()
		self.favoriteBtnGrp.setExclusive(True)
		self.favoriteBtnGrp.addButton(self.favoriteNoAction)
		self.favoriteBtnGrp.addButton(self.favoriteSetChecked)
		self.favoriteBtnGrp.addButton(self.favoriteSetUnchecked)

		self.gridLayout.addWidget(self.favoriteLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.favHLayout.addWidget(self.favoriteNoAction)
		self.favHLayout.addWidget(self.favoriteSetChecked)
		self.favHLayout.addWidget(self.favoriteSetUnchecked)
		self.gridLayout.addLayout(self.favHLayout, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.notableLabel = QtWidgets.QLabel()
		self.notableLabel.setText('Notable: ')

		self.notableNoAction = QtWidgets.QRadioButton('No action')
		self.notableNoAction.setChecked(True)
		self.notableSetChecked = QtWidgets.QRadioButton('Set checked')
		self.notableSetUnchecked = QtWidgets.QRadioButton('Set unchecked')
		self.notableBtnGrp = QtWidgets.QButtonGroup()
		self.notableBtnGrp.setExclusive(True)
		self.notableBtnGrp.addButton(self.notableNoAction)
		self.notableBtnGrp.addButton(self.notableSetChecked)
		self.notableBtnGrp.addButton(self.notableSetUnchecked)

		self.gridLayout.addWidget(self.notableLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.notableHLayout.addWidget(self.notableNoAction)
		self.notableHLayout.addWidget(self.notableSetChecked)
		self.notableHLayout.addWidget(self.notableSetUnchecked)
		self.gridLayout.addLayout(self.notableHLayout, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.gridLayout.setRowMinimumHeight(v_ind, 10)
		v_ind += 1

		self.myRatingLabel = QtWidgets.QLabel()
		self.myRatingLabel.setText('My rating: ')

		self.myRatingDrop = QtWidgets.QComboBox()
		self.myRatingDrop.addItem('')
		myRatingList = [rat * 0.5 for rat in range(0, 21)]
		for rat in myRatingList:
			self.myRatingDrop.addItem(str(rat))

		self.myRatingNoAction = QtWidgets.QRadioButton('No action')
		self.myRatingNoAction.setChecked(True)
		self.myRatingUpdate = QtWidgets.QRadioButton('Update')
		self.myRatingDelete = QtWidgets.QRadioButton('Clear field')
		self.myRatingBtnGrp = QtWidgets.QButtonGroup()
		self.myRatingBtnGrp.setExclusive(True)
		self.myRatingBtnGrp.addButton(self.myRatingNoAction)
		self.myRatingBtnGrp.addButton(self.myRatingUpdate)
		self.myRatingBtnGrp.addButton(self.myRatingDelete)

		self.gridLayout.addWidget(self.myRatingLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.myRatingHLayout.addWidget(self.myRatingDrop)
		self.myRatingHLayout.addSpacing(20)
		self.myRatingHLayout.addWidget(self.myRatingNoAction)
		self.myRatingHLayout.addSpacing(13)
		self.myRatingHLayout.addWidget(self.myRatingUpdate)
		self.myRatingHLayout.addSpacing(19)
		self.myRatingHLayout.addWidget(self.myRatingDelete)
		self.gridLayout.addLayout(self.myRatingHLayout, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.starRatingLabel = QtWidgets.QLabel()
		self.starRatingLabel.setText('Star rating: ')

		self.starRatingText = QtWidgets.QLineEdit()
		self.starRatingText.setFixedWidth(50)

		self.starRatingNoAction = QtWidgets.QRadioButton('No action')
		self.starRatingNoAction.setChecked(True)
		self.starRatingUpdate = QtWidgets.QRadioButton('Update')
		self.starRatingDelete = QtWidgets.QRadioButton('Clear field')
		self.starRatingBtnGrp = QtWidgets.QButtonGroup()
		self.starRatingBtnGrp.setExclusive(True)
		self.starRatingBtnGrp.addButton(self.starRatingNoAction)
		self.starRatingBtnGrp.addButton(self.starRatingUpdate)
		self.starRatingBtnGrp.addButton(self.starRatingDelete)

		self.gridLayout.addWidget(self.starRatingLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.starRatingHLayout.addWidget(self.starRatingText)
		self.starRatingHLayout.addSpacing(18)
		self.starRatingHLayout.addWidget(self.starRatingNoAction)
		self.starRatingHLayout.addSpacing(5)
		self.starRatingHLayout.addWidget(self.starRatingUpdate)
		self.starRatingHLayout.addWidget(self.starRatingDelete)
		self.gridLayout.addLayout(self.starRatingHLayout, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.gridLayout.setRowMinimumHeight(v_ind, 10)
		v_ind += 1

		self.songArtistLabel = QtWidgets.QLabel()
		self.songArtistLabel.setText('Song artist: ')

		self.songArtistTextBox = QtWidgets.QLineEdit()
		self.songArtistTextBox.setFixedWidth(320)

		self.songArtistNoAction = QtWidgets.QRadioButton('No action')
		self.songArtistNoAction.setChecked(True)
		self.songArtistOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.songArtistDelete = QtWidgets.QRadioButton('Clear field')
		self.songArtistBtnGrp = QtWidgets.QButtonGroup()
		self.songArtistBtnGrp.setExclusive(True)
		self.songArtistBtnGrp.addButton(self.songArtistNoAction)
		self.songArtistBtnGrp.addButton(self.songArtistOverwrite)
		self.songArtistBtnGrp.addButton(self.songArtistDelete)

		self.gridLayout.addWidget(self.songArtistLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.songArtistTextBox, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.songArtistNoAction, v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.songArtistOverwrite, v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.songArtistDelete, v_ind, 4, 1, 2, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.songTitleLabel = QtWidgets.QLabel()
		self.songTitleLabel.setText('Song title: ')

		self.songTitleTextBox = QtWidgets.QLineEdit()
		self.songTitleTextBox.setFixedWidth(320)

		self.songTitleNoAction = QtWidgets.QRadioButton('No action')
		self.songTitleNoAction.setChecked(True)
		self.songTitleOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.songTitleDelete = QtWidgets.QRadioButton('Clear field')
		self.songTitleBtnGrp = QtWidgets.QButtonGroup()
		self.songTitleBtnGrp.setExclusive(True)
		self.songTitleBtnGrp.addButton(self.songTitleNoAction)
		self.songTitleBtnGrp.addButton(self.songTitleOverwrite)
		self.songTitleBtnGrp.addButton(self.songTitleDelete)

		self.gridLayout.addWidget(self.songTitleLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.songTitleTextBox, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.songTitleNoAction, v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.songTitleOverwrite, v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.songTitleDelete, v_ind, 4, 1, 2, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.songGenreLabel = QtWidgets.QLabel()
		self.songGenreLabel.setText('Song genre: ')

		self.songGenreTextBox = QtWidgets.QLineEdit()
		self.songGenreTextBox.setFixedWidth(320)

		self.songGenreNoAction = QtWidgets.QRadioButton('No action')
		self.songGenreNoAction.setChecked(True)
		self.songGenreOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.songGenreDelete = QtWidgets.QRadioButton('Clear field')
		self.songGenreBtnGrp = QtWidgets.QButtonGroup()
		self.songGenreBtnGrp.setExclusive(True)
		self.songGenreBtnGrp.addButton(self.songGenreNoAction)
		self.songGenreBtnGrp.addButton(self.songGenreOverwrite)
		self.songGenreBtnGrp.addButton(self.songGenreDelete)

		self.gridLayout.addWidget(self.songGenreLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.songGenreTextBox, v_ind, 1, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.songGenreNoAction, v_ind, 2, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.songGenreOverwrite, v_ind, 3, alignment=QtCore.Qt.AlignLeft)
		self.gridLayout.addWidget(self.songGenreDelete, v_ind, 4, 1, 2, alignment=QtCore.Qt.AlignLeft)
		v_ind += 1

		self.vidFtgLabel = QtWidgets.QLabel()
		self.vidFtgLabel.setText('Video footage: ')

		self.vidFtgTextBox = QtWidgets.QTextEdit()
		self.vidFtgTextBox.setPlaceholderText('Separate multiple footage entries with "; " (semicolon plus space)')
		self.vidFtgTextBox.setFixedSize(320, 40)

		self.vidFtgNoAction = QtWidgets.QRadioButton('No action')
		self.vidFtgNoAction.setChecked(True)
		self.vidFtgOverwrite = QtWidgets.QRadioButton('Overwrite')
		self.vidFtgAdd = QtWidgets.QRadioButton('Add to')
		self.vidFtgDelete = QtWidgets.QRadioButton('Clear field')
		self.vidFtgBtnGrp = QtWidgets.QButtonGroup()
		self.vidFtgBtnGrp.setExclusive(True)
		self.vidFtgBtnGrp.addButton(self.vidFtgNoAction)
		self.vidFtgBtnGrp.addButton(self.vidFtgOverwrite)
		self.vidFtgBtnGrp.addButton(self.vidFtgAdd)
		self.vidFtgBtnGrp.addButton(self.vidFtgDelete)

		self.gridLayout.addWidget(self.vidFtgLabel, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.gridLayout.addWidget(self.vidFtgTextBox, v_ind, 1)
		self.gridLayout.addWidget(self.vidFtgNoAction, v_ind, 2)
		self.gridLayout.addWidget(self.vidFtgOverwrite, v_ind, 3)
		self.gridLayout.addWidget(self.vidFtgAdd, v_ind, 4)
		self.gridLayout.addWidget(self.vidFtgDelete, v_ind, 5)
		v_ind += 1

		self.gridLayout.setRowMinimumHeight(v_ind, 10)
		v_ind += 1

		self.tags1Label = QtWidgets.QLabel()
		self.tags1Label.setText(tag_name_list_all_for_use[0] + ': ')

		self.tags1AddTagsBtn = QtWidgets.QPushButton('+')
		self.tags1AddTagsBtn.setFixedSize(20, 20)
		self.tags1AddTagsBtn.setToolTip('Select tag(s)')

		self.tags1TextBox = QtWidgets.QLineEdit()
		self.tags1TextBox.setReadOnly(True)
		self.tags1TextBox.setFixedWidth(290)

		self.tags1NoAction = QtWidgets.QRadioButton('No action')
		self.tags1NoAction.setChecked(True)
		self.tags1Overwrite = QtWidgets.QRadioButton('Overwrite')
		self.tags1Add = QtWidgets.QRadioButton('Add to')
		self.tags1RemoveTags = QtWidgets.QRadioButton('Remove tags')
		self.tags1Delete = QtWidgets.QRadioButton('Clear field')
		self.tags1BtnGrp = QtWidgets.QButtonGroup()
		self.tags1BtnGrp.setExclusive(True)
		self.tags1BtnGrp.addButton(self.tags1NoAction)
		self.tags1BtnGrp.addButton(self.tags1Overwrite)
		self.tags1BtnGrp.addButton(self.tags1Add)
		self.tags1BtnGrp.addButton(self.tags1RemoveTags)
		self.tags1BtnGrp.addButton(self.tags1Delete)

		self.gridLayout.addWidget(self.tags1Label, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.tags1HLayout.addWidget(self.tags1AddTagsBtn)
		self.tags1HLayout.addWidget(self.tags1TextBox)
		self.gridLayout.addLayout(self.tags1HLayout, v_ind, 1)
		self.gridLayout.addWidget(self.tags1NoAction, v_ind, 2)
		self.gridLayout.addWidget(self.tags1Overwrite, v_ind, 3)
		self.gridLayout.addWidget(self.tags1Add, v_ind, 4)
		self.gridLayout.addWidget(self.tags1RemoveTags, v_ind, 5)
		self.gridLayout.addWidget(self.tags1Delete, v_ind, 6)

		if self.tags1Label.text()[:-2] in tag_name_list_not_in_use:
			self.tags1Label.setDisabled(True)
			self.tags1AddTagsBtn.setDisabled(True)
			self.tags1TextBox.setDisabled(True)
			for btn in self.tags1BtnGrp.buttons():
				btn.setDisabled(True)
		v_ind += 1

		self.tags2Label = QtWidgets.QLabel()
		self.tags2Label.setText(tag_name_list_all_for_use[1] + ': ')

		self.tags2AddTagsBtn = QtWidgets.QPushButton('+')
		self.tags2AddTagsBtn.setFixedSize(20, 20)
		self.tags2AddTagsBtn.setToolTip('Select tag(s)')

		self.tags2TextBox = QtWidgets.QLineEdit()
		self.tags2TextBox.setReadOnly(True)
		self.tags2TextBox.setFixedWidth(290)

		self.tags2NoAction = QtWidgets.QRadioButton('No action')
		self.tags2NoAction.setChecked(True)
		self.tags2Overwrite = QtWidgets.QRadioButton('Overwrite')
		self.tags2Add = QtWidgets.QRadioButton('Add to')
		self.tags2RemoveTags = QtWidgets.QRadioButton('Remove tags')
		self.tags2Delete = QtWidgets.QRadioButton('Clear field')
		self.tags2BtnGrp = QtWidgets.QButtonGroup()
		self.tags2BtnGrp.setExclusive(True)
		self.tags2BtnGrp.addButton(self.tags2NoAction)
		self.tags2BtnGrp.addButton(self.tags2Overwrite)
		self.tags2BtnGrp.addButton(self.tags2Add)
		self.tags2BtnGrp.addButton(self.tags2RemoveTags)
		self.tags2BtnGrp.addButton(self.tags2Delete)

		self.gridLayout.addWidget(self.tags2Label, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.tags2HLayout.addWidget(self.tags2AddTagsBtn)
		self.tags2HLayout.addWidget(self.tags2TextBox)
		self.gridLayout.addLayout(self.tags2HLayout, v_ind, 1)
		self.gridLayout.addWidget(self.tags2NoAction, v_ind, 2)
		self.gridLayout.addWidget(self.tags2Overwrite, v_ind, 3)
		self.gridLayout.addWidget(self.tags2Add, v_ind, 4)
		self.gridLayout.addWidget(self.tags2RemoveTags, v_ind, 5)
		self.gridLayout.addWidget(self.tags2Delete, v_ind, 6)

		if self.tags2Label.text()[:-2] in tag_name_list_not_in_use:
			self.tags2Label.setDisabled(True)
			self.tags2AddTagsBtn.setDisabled(True)
			self.tags2TextBox.setDisabled(True)
			for btn in self.tags2BtnGrp.buttons():
				btn.setDisabled(True)
		v_ind += 1

		self.tags3Label = QtWidgets.QLabel()
		self.tags3Label.setText(tag_name_list_all_for_use[2] + ': ')

		self.tags3AddTagsBtn = QtWidgets.QPushButton('+')
		self.tags3AddTagsBtn.setFixedSize(20, 20)
		self.tags3AddTagsBtn.setToolTip('Select tag(s)')

		self.tags3TextBox = QtWidgets.QLineEdit()
		self.tags3TextBox.setReadOnly(True)
		self.tags3TextBox.setFixedWidth(290)

		self.tags3NoAction = QtWidgets.QRadioButton('No action')
		self.tags3NoAction.setChecked(True)
		self.tags3Overwrite = QtWidgets.QRadioButton('Overwrite')
		self.tags3Add = QtWidgets.QRadioButton('Add to')
		self.tags3RemoveTags = QtWidgets.QRadioButton('Remove tags')
		self.tags3Delete = QtWidgets.QRadioButton('Clear field')
		self.tags3BtnGrp = QtWidgets.QButtonGroup()
		self.tags3BtnGrp.setExclusive(True)
		self.tags3BtnGrp.addButton(self.tags3NoAction)
		self.tags3BtnGrp.addButton(self.tags3Overwrite)
		self.tags3BtnGrp.addButton(self.tags3Add)
		self.tags3BtnGrp.addButton(self.tags3RemoveTags)
		self.tags3BtnGrp.addButton(self.tags3Delete)

		self.gridLayout.addWidget(self.tags3Label, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.tags3HLayout.addWidget(self.tags3AddTagsBtn)
		self.tags3HLayout.addWidget(self.tags3TextBox)
		self.gridLayout.addLayout(self.tags3HLayout, v_ind, 1)
		self.gridLayout.addWidget(self.tags3NoAction, v_ind, 2)
		self.gridLayout.addWidget(self.tags3Overwrite, v_ind, 3)
		self.gridLayout.addWidget(self.tags3Add, v_ind, 4)
		self.gridLayout.addWidget(self.tags3RemoveTags, v_ind, 5)
		self.gridLayout.addWidget(self.tags3Delete, v_ind, 6)

		if self.tags3Label.text()[:-2] in tag_name_list_not_in_use:
			self.tags3Label.setDisabled(True)
			self.tags3AddTagsBtn.setDisabled(True)
			self.tags3TextBox.setDisabled(True)
			for btn in self.tags3BtnGrp.buttons():
				btn.setDisabled(True)
		v_ind += 1

		self.tags4Label = QtWidgets.QLabel()
		self.tags4Label.setText(tag_name_list_all_for_use[3] + ': ')

		self.tags4AddTagsBtn = QtWidgets.QPushButton('+')
		self.tags4AddTagsBtn.setFixedSize(20, 20)
		self.tags4AddTagsBtn.setToolTip('Select tag(s)')

		self.tags4TextBox = QtWidgets.QLineEdit()
		self.tags4TextBox.setReadOnly(True)
		self.tags4TextBox.setFixedWidth(290)

		self.tags4NoAction = QtWidgets.QRadioButton('No action')
		self.tags4NoAction.setChecked(True)
		self.tags4Overwrite = QtWidgets.QRadioButton('Overwrite')
		self.tags4Add = QtWidgets.QRadioButton('Add to')
		self.tags4RemoveTags = QtWidgets.QRadioButton('Remove tags')
		self.tags4Delete = QtWidgets.QRadioButton('Clear field')
		self.tags4BtnGrp = QtWidgets.QButtonGroup()
		self.tags4BtnGrp.setExclusive(True)
		self.tags4BtnGrp.addButton(self.tags4NoAction)
		self.tags4BtnGrp.addButton(self.tags4Overwrite)
		self.tags4BtnGrp.addButton(self.tags4Add)
		self.tags4BtnGrp.addButton(self.tags4RemoveTags)
		self.tags4BtnGrp.addButton(self.tags4Delete)

		self.gridLayout.addWidget(self.tags4Label, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.tags4HLayout.addWidget(self.tags4AddTagsBtn)
		self.tags4HLayout.addWidget(self.tags4TextBox)
		self.gridLayout.addLayout(self.tags4HLayout, v_ind, 1)
		self.gridLayout.addWidget(self.tags4NoAction, v_ind, 2)
		self.gridLayout.addWidget(self.tags4Overwrite, v_ind, 3)
		self.gridLayout.addWidget(self.tags4Add, v_ind, 4)
		self.gridLayout.addWidget(self.tags4RemoveTags, v_ind, 5)
		self.gridLayout.addWidget(self.tags4Delete, v_ind, 6)

		if self.tags4Label.text()[:-2] in tag_name_list_not_in_use:
			self.tags4Label.setDisabled(True)
			self.tags4AddTagsBtn.setDisabled(True)
			self.tags4TextBox.setDisabled(True)
			for btn in self.tags4BtnGrp.buttons():
				btn.setDisabled(True)
		v_ind += 1

		self.tags5Label = QtWidgets.QLabel()
		self.tags5Label.setText(tag_name_list_all_for_use[4] + ': ')

		self.tags5AddTagsBtn = QtWidgets.QPushButton('+')
		self.tags5AddTagsBtn.setFixedSize(20, 20)
		self.tags5AddTagsBtn.setToolTip('Select tag(s)')

		self.tags5TextBox = QtWidgets.QLineEdit()
		self.tags5TextBox.setReadOnly(True)
		self.tags5TextBox.setFixedWidth(290)

		self.tags5NoAction = QtWidgets.QRadioButton('No action')
		self.tags5NoAction.setChecked(True)
		self.tags5Overwrite = QtWidgets.QRadioButton('Overwrite')
		self.tags5Add = QtWidgets.QRadioButton('Add to')
		self.tags5RemoveTags = QtWidgets.QRadioButton('Remove tags')
		self.tags5Delete = QtWidgets.QRadioButton('Clear field')
		self.tags5BtnGrp = QtWidgets.QButtonGroup()
		self.tags5BtnGrp.setExclusive(True)
		self.tags5BtnGrp.addButton(self.tags5NoAction)
		self.tags5BtnGrp.addButton(self.tags5Overwrite)
		self.tags5BtnGrp.addButton(self.tags5Add)
		self.tags5BtnGrp.addButton(self.tags5RemoveTags)
		self.tags5BtnGrp.addButton(self.tags5Delete)

		self.gridLayout.addWidget(self.tags5Label, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.tags5HLayout.addWidget(self.tags5AddTagsBtn)
		self.tags5HLayout.addWidget(self.tags5TextBox)
		self.gridLayout.addLayout(self.tags5HLayout, v_ind, 1)
		self.gridLayout.addWidget(self.tags5NoAction, v_ind, 2)
		self.gridLayout.addWidget(self.tags5Overwrite, v_ind, 3)
		self.gridLayout.addWidget(self.tags5Add, v_ind, 4)
		self.gridLayout.addWidget(self.tags5RemoveTags, v_ind, 5)
		self.gridLayout.addWidget(self.tags5Delete, v_ind, 6)

		if self.tags5Label.text()[:-2] in tag_name_list_not_in_use:
			self.tags5Label.setDisabled(True)
			self.tags5AddTagsBtn.setDisabled(True)
			self.tags5TextBox.setDisabled(True)
			for btn in self.tags5BtnGrp.buttons():
				btn.setDisabled(True)
		v_ind += 1

		self.tags6Label = QtWidgets.QLabel()
		self.tags6Label.setText(tag_name_list_all_for_use[5] + ': ')

		self.tags6AddTagsBtn = QtWidgets.QPushButton('+')
		self.tags6AddTagsBtn.setFixedSize(20, 20)
		self.tags6AddTagsBtn.setToolTip('Select tag(s)')

		self.tags6TextBox = QtWidgets.QLineEdit()
		self.tags6TextBox.setReadOnly(True)
		self.tags6TextBox.setFixedWidth(290)

		self.tags6NoAction = QtWidgets.QRadioButton('No action')
		self.tags6NoAction.setChecked(True)
		self.tags6Overwrite = QtWidgets.QRadioButton('Overwrite')
		self.tags6Add = QtWidgets.QRadioButton('Add to')
		self.tags6RemoveTags = QtWidgets.QRadioButton('Remove tags')
		self.tags6Delete = QtWidgets.QRadioButton('Clear field')
		self.tags6BtnGrp = QtWidgets.QButtonGroup()
		self.tags6BtnGrp.setExclusive(True)
		self.tags6BtnGrp.addButton(self.tags6NoAction)
		self.tags6BtnGrp.addButton(self.tags6Overwrite)
		self.tags6BtnGrp.addButton(self.tags6Add)
		self.tags6BtnGrp.addButton(self.tags6RemoveTags)
		self.tags6BtnGrp.addButton(self.tags6Delete)

		self.gridLayout.addWidget(self.tags6Label, v_ind, 0, alignment=QtCore.Qt.AlignRight)
		self.tags6HLayout.addWidget(self.tags6AddTagsBtn)
		self.tags6HLayout.addWidget(self.tags6TextBox)
		self.gridLayout.addLayout(self.tags6HLayout, v_ind, 1)
		self.gridLayout.addWidget(self.tags6NoAction, v_ind, 2)
		self.gridLayout.addWidget(self.tags6Overwrite, v_ind, 3)
		self.gridLayout.addWidget(self.tags6Add, v_ind, 4)
		self.gridLayout.addWidget(self.tags6RemoveTags, v_ind, 5)
		self.gridLayout.addWidget(self.tags6Delete, v_ind, 6)

		if self.tags6Label.text()[:-2] in tag_name_list_not_in_use:
			self.tags6Label.setDisabled(True)
			self.tags6AddTagsBtn.setDisabled(True)
			self.tags6TextBox.setDisabled(True)
			for btn in self.tags6BtnGrp.buttons():
				btn.setDisabled(True)
		v_ind += 1

		self.backButton = QtWidgets.QPushButton('Back')
		self.backButton.setFixedWidth(125)
		self.submitButton = QtWidgets.QPushButton('Submit')
		self.submitButton.setFixedWidth(125)
		self.bottomBtnHLayout.addWidget(self.backButton)
		self.bottomBtnHLayout.addWidget(self.submitButton)

		# Signals / slots
		self.dlYTThumbsBtn.clicked.connect(lambda: self.dl_generate_thumbs('download'))
		self.generateThumbsBtn.clicked.connect(lambda: self.dl_generate_thumbs('generate'))
		self.deleteButton.clicked.connect(self.del_button_clicked)
		self.helpButton.clicked.connect(self.help_button_clicked)
		self.starRatingText.editingFinished.connect(self.check_star_rating)
		self.tags1AddTagsBtn.clicked.connect(
			lambda: self.tag_btn_clicked(self.tags1Label.text()[7:-2], self.tags1TextBox))
		self.tags2AddTagsBtn.clicked.connect(
			lambda: self.tag_btn_clicked(self.tags2Label.text()[7:-2], self.tags2TextBox))
		self.tags3AddTagsBtn.clicked.connect(
			lambda: self.tag_btn_clicked(self.tags3Label.text()[7:-2], self.tags3TextBox))
		self.tags4AddTagsBtn.clicked.connect(
			lambda: self.tag_btn_clicked(self.tags4Label.text()[7:-2], self.tags4TextBox))
		self.tags5AddTagsBtn.clicked.connect(
			lambda: self.tag_btn_clicked(self.tags5Label.text()[7:-2], self.tags5TextBox))
		self.tags6AddTagsBtn.clicked.connect(
			lambda: self.tag_btn_clicked(self.tags6Label.text()[7:-2], self.tags6TextBox))
		self.backButton.clicked.connect(self.close)
		self.submitButton.clicked.connect(self.submit_btn_clicked)

		# Misc
		settings_conn.close()

		# Layouts
		self.topRowHLayout.addWidget(self.dlYTThumbsBtn, alignment=QtCore.Qt.AlignLeft)
		self.topRowHLayout.addWidget(self.generateThumbsBtn, alignment=QtCore.Qt.AlignLeft)
		self.topRowHLayout.addWidget(self.deleteButton, alignment=QtCore.Qt.AlignLeft)
		self.topRowHLayout.addSpacing(400)
		self.topRowHLayout.addWidget(self.helpButton, alignment=QtCore.Qt.AlignRight)
		self.vLayoutMaster.addLayout(self.topRowHLayout)
		self.vLayoutMaster.addSpacing(10)
		self.scrollWidget.setLayout(self.gridLayout)
		self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.scrollArea.setFixedSize(900, 500)
		self.scrollArea.setWidget(self.scrollWidget)
		self.vLayoutMaster.addWidget(self.scrollArea, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addSpacing(20)
		self.vLayoutMaster.addLayout(self.bottomBtnHLayout)

		# Widget
		self.wid = QtWidgets.QWidget()
		self.wid.setLayout(self.vLayoutMaster)
		self.setCentralWidget(self.wid)
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Mass edit')
		self.setFixedSize(920, 600)
		self.wid.show()

	def dl_generate_thumbs(self, operation):
		sdb = common_vars.sub_db_lookup()[self.subdb]
		self.d_import = data_import.DataImport()
		self.d_import.get_data(operation, vidids=self.inpVidids, subdb=sdb)

	def del_button_clicked(self):
		sdb = common_vars.sub_db_lookup()[self.subdb]

		warning_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Warning',
											'Warning! You are about to mass delete video entries from AMV\n'
											'Tracker. Are you sure you want to proceed? This cannot be un-\n'
											'done.\n\nPlease note: for a large list of videos, this may take a while.',
											QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
		result = warning_win.exec_()
		if result == QtWidgets.QMessageBox.Yes:
			for v_id in self.inpVidids:
				mainwindow.MainWindow().delete_video(sdb, v_id, bypass_warning=True)

			vids_deleted = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Done',
													  'Videos have been deleted.')
			vids_deleted.exec_()
			self.close()

	def check_star_rating(self):
		try:
			float(str(self.starRatingText.text()))

			if float(self.starRatingText.text()) > 5 or float(self.starRatingText.text()) < 0:
				star_rating_range_error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
																'Star rating must be a number\nbetween 0 and 5.')
				star_rating_range_error.exec_()
				self.starRatingText.clear()
				self.starRatingText.setFocus()

		except:
			star_rating_type_error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
														   'Star rating must be a number\nbetween 0 and 5.')
			star_rating_type_error.exec_()
			self.starRatingText.clear()
			self.starRatingText.setFocus()

	def help_button_clicked(self):
		help_text = 'Some fields on each video entry can be mass updated in AMV Tracker.<br>' \
					'These fields are shown below. Any mass updates you do here will be<br>' \
					'applied to <u>all</u> videos currently displayed in the video table.<br><br>' \
					'<b>As such, please be cautious when doing any mass updates, as they</b><br>' \
					'<b>cannot be undone.</b><br><br>' \
					'Please note the radio buttons that can be pressed to indicate the type<br>' \
					'of update it will do:<br><br>' \
					'\u2022 <u>No action:</u> If checked, this field will not be updated (even if you<br>' \
					'have typed something in the corresponding text box, or selected<br>' \
					'something in the dropdown menu).<br><br>' \
					'\u2022 <u>Overwrite:</u> The value(s) you have indicated will completely overwrite<br>' \
					'whatever is currently in that field on each video.<br><br>' \
					'\u2022 <u>Add to:</u> The value(s) you have indicated will be appended to the field,<br>' \
					'and will not overwrite anything currently there.<br><br>' \
					'\u2022 <u>Clear field:</u> The field will have any existing values removed. If you<br>' \
					'have entered a new value in the corresponding text box or dropdown<br>' \
					'menu, it will be ignored.<br><br>' \
					'\u2022 <u>Remove tags:</u> (Tags only) Only the selected tag(s) will be removed (if<br>' \
					'they exist) from each video.'

		help_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Help', help_text)
		help_win.exec_()

	def tag_btn_clicked(self, tag_table, tag_text_box):
		tag_win = tag_checkboxes.TagWindow(tag_table, tag_text_box.text())
		if tag_win.exec_():
			tag_text_box.setText(tag_win.out_str[:-2])

	def submit_btn_clicked(self):
		submit_vdb_conn = sqlite3.connect(common_vars.video_db())
		submit_vdb_cursor = submit_vdb_conn.cursor()

		field_lookup_dict = common_vars.video_field_lookup()
		subdb_int = common_vars.sub_db_lookup()[self.subdb]

		overwrite_list = []  # Includes "My rating" / "Star rating"
		add_to_list = []
		clear_field_list = []
		check_upd_list = []
		remove_tags_list = []

		fav_val = ''
		notable_val = ''

		for btn in self.favoriteBtnGrp.buttons():
			if btn.isChecked() and btn.text() == 'Set checked':
				fav_val = 1
			elif btn.isChecked() and btn.text() == 'Set unchecked':
				fav_val = 0

		for btn in self.notableBtnGrp.buttons():
			if btn.isChecked() and btn.text() == 'Set checked':
				notable_val = 1
			elif btn.isChecked() and btn.text() == 'Set unchecked':
				notable_val = 0

		summary_dict = {
			self.addlEditorsBtnGrp: (self.addlEditorsLabel.text()[:-2], self.addlEditorsTextBox.text()),
			self.editorPseudBtnGrp: (self.editorPseudLabel.text()[:-2], self.editorPseudTextBox.text()),
			self.studioBtnGrp: (self.studioLabel.text()[:-2], self.studioTextBox.text()),
			self.vidDescBtnGrp: (self.vidDescLabel.text()[:-2], self.vidDescTextBox.toPlainText()),
			self.commentsBtnGrp: (self.commentsLabel.text()[:-2], self.commentsTextBox.toPlainText()),
			self.contestBtnGrp: (self.contestLabel.text()[:-2], self.contestTextBox.toPlainText()),
			self.editorYTChannelURLBtnGrp: (self.editorYTChannelURLLabel.text()[:-2], self.editorYTChannelURLTextBox.text()),
			self.editorAMVOrgChannelURLBtnGrp: (self.editorAMVOrgChannelURLLabel.text()[:-2], self.editorAMVOrgChannelURLTextBox.text()),
			self.editorAmvnewsChannelURLBtnGrp: (self.editorAmvnewsChannelURLLabel.text()[:-2], self.editorAmvnewsChannelURLTextBox.text()),
			self.editorOtherChannelURLBtnGrp: (self.editorOtherChannelURLLabel.text()[:-2], self.editorOtherChannelURLTextBox.text()),
			self.favoriteBtnGrp: (self.favoriteLabel.text()[:-2], fav_val),
			self.notableBtnGrp: (self.notableLabel.text()[:-2], notable_val),
			self.myRatingBtnGrp: (self.myRatingLabel.text()[:-2], self.myRatingDrop.currentText()),
			self.starRatingBtnGrp: (self.starRatingLabel.text()[:-2], self.starRatingText.text()),
			self.songArtistBtnGrp: (self.songArtistLabel.text()[:-2], self.songArtistTextBox.text()),
			self.songTitleBtnGrp: (self.songTitleLabel.text()[:-2], self.songTitleTextBox.text()),
			self.songGenreBtnGrp: (self.songGenreLabel.text()[:-2], self.songGenreTextBox.text()),
			self.vidFtgBtnGrp: (self.vidFtgLabel.text()[:-2], self.vidFtgTextBox.toPlainText()),
			self.tags1BtnGrp: (self.tags1Label.text()[:-2], self.tags1TextBox.text()),
			self.tags2BtnGrp: (self.tags2Label.text()[:-2], self.tags2TextBox.text()),
			self.tags3BtnGrp: (self.tags3Label.text()[:-2], self.tags3TextBox.text()),
			self.tags4BtnGrp: (self.tags4Label.text()[:-2], self.tags4TextBox.text()),
			self.tags5BtnGrp: (self.tags5Label.text()[:-2], self.tags5TextBox.text()),
			self.tags6BtnGrp: (self.tags6Label.text()[:-2], self.tags6TextBox.text()),
		}

		for k, v in summary_dict.items():
			if k.checkedButton().text() == 'Overwrite':
				overwrite_list.append((field_lookup_dict[v[0]], v[1]))

			elif k.checkedButton().text() == 'Add to':
				add_to_list.append((field_lookup_dict[v[0]], v[1]))

			elif k.checkedButton().text() == 'Clear field':
				clear_field_list.append((field_lookup_dict[v[0]], v[1]))

			elif 'check' in k.checkedButton().text():
				check_upd_list.append((field_lookup_dict[v[0]], v[1]))

			elif k.checkedButton().text() == 'Update':
				overwrite_list.append((field_lookup_dict[v[0]], v[1]))

			elif k.checkedButton().text() == 'Remove tags':
				remove_tags_list.append((field_lookup_dict[v[0]], v[1]))

		# Overwrite / clear field / update checkbox
		main_query_values = ''
		main_query_columns = []
		if overwrite_list:
			for ow_tup in overwrite_list:
				main_query_columns.append(ow_tup[0])
				main_query_values += str(ow_tup[1]) + ', '

		if check_upd_list:
			for chk_tup in check_upd_list:
				main_query_columns.append(chk_tup[0])
				main_query_values += str(chk_tup[1]) + ', '

		if clear_field_list:
			for clear_tup in clear_field_list:
				main_query_columns.append(clear_tup[0])
				main_query_values += '' + ', '

		ow_list = []
		ow_ind = 0
		if main_query_columns:
			for col in main_query_columns:
				for v_id in self.inpVidids:
					ow_list.append((main_query_values.split(', ')[:-1][ow_ind], v_id))

				submit_vdb_cursor.executemany('UPDATE {} SET {} = ? WHERE video_id = ?'.format(subdb_int, col),
											  ow_list)
				submit_vdb_conn.commit()

		# Append
		add_list = []
		if add_to_list:
			for add_tup in add_to_list:
				for v_id in self.inpVidids:
					submit_vdb_cursor.execute('SELECT {} FROM {} WHERE video_id = ?'.format(add_tup[0], subdb_int),
											  (v_id,))
					curr_val = submit_vdb_cursor.fetchone()[0]
					if 'tags_' in add_tup[0] or 'addl_' in add_tup[0] or 'pseud' in add_tup[0] or 'footage' in \
							add_tup[0]:
						curr_val_list = curr_val.split('; ')
						addl_val_list = add_tup[1].split('; ')
						if curr_val:
							new_val = '; '.join(sorted(list(set(curr_val_list + addl_val_list)),
													   key=lambda x: x.casefold()))
						else:
							new_val = add_tup[1]

					else:
						if not curr_val:
							new_val = add_tup[1]
						else:
							new_val = curr_val + '\n\n{}'.format(add_tup[1])

					add_list.append((new_val, v_id))
				submit_vdb_cursor.executemany('UPDATE {} SET {} = ? WHERE video_id = ?'.format(subdb_int, add_tup[0]),
											  add_list)
				submit_vdb_conn.commit()

		# Remove tags
		rem_list = []
		if remove_tags_list:
			for rem_tup in remove_tags_list:
				for v_id in self.inpVidids:
					submit_vdb_cursor.execute('SELECT {} FROM {} WHERE video_id = ?'.format(rem_tup[0], subdb_int),
											  (v_id,))
					curr_val = submit_vdb_cursor.fetchone()[0].split('; ')
					tags_to_rem = rem_tup[1].split('; ')
					all_tags = curr_val + tags_to_rem
					remainder = [x for x in all_tags if all_tags.count(x) == 1]
					remainder_str = '; '.join(remainder)
					rem_list.append((remainder_str, v_id))
				submit_vdb_cursor.executemany('UPDATE {} SET {} = ? WHERE video_id = ?'.format(subdb_int, rem_tup[0]),
											  rem_list)
				submit_vdb_conn.commit()

		submit_vdb_conn.close()

		msg_txt = 'Only "No action" buttons were checked -- therefore no\nvideos have been updated.'
		for k, v in summary_dict.items():
			if k.checkedButton().text() != 'No action':
				msg_txt = 'Operation completed -- filtered videos have been\nmass updated.'
				break

		msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Done', msg_txt)
		msg.exec_()
		self.close()
