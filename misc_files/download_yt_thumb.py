import PyQt5.QtWidgets as QtWidgets

from misc_files import check_for_thumb_path, common_vars

from os import path
from urllib import error, parse, request


def download(vidid, url, bypass_check=False):
	"""
	Downloads thumbnail from YouTube (if available) and returns the path to the file as a string. If the download fails,
	returns string 'failed'.
	"""

	url_data = parse.urlparse(url)
	query = parse.parse_qs(url_data.query)
	yt_id = query['v'][0]
	save_path = common_vars.thumb_path() + '\\{}.jpg'.format(vidid)
	ok_to_proceed = True

	check_for_thumb_path.check_for_thumb_path()

	if path.isfile(save_path) and not bypass_check:
		thumb_exists_popup = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Overwrite thumbnail?',
												   'A thumbnail already exists for this video.\n'
												   'OK to overwrite?',
												   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
		result = thumb_exists_popup.exec_()

		if result == QtWidgets.QMessageBox.No:
			ok_to_proceed = False

	if ok_to_proceed:
		try:
			request.urlretrieve('https://img.youtube.com/vi/{}/maxresdefault.jpg'.format(yt_id), save_path)
			out_str = save_path

		except error.HTTPError:
			try:
				request.urlretrieve('https://img.youtube.com/vi/{}/0.jpg'.format(yt_id), save_path)
				out_str = save_path

			except:
				out_str = 'failed'

	else:
		out_str = 'no action'

	return out_str

