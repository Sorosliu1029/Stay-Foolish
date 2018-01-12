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
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


def parse_date(date):
    return datetime.strptime(date, '%Y-%m-%d')

def get_user_book_status(session, user_id, start, mode="grid"):
    params = {
        "sort": "time",
        "start": start,
        "mode": mode,
    }
    r = session.get("https://book.douban.com/people/{}/collect".format(user_id), params=params)
    if r.ok:
        return r.text

def get_rated_books(session, user_id, latest_book_date):
    start = 0
    while True:
        if session.cookies:
            html = get_user_book_status(session, user_id, start)
        assert html
        start += 15

        soup = BeautifulSoup(html, "lxml")
        rating_pattern = re.compile(r'rating(\d+)-t')
        date_pattern = re.compile(r'\d+-\d+-\d+')
        items = soup.find_all('li', 'subject-item')
        if not items:
            return

        for status in items:
            pic = status.find('div', 'pic')
            info = status.find('div', 'info')
            short_note = info.find('div', 'short-note')

            cover_url = pic.find('img')['src']
            douban_link = info.h2.a['href']
            title_text = info.h2.a.get_text()
            title = re.sub(r'\s', '', title_text)

            rating_match = rating_pattern.search(''.join(short_note.div.span['class']))
            if rating_match:
                rate = rating_match.group(1)

            date_match = date_pattern.search(short_note.find('span', 'date').get_text())
            if date_match:
                date = date_match.group(0)

            assert rate and date
            if parse_date(date) <= latest_book_date:
                return

            yield {
                'title': title,
                'douban_link': douban_link,
                'cover_url': cover_url,
                'rate': int(rate),
                'date': date
            }

def main():
    if os.path.exists('config.json'):
        with open('config.json', 'rt', encoding='utf-8') as f:
            config = json.load(f)
    else:
        print('Please create "config.json" containing "user_id" field')
        sys.exit(1)

    user_id = config['user_id']
    if not os.path.exists('books.json'):
        with open('books.json', 'wt', encoding='utf-8') as f:
            json.dump([], f)

    with open('books.json', 'rt', encoding='utf-8') as f:
        books = json.load(f)

    assert books != None

    if books:
        latest_book_date = parse_date(books[0]["date"])
    else:
        latest_book_date = parse_date('1970-01-01')

    with requests.Session() as s:
        s.head('https://www.douban.com/')
        new_books = list(get_rated_books(s, user_id, latest_book_date))

    if new_books:
        books = new_books + books
        with open('books.json', 'wt', encoding='utf-8') as f:
            json.dump(books, f, indent=2, ensure_ascii=False)
            
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('README.template')
    template.stream(books=books).dump('README.md')

if __name__ == "__main__":
    main()
