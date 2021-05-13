import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore


class AddlEditorsWindow(QtWidgets.QDialog):
	def __init__(self, prim_editor, inp_ed_str):
		super(AddlEditorsWindow, self).__init__()

		hLayout1 = QtWidgets.QHBoxLayout()
		hLayout2 = QtWidgets.QHBoxLayout()
		vLayoutMaster = QtWidgets.QVBoxLayout()

		self.prim_editor = prim_editor
		self.inp_ed_str = inp_ed_str

		self.primEditorLabel = QtWidgets.QLabel()
		self.primEditorLabel.setText('Primary editor: ' + prim_editor)

		self.addlEditorsLabel = QtWidgets.QLabel()
		self.addlEditorsLabel.setText('Additional editors:')
		self.addlEditorsBox = QtWidgets.QTextEdit()
		self.addlEditorsBox.setPlaceholderText('Please enter one editor username per line')
		self.addlEditorsBox.setFixedSize(150, 400)

		if self.inp_ed_str != '':
			self.edBoxString = ''
			for ed_name in self.inp_ed_str.split('; '):
				if ed_name != '':
					self.edBoxString += ed_name + '\n'
			self.addlEditorsBox.setText(self.edBoxString)

		self.backButton = QtWidgets.QPushButton('Back')
		self.submitButton = QtWidgets.QPushButton('Submit')

		# Signals/slots
		self.backButton.clicked.connect(self.back_button)
		self.submitButton.clicked.connect(self.text_added)

		# Layout
		vLayoutMaster.addWidget(self.primEditorLabel)
		vLayoutMaster.addSpacing(20)
		hLayout1.addWidget(self.addlEditorsLabel, alignment=QtCore.Qt.AlignTop)
		hLayout1.addWidget(self.addlEditorsBox)
		vLayoutMaster.addLayout(hLayout1)
		hLayout2.addWidget(self.backButton)
		hLayout2.addWidget(self.submitButton)
		vLayoutMaster.addLayout(hLayout2)

		# Widget
		self.setLayout(vLayoutMaster)
		self.setWindowTitle('Add addl editors')
		self.setFixedSize(self.sizeHint())
		self.show()

	def back_button(self):
		self.out_str = self.inp_ed_str
		self.accept()

	def text_added(self):
		self.output_lst = self.addlEditorsBox.toPlainText().split('\n')
		self.output_lst_deduped = []
		if '' in self.output_lst:
			self.output_lst.remove('')
		marker = set()

		# Remove duplicate editor names from list regardless of case
		for ed in self.output_lst:
			if ed.lower() not in marker:
				marker.add(ed.lower())
				self.output_lst_deduped.append(ed)

		# Check that none of the names entered are the primary editor
		for ed_name in self.output_lst_deduped:
			if ed_name.lower() == self.prim_editor.lower():
				self.msgBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Notice',
					                                    '{} is already listed as the primary editor in this video entry.\n'
					                                    'This username has been removed from the list.'.format(self.prim_editor),
					                                    QtWidgets.QMessageBox.Ok)
				self.msgBox.exec_()

		self.output_lst_deduped.sort(key=lambda x: x.lower())
		self.out_str = ''
		for ed in self.output_lst_deduped:
			if ed != '' and ed.lower() != self.prim_editor.lower():
				self.out_str += ed + '; '

		self.accept()

