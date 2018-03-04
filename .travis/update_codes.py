#!/usr/bin/python3
"""
Update data/codes.json
"""
import json
import os
import sys
from datetime import datetime
import requests

GITHUB_SEARCH_URL = 'https://api.github.com/search/repositories'
CODE_STORE = os.path.join('data', 'codes.json')
LIST_LIMIT = 5

def search_from_github(name, language):
    q = '{name}+{language}fork:false+in:name'.format(name=name, language='language:'+language+'+' if language else '')
    resp = requests.get('{base}?q={params}'.format(base=GITHUB_SEARCH_URL, params=q))
    if resp.ok:
        return resp.json()['items']
    resp.raise_for_status()

def main():
    name = input('Source code name? ').strip()
    assert name
    language = input('In which programming language? ') or None
    rate = int(input('In which level will you recommend? [1-5] '))
    assert rate and 1 <= rate <= 5
    
    items = search_from_github(name, language)
    items = list(filter(lambda item: item['language'] and item['language'].lower() == language.lower(), items))
    fields = ['id', 'name', 'html_url', 'description', 'language']
    brief_items = []
    for idx, item in enumerate(items[:LIST_LIMIT], start=1):
        brief_item = dict([(k, v) for k, v in item.items() if k in fields])
        brief_items.append(brief_item)
        print(str(idx), end='')
        for f in ['name', 'html_url', 'language']:
            print('\t{:>10}:\t{}'.format(f, brief_item[f]))
    selected = int(input('Select one of the candidates: ([1]-{limit}) '.format(limit=LIST_LIMIT)) or '1')

    source_code = brief_items[selected-1]
    source_code['rate'] = rate
    source_code['date'] = datetime.today().strftime('%Y-%m-%d')

    if not os.path.exists(CODE_STORE):
        with open(CODE_STORE, 'wt', encoding='utf-8') as f:
            json.dump([], f)
    with open(CODE_STORE, 'rt', encoding='utf-8') as f:
        codes = json.load(f)

    for code in codes:
        if code['id'] == source_code['id']:
            print('{name} already recorded.'.format(name=name))
            sys.exit(0)

    codes.insert(0, source_code)
    with open(CODE_STORE, 'wt', encoding='utf-8') as f:
        json.dump(codes, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()