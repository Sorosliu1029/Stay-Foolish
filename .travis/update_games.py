#!/usr/bin/python3
"""
Update data/games.json
"""
import json
import sys
import os
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
GAME_STORE = os.path.join('data', 'games.json')

def query_from_bing(keywords, site):
    for keyword in keywords:
        query = {
            'q': '{keyword} site:{site}'.format(keyword=keyword, site=site)
        }
        encoded_query = urlencode(query)
        url = '{base}?{query}'.format(base=BING_URL, query=encoded_query)
        resp = requests.get(url)
        if resp.ok:
            href = extract_info(resp.text, keywords, site)
            if href:
                return href
        resp.raise_for_status()

def extract_info(html, keywords, site):
    soup = BeautifulSoup(html, 'lxml')
    query_results = soup.find_all('li', class_='b_algo')

    for li in query_results:
        item = li.find('a')
        href = item['href']
        title = item.text
        print('Searched result:\t{}'.format(title))
        if any([keyword.lower() in title.lower() for keyword in keywords]) and href.startswith(site):
            return href
    else:
        return None

def get_game_icon(href):
    if href:
        resp = requests.get(href)
        if resp.ok:
            html = resp.text
            soup = BeautifulSoup(html, 'lxml')

            if href.startswith(ITUNES_PLATFORM):
                icon_link = soup.find('img', class_='we-artwork__image')
            elif href.startswith(STEAM_PLATFORM):
                icon_link = soup.find('img', class_='game_header_image_full')

            if icon_link:
                icon_link = icon_link['src']
            return icon_link
        resp.raise_for_status()

def main():
    opt = 'n'
    try:
        while opt.lower() == 'n':
            en_name = input('Input game name(EN): ').strip()
            cn_name = input('Input game name(CN): ').strip()
            rate = int(input('How good it is? (1-5): ').strip())
            assert 1 <= rate <= 5

            game_info = {
                'en_name': en_name if en_name else None,
                'cn_name': cn_name if cn_name else None,
                'rate': rate
            }

            name = tuple(filter(None, (en_name, cn_name)))
            for site, site_url in PLATFORMS.items():
                href = query_from_bing(name, site_url)
                game_info[site] = href
            game_info['icon_link'] = get_game_icon(game_info['itunes'] or game_info['steam']) 
            
            print('Please confirm game info below:')
            for k, v in game_info.items():
                print('\t{k}\t: {v}'.format(k=k, v=v))
            opt = input('Press Enter or y to confirm, or n to re-enter. ([y]/n) ').strip() or 'y'
    except KeyboardInterrupt:
        sys.exit(1)
    
    if not os.path.exists(GAME_STORE):
        with open(GAME_STORE, 'wt', encoding='utf-8') as f:
            json.dump([], f)
    with open(GAME_STORE, 'rt', encoding='utf-8') as f:
        games = json.load(f)
    
    for game in games:
        if game['en_name'] and game['en_name'] == en_name:
            print('{name} is already in list'.format(name=en_name))
            sys.exit(0)
        if game['cn_name'] and game['cn_name'] == cn_name:
            print('{name} is already in list'.format(name=cn_name))
            sys.exit(0)

    games.insert(0, game_info)
    with open(GAME_STORE, 'wt', encoding='utf-8') as f:
            json.dump(games, f, indent=2, ensure_ascii=False)
    
if __name__ == '__main__':
    main()