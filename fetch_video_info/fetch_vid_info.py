import requests

from bs4 import BeautifulSoup as beautifulsoup
from urllib import parse


def download_data(url, site):
	"""
	:param site: "org" for a-m-v.org, or "youtube" for YouTube
	:param url: a-m-v.org video profile URL or YouTube channel URL to parse
	:return: dict with {data_label: value}
	"""

	if site == 'org':
		r = requests.get(url)
		soup = beautifulsoup(r.content, 'html5lib')

		editor_info = soup.find('div', {'id': 'videoInformation'}).find('ul').find_all('li')
		editors = editor_info[0].get_text().strip().split(':')[1].strip().split(', ')
		"""try:
			editors = editor_info[0].get_text().strip().split('ember:')[1].strip().split(', ')
		except:
			editors = editor_info[0].get_text().strip().split('):')[1].strip().split(', ')"""
		ed_name = editors[0]

		if len(ed_name) > 1:
			addl_ed = '; '.join(editors[1:])
		else:
			addl_ed = ''

		vid_title = soup.find('span', {'class': 'videoTitle'}).get_text().strip()
		studio = soup.find('span', {'class': 'videoStudio'})
		if studio is not None:
			studio = studio.get_text().strip()
		else:
			studio = ''

		try:
			rel_date = soup.find('span', {'class': 'videoPremiere'}).get_text().strip()
			rel_date_year = str(rel_date[:4])
			rel_date_mo = int(rel_date[5:7])
			rel_date_day = int(rel_date[8:])
		except:
			rel_date_year = ''
			rel_date_mo = 0
			rel_date_day = 0

		song_artist_html = soup.find_all('span', attrs={'class': 'artist'})
		song_artist_all = [elem.get_text().strip() for elem in song_artist_html]
		if len(list(set(song_artist_all))) == 1:
			song_artist = song_artist_all[0]
		else:
			song_artist = 'Various'

		song_title_html = soup.find_all('span', attrs={'class': 'song'})
		song_title_all = [elem.get_text().strip() for elem in song_title_html]
		if len(song_title_all) > 1:
			song_title = 'Various'
		else:
			song_title = song_title_all[0]

		anime_nonspoiler_html = soup.find('ul', {'class': 'videoAnime'}).find_all('a', attrs={'class': 'anime'})
		anime_spoiler_html = soup.find('ul', {'class': 'videoAnime'}).find_all('a', attrs={'class': 'animeSpoiler'})
		anime_all = [elem.get_text().strip() for elem in anime_nonspoiler_html] + [elem.get_text().strip() for elem
																				   in anime_spoiler_html]
		anime_all.sort(key=lambda x: x.casefold())

		list_of_anime_suffixes = [' (TV)', ' (OAV)', ' (OVA)', ' (ONA)', ' (Movie)', ' (movie)', ' (TV series)']
		anime_all_fixed = []

		for an in anime_all:
			needs_replacing = False
			suffix_to_replace = ''
			for suffix in list_of_anime_suffixes:
				if suffix in an:
					needs_replacing = True
					suffix_to_replace = suffix

			if needs_replacing:
				anime_all_fixed.append(an.replace(suffix_to_replace, ''))
			else:
				anime_all_fixed.append(an)

		anime_all_fixed.sort(key=lambda x: x.casefold())

		try:
			contests_confirmed_html = soup.find('ul', {'class': 'videoParticipation'}).find_all('li', attrs={'class',
																											 'confirmed'})
			contests_pending_html = soup.find('ul', {'class': 'videoParticipation'}).find_all('li',
																							  attrs={'class', 'pending'})
			contests_all = [elem.get_text().strip() for elem in contests_confirmed_html] + [elem.get_text().strip() for
																							elem in contests_pending_html]

			contests_final = []
			for con in contests_all:
				contests_final.append(con.split(', ')[0])
			contests = '; '.join(contests_final)
		except:
			contests = ''

		vid_desc = soup.find('span', {'class': 'comments'}).get_text().strip()

		yt_link = ''
		amvnews_link = ''
		other_link = ''
		try:
			links_html = soup.find('div', {'id': 'downloads'}).find_all('a')
			links = [parse.unquote(lnk.get('href')) for lnk in links_html]
			for lnk in links:
				if 'youtube' in lnk:
					yt_link = lnk.split('url=')[1]
				elif 'amvnews' in lnk:
					amvnews_link = lnk.split('url=')[1]
				elif 'localdownload' not in lnk:
					other_link = lnk.split('url=')[1]
		except:
			pass

		try:
			duration = soup.find('div', {'id': 'downloads'}).find('li', {'class': 'local'}).find('span', {'class': 'duration'})
			dur_min = int(duration.get_text().strip().split(':')[0])
			dur_sec = int(duration.get_text().strip().split(':')[1])
		except:
			dur_min = -1
			dur_sec = -1

		editor_profile = soup.find('div', {'id': 'videoInformation'}).find('ul').find('li').find('a')
		editor_profile_link = 'https://www.animemusicvideos.org' + editor_profile.get('href')

		out_dict = {
			'primary_editor_username': ed_name,
			'addl_editors': addl_ed,
			'studio': studio,
			'video_title': vid_title,
			'release_date': [rel_date_year, rel_date_mo, rel_date_day],
			'video_footage': anime_all_fixed,
			'song_artist': song_artist,
			'song_title': song_title,
			'video_length': [dur_min, dur_sec],
			'contests_entered': contests,
			'video_description': vid_desc,
			'video_youtube_url': yt_link,
			'video_amvnews_url': amvnews_link,
			'video_other_url': other_link,
			'editor_org_profile_url': editor_profile_link
		}

	else:
		out_dict = dict()

	return out_dict

