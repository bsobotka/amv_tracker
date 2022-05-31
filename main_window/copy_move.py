import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import sqlite3

from main_window import mainwindow
from misc_files import common_vars


class CopyMoveWindow(QtWidgets.QMainWindow):
	move_completed = QtCore.pyqtSignal()

	def __init__(self, vidid, subdb, copy=False):
		super(CopyMoveWindow, self).__init__()
		self.subdbFriendly = subdb
		self.subdbInternal = common_vars.sub_db_lookup()[subdb]
		self.vidid = vidid
		self.isCopy = copy
		if self.isCopy:
			self.copyText = 'Copy'
		else:
			self.copyText = 'Move'

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.checkVLayout = QtWidgets.QVBoxLayout()
		self.hLayout = QtWidgets.QHBoxLayout()
		self.scrollWidget = QtWidgets.QWidget()
		self.scrollArea = QtWidgets.QScrollArea()
		self.scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

		self.copyFromLabel = QtWidgets.QLabel()
		self.copyFromLabel.setText('{} from sub-DB: {}'.format(self.copyText, self.subdbFriendly))

		self.copyToLabel = QtWidgets.QLabel()
		self.copyToLabel.setText('{} video to following sub-DB(s):'.format(self.copyText))

		self.noteLabel = QtWidgets.QLabel()
		self.noteLabel.setText('\nPlease note: If you are accessing this function from\n'
							   'the edit screen and you have made unsubmitted changes\n'
							   'to the video entry, those changes will not be copied.\n'
							   'Please submit those changes and then copy the video if\n'
							   'you want them to carry over.\n')

		self.cancelButton = QtWidgets.QPushButton('Cancel')
		self.cancelButton.setFixedWidth(125)

		self.submitButton = QtWidgets.QPushButton('Submit')
		self.submitButton.setFixedWidth(125)

		# Layouts
		self.vLayoutMaster.addWidget(self.copyFromLabel)
		self.vLayoutMaster.addSpacing(10)
		self.vLayoutMaster.addWidget(self.copyToLabel)
		self.populate_checkboxes()
		self.scrollWidget.setLayout(self.checkVLayout)
		self.scrollArea.setWidget(self.scrollWidget)
		self.vLayoutMaster.addWidget(self.scrollArea)
		if self.isCopy:
			self.vLayoutMaster.addWidget(self.noteLabel)
		self.hLayout.addWidget(self.cancelButton)
		self.hLayout.addWidget(self.submitButton)
		self.vLayoutMaster.addLayout(self.hLayout)

		# Signals / slots
		self.cancelButton.clicked.connect(self.close)
		self.submitButton.clicked.connect(self.submit_clicked)

		# Widget
		self.wid = QtWidgets.QWidget()
		self.wid.setLayout(self.vLayoutMaster)
		self.setCentralWidget(self.wid)
		self.setWindowTitle('{} video'.format(self.copyText))
		self.setFixedSize(self.sizeHint())
		self.setFixedHeight(400)
		self.wid.show()

	def populate_checkboxes(self):
		pop_check_conn = sqlite3.connect(common_vars.video_db())
		pop_check_cursor = pop_check_conn.cursor()

		pop_check_cursor.execute('SELECT user_subdb_name FROM db_name_lookup WHERE user_subdb_name != ?',
								 (self.subdbFriendly,))
		list_of_subdbs = [x[0] for x in pop_check_cursor]
		list_of_subdbs.sort(key=lambda k: k.casefold())
		check_list = [QtWidgets.QCheckBox(x) for x in list_of_subdbs]

		for chk in check_list:
			self.checkVLayout.addWidget(chk)

		pop_check_conn.close()

	def submit_clicked(self):
		submit_conn = sqlite3.connect(common_vars.video_db())
		submit_cursor = submit_conn.cursor()
		subdb_int = common_vars.sub_db_lookup()[self.subdbFriendly]
		dbs_updated = ''
		was_db_updated = False

		submit_cursor.execute('SELECT primary_editor_username, primary_editor_pseudonyms, video_title FROM {} '
							  'WHERE video_id = ?'.format(subdb_int), (self.vidid,))
		vid_info = submit_cursor.fetchone()
		ed_name = vid_info[0]
		pseud = vid_info[1]
		vid_title = vid_info[2]

		checked_boxes = [common_vars.sub_db_lookup()[chk.text()] for chk in
						 self.checkVLayout.parentWidget().findChildren(QtWidgets.QCheckBox) if chk.isChecked()]
		checked_boxes.sort()

		if not checked_boxes:
			err_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'No sub-DBs selected',
											'You must select at least one sub-DB to {} this\n'
											'video to.'.format(self.copyText.lower()))
			err_win.exec_()
		else:
			for cbox in checked_boxes:
				submit_cursor.execute(
					'SELECT video_id FROM {} WHERE (video_title = ? AND '
					'(primary_editor_username = ? OR primary_editor_pseudonyms = ?) OR '
					'((primary_editor_username = ? OR primary_editor_pseudonyms = ?)'
					' AND primary_editor_pseudonyms != "")) OR video_id = ?'.format(cbox),
					(vid_title, ed_name, ed_name, pseud, pseud, self.vidid))
				matching_entries = submit_cursor.fetchall()

				ok_to_move = False

				if matching_entries:
					match_str = ''

					for v_id_tup in matching_entries:
						submit_cursor.execute('SELECT primary_editor_username, video_title FROM {} WHERE video_id = ?'
											  .format(cbox), (v_id_tup[0],))
						match_data = submit_cursor.fetchone()
						match_str += '{} - {}<br>'.format(match_data[0], match_data[1])

					videos_exist_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Video already in sub-DB',
															 'This video appears to already be in the sub-DB<br>'
															 '<b>{}</b>, under the following entry(ies):<br><br>{}<br><br>'
															 'Would you like to {} this video over anyway?'
															 .format(common_vars.sub_db_lookup(reverse=True)[cbox],
																	 match_str,
																	 self.copyText.lower()),
															 QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
					result = videos_exist_win.exec_()
					if result == QtWidgets.QMessageBox.Yes:
						ok_to_move = True

				else:
					ok_to_move = True

				if ok_to_move:
					submit_cursor.execute('SELECT * FROM {} WHERE video_id = ?'.format(self.subdbInternal),
										  (self.vidid,))
					data_tup = submit_cursor.fetchone()
					data_list = [data_tup[x] for x in range(1, len(data_tup))]
					new_vidid = common_vars.id_generator('video')
					data_list.insert(0, new_vidid)
					submit_cursor.execute('INSERT OR IGNORE INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '
										  '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '
										  '?, ?, ?, ?)'.format(cbox), (tuple(data_list)))
					submit_conn.commit()
					dbs_updated += common_vars.sub_db_lookup(reverse=True)[cbox]+'\n'
					was_db_updated = True

		submit_conn.close()

		if self.isCopy:
			msg_text = 'copied'
		else:
			msg_text = 'moved'

		if was_db_updated:
			vid_moved_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Done',
												  '[{} - {}] has been {} to\nfollowing sub-DB(s):\n\n'
												  '{}'.format(ed_name, vid_title, msg_text, dbs_updated))
			vid_moved_win.exec_()

			if self.isCopy is False:
				self.move_completed.emit()
			self.close()

