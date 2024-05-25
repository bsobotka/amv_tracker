import sys
import traceback
import PyQt5.QtWidgets as QtWidgets

from datetime import datetime

from main_window import mainwindow


def error_handler(etype, value, tb):
	# Writes error messages to errors.log file
	todays_date = datetime.now().strftime('%Y-%m-%d, %H:%M:%S')
	error_msg = ''.join(traceback.format_exception(etype, value, tb))
	with open('errors.log', 'a') as f:
		f.write('\n' + todays_date + '\n' + error_msg)
	err_msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
									'An error has occurred. Please raise an issue<br>'
									'<a href="https://github.com/bsobotka/amv_tracker/issues">here</a> '
									'and provide a copy of your errors.log file,<br>'
									'found in the AMV Tracker directory.<br><br>'
									'Error traceback:<br>{}'.format(error_msg))
	err_msg.exec_()
	QtWidgets.QApplication.quit()


if __name__ == '__main__':
	## TODO: Uncomment below line before freezing code
	sys.excepthook = error_handler

	app = QtWidgets.QApplication(sys.argv)
	main_win = mainwindow.MainWindow()
	main_win.show()
	sys.exit(app.exec_())
