#!/usr/bin/python3
"""
Update README file and GitHub Page index.html
"""
import os
import sys
import json
from jinja2 import Environment, FileSystemLoader
from update_from_douban import update_books, update_movies
from update_from_linkedin import update_courses
from update_from_pocketcasts import update_podcasts

CONFIGURATION_FILE = os.path.join('.', 'config.json')
TEMPLATE_PATH = os.path.join('.', 'templates')
BOOK_STORE = os.path.join('data', 'books.json')
MOVIE_STORE = os.path.join('data', 'movies.json')
COURSE_STORE = os.path.join('data', 'courses.json')
PAPER_STORE = os.path.join('data', 'papers.json')
PODCAST_STORE = os.path.join('data', 'podcasts.json')
GAME_STORE = os.path.join('data', 'games.json')
README_PATH = os.path.join('.', 'README.md')
INDEX_PATH = os.path.join('docs', 'index.html')


def get_configuration():
    if os.path.exists(CONFIGURATION_FILE):
        with open(CONFIGURATION_FILE, 'rt', encoding='utf-8') as f:
            config = json.load(f)
            douban_user_id = config['douban_user_id']
            linkedin_user_name = config['linkedin_user_name']
            linkedin_user_password = config['linkedin_user_password']
            pocketcasts_user_name = config['pocketcasts_user_name']
            pocketcasts_password = config['pocketcasts_password']
    elif os.getenv('DOUBAN_USER_ID') and os.getenv('POCKETCASTS_USER_NAME') and os.getenv('POCKETCASTS_PASSWORD'):
        douban_user_id = os.getenv('DOUBAN_USER_ID')
        linkedin_user_name = None
        linkedin_user_password = None
        pocketcasts_user_name = os.getenv('POCKETCASTS_USER_NAME')
        pocketcasts_password = os.getenv('POCKETCASTS_PASSWORD')
    else:
        raise SystemExit('Please create "config.json" containing "douban_user_id", "linkedin_user_name", "linkedin_user_password", "pocketcasts_user_name" and "pocketcasts_password" field')

    return {
        'douban_user_id': douban_user_id,
        'linkedin_user_name': linkedin_user_name,
        'linkedin_user_password': linkedin_user_password,
        'pocketcasts_user_name': pocketcasts_user_name,
        'pocketcasts_password': pocketcasts_password
    }

def get_data():
    with open(BOOK_STORE, 'rt', encoding='utf-8') as f:
        books = json.load(f)
    
    with open(COURSE_STORE, 'rt', encoding='utf-8') as f:
        courses = json.load(f)
    
    with open(PAPER_STORE, 'rt', encoding='utf-8') as f:
        papers = json.load(f)

    with open(PODCAST_STORE, 'rt', encoding='utf-8') as f:
        podcasts = json.load(f)

    with open(MOVIE_STORE, 'rt', encoding='utf-8') as f:
        movies = json.load(f)

    with open(GAME_STORE, 'rt', encoding='utf-8') as f:
        games = json.load(f)
    
    return {
        'books': books,
        'courses': courses,
        'papers': papers,
        'podcasts': podcasts,
        'movies': movies,
        'games': games
    }

def main(skip_update):
    if not skip_update:
        configuration = get_configuration()

        update_books(configuration['douban_user_id'])
        update_movies(configuration['douban_user_id'])
        update_podcasts(configuration['pocketcasts_user_name'], configuration['pocketcasts_password'])
        if configuration['linkedin_user_name'] is not None and configuration['linkedin_user_password'] is not None:
            update_courses(configuration['linkedin_user_name'], configuration['linkedin_user_password'])

    data = get_data()

    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
    readme_template = env.get_template('README.j2')
    readme_template.stream(**data).dump(README_PATH)

    html_template = env.get_template('index.html.j2')
    html_template.stream(**data).dump(INDEX_PATH)

if __name__ == '__main__':
    skip_update = False
    if len(sys.argv) > 1:
        skip_update = True
    main(skip_update)