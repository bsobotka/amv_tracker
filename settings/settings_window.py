import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

from os import getcwd

from misc_files import check_for_db
from settings import data_management_settings, data_import, library_management, search_settings, tag_management, \
	video_entry_settings


class SettingsWindow(QtWidgets.QMainWindow):
	window_closed = QtCore.pyqtSignal()

	def __init__(self):
		super(SettingsWindow, self).__init__()

		# Check that .db file exists
		check_for_db.check_for_db()

		# Top-level layouts/widgets
		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.blankLayout = QtWidgets.QVBoxLayout()
		self.settingsTabs = QtWidgets.QTabWidget()

		self.dataImportTab = QtWidgets.QWidget()
		self.entryTab = QtWidgets.QWidget()
		self.searchTab = QtWidgets.QWidget()
		self.dataMgmtTab = QtWidgets.QWidget()
		self.tagMgmtTab = QtWidgets.QWidget()
		self.libMgmtTab = QtWidgets.QWidget()

		self.settingsTabs.addTab(self.dataImportTab, 'Data import')
		self.settingsTabs.addTab(self.entryTab, 'Video entry')
		self.settingsTabs.addTab(self.searchTab, 'Search display')
		self.settingsTabs.addTab(self.dataMgmtTab, 'Data management')
		self.settingsTabs.addTab(self.tagMgmtTab, 'Tag management')
		self.settingsTabs.addTab(self.libMgmtTab, 'Library management')

		# Signals/slots
		self.settingsTabs.currentChanged.connect(self.tab_changed)

		self.generalSettingsScreen = data_import.DataImport()
		self.entryScreen = video_entry_settings.VideoEntrySettings()
		self.searchScreen = search_settings.SearchSettings()
		self.dataMgmtScreen = data_management_settings.DataMgmtSettings()
		self.tagMgmtScreen = tag_management.TagManagement()
		self.libMgmtScreen = library_management.LibraryManagement()

		# Layouts
		self.dataImportTab.setLayout(self.generalSettingsScreen.gridLayout)
		self.entryTab.setLayout(self.entryScreen.vLayoutMaster)
		self.searchTab.setLayout(self.searchScreen.vLayoutMaster)
		self.dataMgmtTab.setLayout(self.dataMgmtScreen.gridLayout)
		self.tagMgmtTab.setLayout(self.tagMgmtScreen.editTagsGridLayout)
		self.libMgmtTab.setLayout(self.libMgmtScreen.gridLayoutMaster)
		self.vLayoutMaster.addWidget(self.settingsTabs)

		# Widget
		self.wid = QtWidgets.QWidget()
		self.wid.setLayout(self.vLayoutMaster)
		self.setCentralWidget(self.wid)
		self.setWindowIcon(QtGui.QIcon(getcwd() + '/icons/amvt-logo.png'))
		self.setWindowTitle('Settings')
		self.setFixedSize(self.sizeHint())
		self.wid.show()

	def closeEvent(self, event):
		self.window_closed.emit()
		event.accept()

	def tab_changed(self, i):
		check_for_db.check_for_db()
		if i == 1:
			self.entryScreen.refresh_checkboxes()
		elif i == 4:
			self.tagMgmtScreen.populate_tag_widgets(self.tagMgmtScreen.tagTypeListWid)
			self.tagMgmtScreen.enable_tag_buttons(self.tagMgmtScreen.tagTypeListWid, tab_change=True)
		elif i == 5:
			self.libMgmtScreen.dataTypeListWid.clearSelection()
			self.libMgmtScreen.dataListWid.clear()
