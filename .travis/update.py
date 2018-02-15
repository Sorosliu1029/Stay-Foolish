#!/usr/bin/python3
"""
Update README file and GitHub Page index.html
"""
import os
import json
from jinja2 import Environment, FileSystemLoader
from update_from_douban import update_books
from update_from_linkedin import update_courses

CONFIGURATION_FILE = os.path.join('.', 'config.json')
TEMPLATE_PATH = os.path.join('.', 'templates')
BOOK_STORE = os.path.join('data', 'books.json')
MOVIE_STORE = os.path.join('data', 'movies.json')
COURSE_STORE = os.path.join('data', 'courses.json')
README_PATH = os.path.join('.', 'README.md')
INDEX_PATH = os.path.join('docs', 'index.html')


def get_configuration():
    if os.path.exists(CONFIGURATION_FILE):
        with open(CONFIGURATION_FILE, 'rt', encoding='utf-8') as f:
            config = json.load(f)
            douban_user_id = config['douban_user_id']
            linkedin_user_name = config['linkedin_user_name']
            linkedin_user_password = config['linkedin_user_password']
    elif os.getenv('DOUBAN_USER_ID'):
        douban_user_id = os.getenv('DOUBAN_USER_ID')
        linkedin_user_name = None
        linkedin_user_password = None
    else:
        raise SystemExit('Please create "config.json" containing "douban_user_id", "linkedin_user_name" and "linkedin_user_password" field')

    return {
        'douban_user_id': douban_user_id,
        'linkedin_user_name': linkedin_user_name,
        'linkedin_user_password': linkedin_user_password
    }

def get_data():
    with open(BOOK_STORE, 'rt', encoding='utf-8') as f:
        books = json.load(f)
    
    with open(COURSE_STORE, 'rt', encoding='utf-8') as f:
        courses = json.load(f)

    with open(MOVIE_STORE, 'rt', encoding='utf-8') as f:
        movies = json.load(f)
    
    return {
        'books': books,
        'courses': courses,
        'movies': movies
    }

def main(skip_update=False):
    if not skip_update:
        configuration = get_configuration()

        update_books(configuration['douban_user_id'])
        if configuration['linkedin_user_name'] is not None and configuration['linkedin_user_password'] is not None:
            update_courses(configuration['linkedin_user_name'], configuration['linkedin_user_password'])

    data = get_data()

    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
    readme_template = env.get_template('README.j2')
    readme_template.stream(**data).dump(README_PATH)

    html_template = env.get_template('index.html.j2')
    html_template.stream(**data).dump(INDEX_PATH)

if __name__ == '__main__':
    main(skip_update=False)