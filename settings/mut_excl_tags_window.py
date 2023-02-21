import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import sqlite3

from os import getcwd

from misc_files import common_vars, check_for_db


class MutuallyExclTagsWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(MutuallyExclTagsWindow, self).__init__()

		# Initialize SQLite connections
		tag_conn = sqlite3.connect(common_vars.video_db())
		tag_cursor = tag_conn.cursor()

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.vLayoutMaster.setAlignment(QtCore.Qt.AlignTop)
		self.hLayout1 = QtWidgets.QHBoxLayout()
		self.hLayout2 = QtWidgets.QHBoxLayout()
		self.hLayout3 = QtWidgets.QHBoxLayout()
		self.hLayoutBottom = QtWidgets.QHBoxLayout()

		self.scrollWid = QtWidgets.QWidget()
		self.scrollArea = QtWidgets.QScrollArea()
		self.scrollVLayout = QtWidgets.QVBoxLayout()
		self.scrollVLayout.setAlignment(QtCore.Qt.AlignTop)

		self.label1 = QtWidgets.QLabel()
		self.label1.setText('From here you can set tags within a single tag group to be\n'
		                    '"mutually exclusive", meaning that when a given tag is\n'
		                    'checked on data entry, any tags you identify here will be\n'
		                    'disabled automatically so that you cannot check them. This\n'
		                    'is useful to keep tag choices and data consistent as you\n'
		                    'enter videos into AMV Tracker.')

		self.label2 = QtWidgets.QLabel()
		self.label2.setText('Select the tag category:')
		self.tagGroupDrop = QtWidgets.QComboBox()
		self.tagGroupDrop.setFixedWidth(150)
		tag_cursor.execute('SELECT user_field_name FROM tags_lookup WHERE in_use = ?', ('1',))
		self.tagGroupList = [t[0] for t in tag_cursor.fetchall()]
		self.tagGroupList.sort(key=lambda x: x.casefold())
		for tag in self.tagGroupList:
			self.tagGroupDrop.addItem(tag)
		
		self.label3 = QtWidgets.QLabel()
		self.label3.setText('If this tag is checked... -->')
		self.tagNameDrop = QtWidgets.QComboBox()
		self.tagNameDrop.setFixedWidth(150)
		self.populate_tag_name_drop()
		
		self.label4 = QtWidgets.QLabel()
		self.label4.setText('...then prevent the following\ntag(s) from being checkable:')
		self.populate_scroll_area(self.tagNameDrop.count())
	
		self.saveButton = QtWidgets.QPushButton('Save changes')
		self.saveButton.setFixedWidth(100)
		self.closeButton = QtWidgets.QPushButton('Close')
		self.closeButton.setFixedWidth(100)

		# Scroll layout
		self.scrollWid.setLayout(self.scrollVLayout)
		self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.scrollArea.setFixedSize(200, 200)
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setWidget(self.scrollWid)
		
		# Layouts
		self.vLayoutMaster.addWidget(self.label1, alignment=QtCore.Qt.AlignCenter)
		self.vLayoutMaster.addSpacing(20)
		
		self.hLayout1.addWidget(self.label2)
		self.hLayout1.addWidget(self.tagGroupDrop)
		self.vLayoutMaster.addLayout(self.hLayout1)
		
		self.hLayout2.addWidget(self.label3)
		self.hLayout2.addWidget(self.tagNameDrop)
		self.vLayoutMaster.addLayout(self.hLayout2)

		self.hLayout3.addWidget(self.label4, alignment=QtCore.Qt.AlignTop)
		self.hLayout3.addWidget(self.scrollArea)
		self.vLayoutMaster.addLayout(self.hLayout3)
		
		self.hLayoutBottom.addWidget(self.closeButton, alignment=QtCore.Qt.AlignLeft)
		self.hLayoutBottom.addWidget(self.saveButton, alignment=QtCore.Qt.AlignRight)
		self.vLayoutMaster.addLayout(self.hLayoutBottom)
		
		# Signals / slots
		self.closeButton.clicked.connect(self.close)
		self.tagGroupDrop.currentIndexChanged.connect(self.populate_tag_name_drop)
		self.tagNameDrop.currentIndexChanged.connect(lambda: self.populate_scroll_area(self.tagNameDrop.count()))
		self.saveButton.clicked.connect(self.save_button_clicked)

		# Close db conn
		tag_conn.close()
		
		# Widget
		self.wid = QtWidgets.QWidget()
		self.wid.setLayout(self.vLayoutMaster)
		self.setCentralWidget(self.wid)
		self.setFixedSize(self.sizeHint())
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Mutually exclusive tags')
		self.show()

	def populate_tag_name_drop(self):
		self.tagNameDrop.clear()
		group_w_name = common_vars.tag_group_w_tag_names('user')
		for group, tags in group_w_name.items():
			if group.casefold() == self.tagGroupDrop.currentText().casefold():
				tags.sort(key=lambda x: x.casefold())
				for t in tags:
					self.tagNameDrop.addItem(t)

	def populate_scroll_area(self, ct):
		for i in reversed(range(self.scrollVLayout.count())):
			self.scrollVLayout.itemAt(i).widget().setParent(None)
		pop_scroll_area_conn = sqlite3.connect(common_vars.video_db())
		pop_scroll_area_cursor = pop_scroll_area_conn.cursor()

		tag_name_dict = common_vars.tag_table_lookup()
		curr_tag_name = self.tagNameDrop.currentText()
		curr_tag_grp = self.tagGroupDrop.currentText()
		curr_tag_grp_int = tag_name_dict[curr_tag_grp]

		pop_scroll_area_cursor.execute('SELECT tag_name, disable_tags FROM {} WHERE tag_name != ?'
		                               .format(curr_tag_grp_int), (curr_tag_name,))
		cboxes = [QtWidgets.QCheckBox(x[0]) for x in pop_scroll_area_cursor.fetchall()]
		cboxes.sort(key=lambda x: x.text().casefold())

		if ct > 0:  # Ignores trigger from clear() func in populate_tag_name_drop
			pop_scroll_area_cursor.execute('SELECT disable_tags FROM {} WHERE tag_name = ?'
			                               .format(curr_tag_grp_int), (curr_tag_name,))
			dis_tags = pop_scroll_area_cursor.fetchone()[0]

			if dis_tags:
				tags_to_disable = dis_tags.split('; ')
			else:
				tags_to_disable = []

			for box in cboxes:
				for t in tags_to_disable:
					if box.text() == t:
						box.setChecked(True)
				self.scrollVLayout.addWidget(box)

		pop_scroll_area_conn.close()

	def save_button_clicked(self):
		save_conn = sqlite3.connect(common_vars.video_db())
		save_cursor = save_conn.cursor()

		checked_boxes = [self.scrollVLayout.itemAt(ind).widget().text() for ind in range(0, self.scrollVLayout.count())
		                 if self.scrollVLayout.itemAt(ind).widget().isChecked()]
		tags_to_disable = '; '.join(checked_boxes)
		sel_tag_grp = common_vars.tag_table_lookup()[self.tagGroupDrop.currentText()]
		sel_tag_name = self.tagNameDrop.currentText()

		# Updating tag with list of mutually exclusive tags
		save_cursor.execute('UPDATE {} SET disable_tags = ? WHERE tag_name = ?'.format(sel_tag_grp),
		                    (tags_to_disable, sel_tag_name))

		# Inverse of above
		for tag in checked_boxes:
			save_cursor.execute('SELECT disable_tags FROM {} WHERE tag_name = ?'.format(sel_tag_grp), (tag,))
			curr_dis_tags_list = save_cursor.fetchone()[0]
			if curr_dis_tags_list:
				curr_dis_tags = curr_dis_tags_list.split('; ')
			else:
				curr_dis_tags = []

			if sel_tag_name not in curr_dis_tags:
				curr_dis_tags.append(sel_tag_name)

			new_dis_tags = '; '.join(curr_dis_tags)
			save_cursor.execute('UPDATE {} SET disable_tags = ? WHERE tag_name = ?'.format(sel_tag_grp),
			                    (new_dis_tags, tag))
		save_conn.commit()

		# Removing deleted relationships
		save_cursor.execute('SELECT disable_tags FROM {} WHERE tag_name = ?'.format(sel_tag_grp), (sel_tag_name,))
		dis_tags_upd_str = save_cursor.fetchone()[0]
		if dis_tags_upd_str:
			dis_tags_upd_list = dis_tags_upd_str.split('; ')
		else:
			dis_tags_upd_list = []

		suspect_tag_list = [k for k, v in common_vars.tag_desc_lookup(self.tagGroupDrop.currentText()).items()
		                    if k not in dis_tags_upd_list]

		save_cursor.execute('SELECT tag_name, disable_tags FROM {} WHERE disable_tags LIKE "%"||?||"%"'
		                    .format(sel_tag_grp), (sel_tag_name,))
		upd_dict = {x[0]: x[1].split('; ') for x in save_cursor.fetchall() if x[0] in suspect_tag_list}
		for k, v in upd_dict.items():
			upd_dict[k] = v.remove(sel_tag_name)
			upd_dict[k] = '; '.join(v)

		for key, val in upd_dict.items():
			save_cursor.execute('UPDATE {} SET disable_tags = ? WHERE tag_name = ?'.format(sel_tag_grp), (val, key))

		save_completed_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Saved',
		                                           'The specified tag relationships have been updated.')
		save_completed_win.exec_()

		save_conn.commit()
		save_conn.close()
