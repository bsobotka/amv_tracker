"""
Patch notes for fetch_vid_info.py (v3 - automatic cookie extraction)
=======================================================================

Playwright-driven Turnstile solving got re-challenged in a loop, because
Cloudflare detects automation-controlled browsers regardless of whether a
human clicks the checkbox. v2 fixed that by having the user manually copy
cf_clearance out of DevTools after solving the challenge in a normal
browser. This version automates that copy step.

How it works: the user still solves the Turnstile challenge exactly once,
in their own everyday Chrome/Firefox -- nothing about that part changes,
and no automation is involved in the solving itself. But instead of the
user manually digging the cookie out of DevTools, `browser_cookie3` reads
it directly from that browser's local cookie storage on disk (it knows how
to open each browser's cookie DB/keychain, including Chrome's OS-level
encryption). Those cookies are then handed to `requests`, same as v2.

Requires: pip install browser_cookie3

Caveats:
    - Only works when run on the same machine as the browser (it's reading
      local browser profile data, not anything remote).
    - Chrome must be fully closed while reading its cookie DB on some
      platforms, or the read can fail/lock. Firefox is generally more
      permissive about concurrent reads.
    - If cookies aren't found, it almost always means the user hasn't
      solved the Turnstile challenge in that specific browser recently --
      the fallback below tells them exactly that.
    - cf_clearance still expires periodically (Cloudflare-side, not
      something this script controls), so this needs to be re-run
      periodically, but at least the user only has to re-solve the
      challenge in their browser, not go digging in DevTools again.
"""

import re
import requests
import browser_cookie3
import PyQt5.QtWidgets as QtWidgets
import pytube

from bs4 import BeautifulSoup as beautifulsoup
from fetch_video_info import get_yt_desc
from selenium import webdriver
from urllib import parse

#DEFAULT_HEADERS = {
#    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:153.0) Gecko/20100101 Firefox/153.0'
#}

ORG_DOMAIN = 'animemusicvideos.org'


def get_org_cookies(browser='Firefox'):
    """
    Automatically pulls animemusicvideos.org cookies (including cf_clearance) from the user's local browser cookie
    storage.

    :param browser: 'chrome', 'firefox', or 'auto' (tries Chrome first, then Firefox)
    :return: dict of {cookie_name: cookie_value} for animemusicvideos.org
    """

    if browser == 'Chrome':
        loaders = [browser_cookie3.chrome]
    elif browser == 'Firefox':
        loaders = [browser_cookie3.firefox]
    elif browser == 'Auto':
        loaders = [browser_cookie3.chrome, browser_cookie3.firefox]
    else:
        raise ValueError("browser must be 'chrome', 'firefox', or 'auto'")

    last_error = None
    for loader in loaders:
        try:
            cookie_jar = loader(domain_name=ORG_DOMAIN)
            cookies = {c.name: c.value for c in cookie_jar}
            if 'cf_clearance' in cookies:
                return cookies

        except:
            err_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
                                            'Cloudflare challenge page was not manually bypassed in Firefox. Please<br>'
                                            'open Firefox, navigate to <a href=https://www.animemusicvideos.org>https://www.animemusicvideos.org</a>,<br>'
                                            'and allow the Cloudflare challenge to complete, then try to fetch again.<br>'
                                            'If the problem persists after doing the above, please try again later.')
            err_win.exec_()
        # except Exception as e:
            # last_error = e
            # continue

    # raise LookupError(
    #    f"Couldn't find a cf_clearance cookie for {ORG_DOMAIN} in "
    #    f"{'Chrome or Firefox' if browser == 'auto' else browser}. "
    #    f"Open the site in that browser and solve the Turnstile challenge "
    #    f"first, then try again."
    #    + (f" (last underlying error: {last_error})" if last_error else '')
    #)


def download_data(url, site, url_type='video', org_cookies=None):
    # TODO: Fix amvnews fetch function and put fetch button back in layout on mainwindow
    """
    :param url: a-m-v.org/amvnews video profile URL or YouTube channel URL to parse
    :param site: "org" for a-m-v.org, "youtube" for YouTube, or "amvnews" for amvnews
    :param url_type: "video" if we want to parse a video URL, "channel" if we want to parse a channel/profile
    :param org_cookies: optional dict of cookies (e.g. {'cf_clearance': '...'}). If not
        provided and site='org', cookies are pulled automatically from the user's local
        browser via get_org_cookies() -- see org_browser.
    :param org_browser: which browser to auto-extract cookies from when org_cookies isn't
        given: 'chrome', 'firefox', or 'auto' (tries both). Only relevant when site='org'.
    :return: dict with {data_label: value} as output
    """

    if site == 'org':
        driver = webdriver.Firefox()
        user_agent = driver.execute_script('return navigator.userAgent')
        DEFAULT_HEADERS = {'user-agent': '{}'.format(user_agent)}
        driver.quit()

        if not org_cookies:
            org_cookies = get_org_cookies()
        elif 'cf_clearance' not in org_cookies:
            raise ValueError(
                "org_cookies was provided but is missing 'cf_clearance'."
            )

        r = requests.get(url, headers=DEFAULT_HEADERS, cookies=org_cookies)

        # If the cookie has expired or Turnstile still blocks us, requests
        # will succeed (200 OK) but the body will be the challenge page, not
        # the real one. Detect that explicitly rather than letting the
        # parsing below fail with a confusing exception.
        if 'cf-turnstile' in r.text or 'Just a moment' in r.text:
            err_win = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Error',
                                            'Cloudflare challenge page was not manually bypassed in Firefox. Please<br>'
                                            'open Firefox, navigate to <a href=https://www.animemusicvideos.org>https://www.animemusicvideos.org</a>,<br>'
                                            'and allow the Cloudflare challenge to complete, then try to fetch again.<br>'
                                            'If the problem persists after doing the above, please try again later.')
            err_win.exec_()
            return 'Error'

            #raise PermissionError(
            #    "Got a Cloudflare challenge page instead of real content. "
            #    "The cf_clearance cookie is likely expired or invalid -- "
            #    "re-solve the challenge in a normal browser and pass in "
            #    "fresh cookie values."
            #)

        soup = beautifulsoup(r.content, 'html5lib')
    else:
        r = requests.get(url, headers={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) '
												 'Gecko/20100101 Firefox/101.0'})
        soup = beautifulsoup(r.content, 'html5lib')

    if site == 'org':
        # --- everything below this line is your existing, unmodified parsing logic ---
        if 'members_videoinfo' in url:
            editor_info = soup.find('div', {'id': 'videoInformation'}).find('ul').find_all('li')
            try:
                editors = editor_info[0].get_text().strip().split('ember:')[1].strip().split(', ')
            except Exception:
                editors = editor_info[0].get_text().strip().split(':')[1].strip().split(', ')

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
            except Exception:
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
            anime_all = [elem.get_text().strip() for elem in anime_nonspoiler_html] + \
                        [elem.get_text().strip() for elem in anime_spoiler_html]
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

            for ind in range(0, len(anime_all_fixed)):
                if ', the' in anime_all_fixed[ind].casefold():
                    if anime_all_fixed[ind][-5:].lower() == ', the':
                        anime_all_fixed[ind] = 'The ' + anime_all_fixed[ind][:-5]
            anime_all_fixed.sort(key=lambda x: x.casefold())

            try:
                contests_confirmed_html = soup.find('ul', {'class': 'videoParticipation'}).find_all(
                    'li', attrs={'class', 'confirmed'})
                contests_pending_html = soup.find('ul', {'class': 'videoParticipation'}).find_all(
                    'li', attrs={'class', 'pending'})
                contests_all = [elem.get_text().strip() for elem in contests_confirmed_html] + \
                               [elem.get_text().strip() for elem in contests_pending_html]
                contests_final = []
                for con in contests_all:
                    contests_final.append(con.split(', ')[0])
                contests = '; '.join(contests_final)
            except Exception:
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
            except Exception:
                pass

            try:
                duration = soup.find('div', {'id': 'downloads'}).find('li', {'class': 'local'}).find(
                    'span', {'class': 'duration'})
                dur_min = int(duration.get_text().strip().split(':')[0])
                dur_sec = int(duration.get_text().strip().split(':')[1])
            except Exception:
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
        else:
            out_dict = dict()

    elif site == 'youtube':
        if url_type == 'video':
            yt = pytube.YouTube(url)
            ed_name = yt.author
            ed_yt_profile = yt.channel_url
            vid_desc = get_yt_desc.desc_fetcher(url)
            vid_length = yt.length
            yt_datetime = yt.publish_date
            rel_date = yt_datetime.strftime('%Y/%m/%d')
            vid_title = yt.title
            metadata = yt.metadata

            # Below code has never really worked, commenting it out to avoid errors
            #
            #try:
            #    if list(metadata):
            #        song_title = metadata[0]['Song']
            #        song_artist = metadata[0]['Artist']
            #    else:
            #        song_title = ''
            #        song_artist = ''
            #except Exception:
            #    song_title = ''
            #    song_artist = ''

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
            addl_editors_list = [x.get_text() for x in soup.find('span', {'itemprop': 'author'}).find_all('a')
                                  if x.get_text() != ed_name]
            addl_editors_list.sort(key=lambda x: x.casefold())
            addl_editors = '; '.join(addl_editors_list)
        except Exception:
            addl_editors = ''

        vid_title = soup.find('h1', {'class': 'title'}).get_text()
        try:
            studio = soup.find('a', {'href': re.compile(r'\bbystudio\b')}).get_text()
        except Exception:
            studio = ''

        release_date_html = soup.find('div', {'id': 'author-block'}).find_all(
            'span', attrs={'style': 'font: 12px Verdana; color: #999999;'})
        release_date_split = release_date_html[1].get_text()[:-1].split('.')
        release_date = [release_date_split[2], release_date_split[1], release_date_split[0]]

        try:
            music = soup.find('title').get_text().split(': ')[1].split(' - ')
            song_artist = music[0]
            song_title = music[1]
        except Exception:
            song_artist = ''
            song_title = ''

        star_rating = soup.find('span', {'itemprop': 'ratingValue'}).get_text()

        try:
            all_ftg = soup.find('div', {'itemprop': 'description'}).find('b', text='Аниме').next_sibling[2:]
        except Exception:
            all_ftg = soup.find('div', {'itemprop': 'description'}).find('b', text='Anime').next_sibling[2:]
        ftg = all_ftg.split(', ')
        ftg_cleaned = [f.replace('\n', '') for f in ftg]
        ftg_cleaned.sort(key=lambda x: x.casefold())

        desc = soup.find('div', {'itemprop': 'description'}).find('p', {'align': 'justify'}).get_text()

        try:
            awards = soup.find('div', {'itemprop': 'description'}).find('b', text='Awards').next_sibling[2:]
        except Exception:
            awards = ''

        amvnews_ed_prof_html = soup.find('div', {'id': 'author-block'}).find(
            'a', {'href': re.compile(r'\bbyauthor\b')})
        amvnews_ed_prof = 'https://amvnews.ru/' + parse.unquote(amvnews_ed_prof_html.get('href'))

        try:
            org_video_url_html = soup.find(
                'a', {'href': re.compile(r'\bwww.animemusicvideos.org/members/members_videoinfo.php\b')})
            org_video_url = parse.unquote(org_video_url_html.get('href'))
        except Exception:
            org_video_url = ''

        try:
            yt_video_url_html = soup.find('a', {'href': re.compile(r'\bwww.youtube.com/watch\b')})
            yt_video_url = parse.unquote(yt_video_url_html.get('href'))
        except Exception:
            yt_video_url = ''

        if yt_video_url != '':
            yt_obj = pytube.YouTube(yt_video_url)
            video_length = yt_obj.length
            ed_yt_channel = yt_obj.channel_url
        else:
            video_length = 0
            ed_yt_channel = ''

        out_dict = {
            'primary_editor_username': ed_name,
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
            'editor_amvnews_profile_url': amvnews_ed_prof
        }
    else:
        out_dict = dict()

    return out_dict