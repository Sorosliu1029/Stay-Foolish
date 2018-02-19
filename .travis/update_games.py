#!/usr/bin/python3
"""
Update data/games.json
"""
import json
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

ITUNES_PLATFORM = 'https://itunes.apple.com/cn/'
STEAM_PLATFORM =  'http://store.steampowered.com/app/'
PLATFORMS = {
    'itunes': ITUNES_PLATFORM,
    'steam': STEAM_PLATFORM
}
BING_URL = 'https://cn.bing.com/search'

def query_from_bing(keywords, site):
    query = {
        'q': '{keywords} site:{site}'.format(keywords=keywords, site=site)
    }
    encoded_query = urlencode(query)
    url = '{base}?{query}'.format(base=BING_URL, query=encoded_query)
    resp = requests.get(url)
    if resp.ok:
        return extract_info(resp.text, keywords, site)
    resp.raise_for_status()

def extract_info(html, keywords, site):
    soup = BeautifulSoup(html, 'lxml')
    query_results = soup.find('ol', id='b_results')
    assert query_results is not None

    for li in query_results.children:
        item = li.find('a')
        href = item['href']
        title = item.text
        if keywords.lower() in title.lower() and href.startswith(site):
            return href
    else:
        return None

def main():
    game_info = {}
    for site, site_url in PLATFORMS.items():
        href = query_from_bing('this war of mine', site_url)
        game_info[site] = href
    print(game_info)
    
if __name__ == '__main__':
    main()