#!/usr/bin/python3
"""
Grab status from www.douban.com
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime

BOOK_STORE = os.path.join('data', 'books.json')
MOVIE_STORE = os.path.join('data', 'movies.json')

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
    r.raise_for_status()

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
            title = re.sub(r'[\r\n\t]| {2,}', '', title_text)

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

def update_books(user_id):
    assert user_id

    if not os.path.exists(BOOK_STORE):
        with open(BOOK_STORE, 'wt', encoding='utf-8') as f:
            json.dump([], f)
    with open(BOOK_STORE, 'rt', encoding='utf-8') as f:
        books = json.load(f)

    assert books is not None

    if books:
        latest_book_date = parse_date(books[0]["date"])
    else:
        latest_book_date = parse_date('1970-01-01')

    with requests.Session() as s:
        s.head('https://www.douban.com/')
        new_books = list(get_rated_books(s, user_id, latest_book_date))

    if new_books:
        books = new_books + books
        with open(BOOK_STORE, 'wt', encoding='utf-8') as f:
            json.dump(books, f, indent=2, ensure_ascii=False)

def get_user_movie_status(session, user_id, start, mode="grid"):
    params = {
        "sort": "time",
        "start": start,
        "mode": mode,
    }
    r = session.get("https://movie.douban.com/people/{}/collect".format(user_id), params=params)
    if r.ok:
        return r.text
    r.raise_for_status()

def get_rated_movies(session, user_id, latest_movie_date):
    start = 0
    while True:
        if session.cookies:
            html = get_user_movie_status(session, user_id, start)
        assert html
        start += 15

        soup = BeautifulSoup(html, "lxml")
        rating_pattern = re.compile(r'rating(\d+)-t')
        date_pattern = re.compile(r'\d+-\d+-\d+')
        items = soup.find_all('div', 'item')
        if not items:
            return

        for status in items:
            pic = status.find('div', 'pic')
            info = status.find('div', 'info')

            poster_url = pic.find('img')['src']
            title_block = info.find('li', 'title')
            douban_link = title_block.a['href']
            title = title_block.a.em.get_text()

            status_block = info.ul.find_all('li')[2]
            rating_match = rating_pattern.search(''.join(status_block.span['class']))
            if rating_match:
                rate = rating_match.group(1)

            date_match = date_pattern.search(status_block.find('span', 'date').get_text())
            if date_match:
                date = date_match.group(0)

            assert rate and date
            if parse_date(date) <= latest_movie_date:
                return

            yield {
                'title': title,
                'douban_link': douban_link,
                'poster_url': poster_url,
                'rate': int(rate),
                'date': date
            }

def update_movies(user_id):
    assert user_id

    if not os.path.exists(MOVIE_STORE):
        with open(MOVIE_STORE, 'wt', encoding='utf-8') as f:
            json.dump([], f)
    with open(MOVIE_STORE, 'rt', encoding='utf-8') as f:
        movies = json.load(f)

    assert movies is not None

    if movies:
        latest_movie_date = parse_date(movies[0]["date"])
    else:
        latest_movie_date = parse_date('1970-01-01')

    with requests.Session() as s:
        s.head('https://www.douban.com/')
        new_movies = list(get_rated_movies(s, user_id, latest_movie_date))

    if new_movies:
        movies = new_movies + movies
        with open(MOVIE_STORE, 'wt', encoding='utf-8') as f:
            json.dump(movies, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # update_books(None)
    update_movies(None)
