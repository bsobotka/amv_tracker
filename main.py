import sys
import PyQt5.QtWidgets as QtWidgets
from main_window import mainwindow

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	main_win = mainwindow.MainWindow()
	main_win.showMaximized()
	sys.exit(app.exec_())