#!/usr/bin/python3
"""
Grab reading status from www.douban.com
And update markup file
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import os.path
import sys

DOMAIN = ".douban.com"

def get_initial_cookies():
    r = requests.head("https://www{}".format(DOMAIN))
    if r.ok:
        r.cookies.clear(domain=DOMAIN, path='/', name='ll')
    return r.cookies.copy()

def get_user_book_status(user_id, start=0, mode="grid", cookies=None):
    params = {
        "sort": "time",
        "start": start,
        "filter": "all",
        "mode": mode,
        "tags_sort": "count"
    }
    r = requests.get("https://book.douban.com/people/{}/collect".format(user_id), params=params, cookies=cookies)
    if r.ok:
        return r.text

def get_rated_books(html):
    soup = BeautifulSoup(html, "lxml")
    rating_pattern = re.compile(r'rating(\d+)-t')
    date_pattern = re.compile(r'\d+-\d+-\d+')
    for status in soup.find_all('li', 'subject-item'):
        pic = status.find('div', 'pic')
        info = status.find('div', 'info')

        book_img = pic.find('img')['src']
        book_img_width = int(pic.find('img')['width'])
        title_text = info.h2.a.get_text()

        title = re.sub(r'\s', '', title_text)
        short_note = info.find('div', 'short-note')
        rating_match = rating_pattern.search(''.join(short_note.div.span['class']))
        if rating_match:
            rate = rating_match.group(1)
        date_match = date_pattern.search(short_note.find('span', 'date').get_text())
        if date_match:
            date = date_match.group(0)

        yield {
            'title': title,
            'book_img_url': book_img,
            'book_img_width': book_img_width,
            'rate': int(rate),
            'date': date
        }

def main():
    if os.path.exists('config.json'):
        with open('config.json', 'rt') as f:
            config = json.load(f)
    else:
        print('Please create "config.json" containing "user_id" field')
        sys.exit(1)

    user_id = config['user_id']
    cookie = get_initial_cookies()
    html = get_user_book_status(user_id, cookies=cookie)
    books = list(get_rated_books(html))
    with open('books.json', 'wt') as f:
        json.dump(books, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
