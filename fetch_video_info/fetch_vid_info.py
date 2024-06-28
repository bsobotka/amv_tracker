import re
import requests
import pytube

from bs4 import BeautifulSoup as beautifulsoup
from fetch_video_info import get_yt_desc
# from pytube import YouTube
from urllib import parse


def download_data(url, site, url_type='video'):
	"""
	:param url: a-m-v.org/amvnews video profile URL or YouTube channel URL to parse
	:param site: "org" for a-m-v.org, "youtube" for YouTube, or "amvnews" for amvnews
	:param url_type: "video" if we want to parse a video URL, "channel" if we want to parse a channel/profile
	:return: dict with {data_label: value} as output
	"""

	r = requests.get(url, headers={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) '
												 'Gecko/20100101 Firefox/101.0'})
	soup = beautifulsoup(r.content, 'html5lib')

	if site == 'org':
		if 'members_videoinfo' in url:
			editor_info = soup.find('div', {'id': 'videoInformation'}).find('ul').find_all('li')
			# editors = editor_info[0].get_text().strip().split(':')[1].strip().split(', ')
			try:
				editors = editor_info[0].get_text().strip().split('ember:')[1].strip().split(', ')
			except:
				editors = editor_info[0].get_text().strip().split(':')[1].strip().split(', ')
				# editors = editor_info[0].get_text().strip().split('):')[1].strip().split(', ')
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

			# Remove parenthetical suffixes from source titles
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

			# Fix "The" appearing at the end of source titles
			for ind in range(0, len(anime_all_fixed)):
				if ', the' in anime_all_fixed[ind].casefold():
					if anime_all_fixed[ind][-5:].lower() == ', the':
						anime_all_fixed[ind] = 'The ' + anime_all_fixed[ind][:-5]

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
				'video_org_url': url,
				'video_amvnews_url': amvnews_link,
				'video_other_url': other_link,
				'editor_org_profile_url': editor_profile_link
			}

			if yt_link != '':
				out_dict['video_youtube_url'] = yt_link

	elif site == 'youtube':
		if url_type == 'video':
			yt = pytube.YouTube(url)

			ed_name = yt.author
			ed_yt_profile = yt.channel_url
			# vid_desc = yt.description
			vid_desc = get_yt_desc.desc_fetcher(url)
			vid_length = yt.length
			yt_datetime = yt.publish_date
			rel_date = yt_datetime.strftime('%Y/%m/%d')
			vid_title = yt.title

			metadata = yt.metadata
			try:
				if list(metadata):
					song_title = metadata[0]['Song']
					song_artist = metadata[0]['Artist']
				else:
					song_title = ''
					song_artist = ''
			except:
				song_title = ''
				song_artist = ''

			out_dict = {
				'primary_editor_username': ed_name,
				'video_title': vid_title,
				'release_date': rel_date,
				'song_artist': song_artist,
				'song_title': song_title,
				'video_length': vid_length,
				'video_description': vid_desc,
				'video_youtube_url': url,
				'editor_youtube_channel_url': ed_yt_profile,
			}

		else:
			out_dict = dict()

	elif site == 'amvnews':
		ed_name = soup.find('span', {'itemprop': 'name'}).get_text()

		try:
			addl_editors_list = [x.get_text() for x in soup.find('span', {'itemprop': 'author'}).find_all('a') if
								 x.get_text() != ed_name]
			addl_editors_list.sort(key=lambda x: x.casefold())
			addl_editors = '; '.join(addl_editors_list)
		except:
			addl_editors = ''

		vid_title = soup.find('h1', {'class': 'newstitle'}).get_text()

		try:
			studio = soup.find('a', {'href': re.compile(r'\bbystudio\b')}).get_text()
		except:
			studio = ''

		release_date_html = soup.find('div', {'id': 'author-block'}).find_all('span', attrs={'style': 'font: 12px Verdana; color: #999999;'})
		release_date_split = release_date_html[1].get_text()[:-1].split('.')
		release_date = [release_date_split[2], release_date_split[1], release_date_split[0]]

		try:
			music = soup.find('title').get_text().split(': ')[1].split(' - ')
			song_artist = music[0]
			song_title = music[1]
		except:
			song_artist = ''
			song_title = ''

		star_rating = soup.find('span', {'itemprop': 'ratingValue'}).get_text()

		try:
			all_ftg = soup.find('div', {'itemprop': 'description'}).find('b', text='Аниме').next_sibling[2:]
		except:
			all_ftg = soup.find('div', {'itemprop': 'description'}).find('b', text='Anime').next_sibling[2:]

		ftg = all_ftg.split(', ')
		ftg_cleaned = [f.replace('\n', '') for f in ftg]
		ftg_cleaned.sort(key=lambda x: x.casefold())

		desc = soup.find('div', {'itemprop': 'description'}).find('p', {'align': 'justify'}).get_text()

		try:
			awards = soup.find('div', {'itemprop': 'description'}).find('b', text='Awards').next_sibling[2:]
		except:
			awards = ''

		amvnews_ed_prof_html = soup.find('div', {'id': 'author-block'}).find('a', {'href': re.compile(r'\bbyauthor\b')})
		amvnews_ed_prof = 'https://amvnews.ru/' + parse.unquote(amvnews_ed_prof_html.get('href'))

		try:
			org_video_url_html = soup.find('a', {'href': re.compile(r'\bwww.animemusicvideos.org/members/members_videoinfo.php\b')})
			org_video_url = parse.unquote(org_video_url_html.get('href'))
		except:
			org_video_url = ''

		try:
			yt_video_url_html = soup.find('a', {'href': re.compile(r'\bwww.youtube.com/watch\b')})
			yt_video_url = parse.unquote(yt_video_url_html.get('href'))
		except:
			yt_video_url = ''

		if yt_video_url != '':
			yt_obj = pytube.YouTube(yt_video_url)
			video_length = yt_obj.length
			ed_yt_channel = yt_obj.channel_url
		else:
			video_length = 0
			ed_yt_channel = ''

		out_dict = {'primary_editor_username': ed_name,
					'addl_editors': addl_editors,
					'video_title': vid_title,
					'studio': studio,
					'awards_won': awards,
					'release_date': release_date,
					'song_artist': song_artist,
					'song_title': song_title,
					'star_rating': star_rating,
					'video_description': desc,
					'video_length': video_length,
					'video_footage': ftg_cleaned,
					'video_youtube_url': yt_video_url,
					'org_video_url': org_video_url,
					'editor_youtube_channel_url': ed_yt_channel,
					'editor_amvnews_profile_url': amvnews_ed_prof}

	else:
		out_dict = dict()
	return out_dict
