from os import getcwd
from urllib import error, parse, request


def download(vidid, url):
	"""
	Downloads thumbnail from YouTube (if available) and returns the path to the file as a string. If the download fails,
	returns string 'failed'.
	"""

	url_data = parse.urlparse(url)
	query = parse.parse_qs(url_data.query)
	yt_id = query['v'][0]
	save_path = getcwd() + '\\thumbnails\\{}.jpg'.format(vidid)

	try:
		request.urlretrieve('https://img.youtube.com/vi/{}/maxresdefault.jpg'.format(yt_id), save_path)
		out_str = save_path

	except error.HTTPError:
		try:
			request.urlretrieve('https://img.youtube.com/vi/{}/0.jpg'.format(yt_id), save_path)
			out_str = save_path

		except:
			out_str = 'failed'

	return out_str

