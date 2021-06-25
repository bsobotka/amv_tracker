import urllib.request


def internet_check(host):
	try:
		urllib.request.urlopen(host)
		return True
	except:
		return False
