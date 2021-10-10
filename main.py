import sys
import PyQt5.QtWidgets as QtWidgets
from main_window import mainwindow

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	main_win = mainwindow.MainWindow()
	#main_win.showMaximized()
	main_win.show()
	sys.exit(app.exec_())