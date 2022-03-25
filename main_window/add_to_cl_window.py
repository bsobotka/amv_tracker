import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import sqlite3

from misc_files import common_vars


class AddToCustList(QtWidgets.QMainWindow):
	def __init__(self, vidid):
		super(AddToCustList, self).__init__()

		self.vidid = vidid

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.checkVLayout = QtWidgets.QVBoxLayout()
		self.hLayout = QtWidgets.QHBoxLayout()
		self.scrollWidget = QtWidgets.QWidget()
		self.scrollArea = QtWidgets.QScrollArea()
		self.scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

		self.descLabel = QtWidgets.QLabel()
		self.descLabel.setText('Please select the custom list(s) you\'d like to add this\n'
							   'video to.\n\n'
							   'Please note that if any of the lists below are checked\n'
							   'and you uncheck them before submitting, the video will\n'
							   'be removed from that custom list.')

		self.cancelButton = QtWidgets.QPushButton('Cancel')
		self.cancelButton.setFixedWidth(125)

		self.submitButton = QtWidgets.QPushButton('Submit')
		self.submitButton.setFixedWidth(125)

		# Layouts
		self.vLayoutMaster.addWidget(self.descLabel)
		self.populate_checkboxes()
		self.scrollWidget.setLayout(self.checkVLayout)
		self.scrollArea.setWidget(self.scrollWidget)
		self.vLayoutMaster.addWidget(self.scrollArea)
		self.hLayout.addWidget(self.cancelButton)
		self.hLayout.addWidget(self.submitButton)
		self.vLayoutMaster.addLayout(self.hLayout)

		# Signals / slots
		self.cancelButton.clicked.connect(self.close)
		self.submitButton.clicked.connect(self.submit)

		# Widget
		self.wid = QtWidgets.QWidget()
		self.wid.setLayout(self.vLayoutMaster)
		self.setCentralWidget(self.wid)
		self.setWindowTitle('Custom lists')
		self.setFixedSize(self.sizeHint())
		self.setFixedHeight(400)
		self.wid.show()

	def populate_checkboxes(self):
		video_db_conn = sqlite3.connect(common_vars.video_db())
		video_db_cursor = video_db_conn.cursor()

		video_db_cursor.execute('SELECT list_name FROM custom_lists')
		all_cust_lists = [x[0] for x in video_db_cursor.fetchall()]
		all_cust_lists.sort(key=lambda x: x.casefold())

		video_db_cursor.execute('SELECT list_name FROM custom_lists WHERE vid_ids LIKE "%{}%"'.format(self.vidid))
		vid_exists_list = [x[0] for x in video_db_cursor.fetchall()]

		list_of_checks = [QtWidgets.QCheckBox(cl) for cl in all_cust_lists]
		for chk in list_of_checks:
			self.checkVLayout.addWidget(chk)
			if chk.text() in vid_exists_list:
				chk.setChecked(True)

		video_db_conn.close()

	def submit(self):
		submit_conn = sqlite3.connect(common_vars.video_db())
		submit_cursor = submit_conn.cursor()

		checked_boxes = [chk.text() for chk in self.checkVLayout.parentWidget().findChildren(QtWidgets.QCheckBox) if
						 chk.isChecked()]
		unchecked_boxes = [chk.text() for chk in self.checkVLayout.parentWidget().findChildren(QtWidgets.QCheckBox) if
						   not chk.isChecked()]
		all_boxes = checked_boxes + unchecked_boxes

		if len(checked_boxes) == 0:
			nothing_selected = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Nothing selected',
													 'No custom lists were selected, therefore no\n'
													 'action has been taken.')
			nothing_selected.exec_()

		else:
			for box in all_boxes:
				submit_cursor.execute('SELECT vid_ids FROM custom_lists WHERE list_name = ?', (box,))
				vidid_str = submit_cursor.fetchone()[0]
				if box in checked_boxes and self.vidid not in vidid_str:
					vidid_str += '; {}'.format(self.vidid)
					submit_cursor.execute('UPDATE custom_lists SET vid_ids = ? WHERE list_name = ?', (vidid_str, box))
					submit_conn.commit()

				elif box in unchecked_boxes and self.vidid in vidid_str:
					vidid_list = vidid_str.split('; ')
					vidid_list.remove(self.vidid)
					upd_str = '; '.join(vidid_list)
					submit_cursor.execute('UPDATE custom_lists SET vid_ids = ? WHERE list_name = ?', (upd_str, box))
					submit_conn.commit()

			op_completed = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Lists updated',
												 'Custom lists have been updated.')
			op_completed.exec_()

		submit_conn.close()
		self.close()
