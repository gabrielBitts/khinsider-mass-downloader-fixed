import os
import re
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

BASE_URL = 'https://downloads.khinsider.com'


def validate_url(url):
    if '//downloads.khinsider.com/game-soundtracks/album/' not in url:
        return False
    return True


def fetch_from_url(url):
    valid = validate_url(url)
    if not valid:
        print('[error] Invalid url: ' + url)
        return
    print('[info] Url found: ' + url)

    base_dir = 'downloads'
    url_parts = url.split('/')
    dir_name = os.path.join(base_dir, url_parts[-1].strip())

    # Create directories
    if not os.path.exists(base_dir):
        print('[info] creating directory: ' + base_dir)
        os.makedirs(base_dir)
    if not os.path.exists(dir_name):
        print('[info] creating directory: ' + dir_name)
        os.makedirs(dir_name)

    print('[info] crawling for links...')

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Firefox/120.0'}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req) as response:
        soup = BeautifulSoup(response, 'html.parser')

    song_list = soup.find(id="songlist")
    if not song_list:
        print('[error] Could not find song list on the page.')
        return

    anchors = song_list.find_all('a')

    # href (string) -> song name (string)
    songMap = {}

    # Acquire links
    for anchor in anchors:
        href = anchor.get('href')
        if href and 'mp3' in href:
            href = BASE_URL + href
            if href not in songMap:
                songMap[href] = anchor.string

    if not songMap:
        print('[error] No links found for the url. Double check that the url is correct and try again.')
        print('[error] url: ' + url)
        return

    print('[info] ' + str(len(songMap)) + ' links acquired')

    # Map so we don't download duplicate links on the page
    downloaded_mp3s = {}

    # Iterate through links, grab the mp3s, and download them
    for href, song_name in songMap.items():
        req_link = urllib.request.Request(href, headers=headers)
        with urllib.request.urlopen(req_link) as response:
            link_soup = BeautifulSoup(response, 'html.parser')

        audio = link_soup.find('audio')
        if not audio or not audio.get('src'):
            continue

        mp3_url = audio.get('src')

        if mp3_url not in downloaded_mp3s:
            downloaded_mp3s[mp3_url] = True
            safe_song_name = song_name if song_name else 'track'
            file_name = re.sub(r'[<>:"/\\|?*]', '', safe_song_name) + '.mp3'

            req_mp3 = urllib.request.Request(mp3_url, headers=headers)
            with urllib.request.urlopen(req_mp3) as mp3file:
                meta = mp3file.info()
                content_length = meta.get("Content-Length")
                file_size = float(content_length) / 1000000 if content_length else 0.0

                file_on_disk_path = os.path.join(dir_name, file_name)

                # check if file already exists
                file_already_downloaded = False
                if os.path.exists(file_on_disk_path):
                    stat = os.stat(file_on_disk_path)
                    file_already_downloaded = round(float(stat.st_size) / 1000000, 2) == round(file_size, 2)

                # It exists but isn't already the same size
                if not file_already_downloaded:
                    print('[downloading] ' + file_name + ' [%.2f' % file_size + 'MB]')
                    with open(file_on_disk_path, 'wb') as output:
                        output.write(mp3file.read())
                    print('[done] "' + file_name + '"')
                else:
                    print('[skipping] "' + file_name + '" already downloaded.')


input_file_name = 'inputs.txt'
if os.path.exists(input_file_name):
    print('[info] Input file found. Parsing for links...')
    with open(input_file_name, 'r') as file:
        for line in file:
            if line.strip():
                fetch_from_url(line.strip())
else:
    print('Please input link to album on khinsider.')
    print('Example input: https://downloads.khinsider.com/game-soundtracks/album/disgaea-4-a-promise-unforgotten-soundtrack')
    url = input('Url: ')
    fetch_from_url(url.strip())
