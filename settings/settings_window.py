import PyQt5.QtWidgets as QtWidgets

from settings import tag_management, video_entry_settings, data_management_settings_, search_settings


class SettingsWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(SettingsWindow, self).__init__()

		# Top-level layouts/widgets
		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.blankLayout = QtWidgets.QVBoxLayout()
		self.settingsTabs = QtWidgets.QTabWidget()

		self.generalTab = QtWidgets.QWidget()
		self.entryTab = QtWidgets.QWidget()
		self.searchTab = QtWidgets.QWidget()
		self.dataMgmtTab = QtWidgets.QWidget()
		self.tagMgmtTab = QtWidgets.QWidget()

		self.settingsTabs.addTab(self.generalTab, 'General')
		self.settingsTabs.addTab(self.entryTab, 'Video entry')
		self.settingsTabs.addTab(self.searchTab, 'Video search')
		self.settingsTabs.addTab(self.dataMgmtTab, 'Data management')
		self.settingsTabs.addTab(self.tagMgmtTab, 'Tag management')

		# Signals/slots
		self.settingsTabs.currentChanged.connect(self.tab_changed)

		# Layouts
		self.entryTab.setLayout(video_entry_settings.VideoEntrySettings().vLayoutMaster)
		self.searchTab.setLayout(search_settings.SearchSettings().vLayoutMaster)
		self.tagMgmtTab.setLayout(tag_management.TagManagement().editTagsGridLayout)
		self.dataMgmtTab.setLayout(data_management_settings_.DataMgmtSettings().gridLayout)
		self.vLayoutMaster.addWidget(self.settingsTabs)

		# Widget
		self.wid = QtWidgets.QWidget()
		self.wid.setLayout(self.vLayoutMaster)
		self.setCentralWidget(self.wid)
		self.setWindowTitle('Settings')
		self.setFixedSize(self.sizeHint())
		self.wid.show()

	def tab_changed(self, ind):
		if ind == 1:
			pass
