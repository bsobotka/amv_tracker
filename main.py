import sys
import PyQt5.QtWidgets as QtWidgets
from homewindow import homewindow

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	mainWindow = homewindow.HomeWindow()
	mainWindow.show()
	sys.exit(app.exec_())