import sys
import traceback
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

from datetime import datetime
from os import getcwd

from main_window import mainwindow


class ErrorWindow(QtWidgets.QDialog):
	def __init__(self, msg):
		super(ErrorWindow, self).__init__()
		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.errorLabel = QtWidgets.QLabel()
		self.errorLabel.setText('An error has occurred. Please raise an issue '
								'<a href="https://github.com/bsobotka/amv_tracker/issues">here</a> and copy '
								'the below error message<br>(you can also find this message in the errors.log '
								'file, located in your AMV Tracker dir-<br>ectory, in case you need to close this '
								'window.')
		self.errorLabel.setOpenExternalLinks(True)
		self.errorTextBox = QtWidgets.QTextEdit()
		self.errorTextBox.setFixedSize(400, 200)
		self.errorTextBox.setReadOnly(True)
		self.errorTextBox.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
		self.errorTextBox.setText(msg)

		self.okButton = QtWidgets.QPushButton('OK')
		self.okButton.setFixedWidth(125)

		# Layout
		self.vLayoutMaster.addWidget(self.errorLabel)
		self.vLayoutMaster.addSpacing(10)
		self.vLayoutMaster.addWidget(self.errorTextBox)
		self.vLayoutMaster.addSpacing(10)
		self.vLayoutMaster.addWidget(self.okButton, alignment=QtCore.Qt.AlignRight)

		# Signals / slots
		self.okButton.clicked.connect(self.accept)

		# Widget
		self.setLayout(self.vLayoutMaster)
		self.setFixedSize(self.sizeHint())
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Error')
		self.show()


def error_handler(etype, value, tb):
	# Writes error messages to errors.log file
	todays_date = datetime.now().strftime('%Y-%m-%d, %H:%M:%S')
	error_msg = ''.join(traceback.format_exception(etype, value, tb))
	with open('errors.log', 'a') as f:
		f.write('\n' + todays_date + '\n' + error_msg)

	err_win = ErrorWindow(msg=error_msg)
	err_win.exec_()
	QtWidgets.QApplication.quit()


if __name__ == '__main__':
	# TODO: Uncomment below line before freezing code
	sys.excepthook = error_handler

	app = QtWidgets.QApplication(sys.argv)
	main_win = mainwindow.MainWindow()
	main_win.show()
	sys.exit(app.exec_())
