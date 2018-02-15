#!/usr/bin/python3
"""
Update README file
"""
import os
import json
from jinja2 import Environment, FileSystemLoader
from update_from_douban import update_books
from update_from_linkedin import update_courses

CONFIGURATION_FILE = os.path.join('.', 'config.json')
TEMPLATE_PATH = os.path.join('.', 'templates')
BOOK_STORE = os.path.join('data', 'books.json')
COURSE_STORE = os.path.join('data', 'courses.json')


def get_configuration():
    if os.path.exists(CONFIGURATION_FILE):
        with open(CONFIGURATION_FILE, 'rt', encoding='utf-8') as f:
            config = json.load(f)
            douban_user_id = config['douban_user_id']
            linkedin_user_name = config['linkedin_user_name']
            linkedin_user_password = config['linkedin_user_password']
    elif os.getenv('DOUBAN_USER_ID') \
        and os.getenv('LINKEDIN_USER_NAME') \
        and os.getenv('LINKEDIN_USER_PASSWORD'):
        douban_user_id = os.getenv('DOUBAN_USER_ID')
        linkedin_user_name = os.getenv('LINKEDIN_USER_NAME')
        linkedin_user_password = os.getenv('LINKEDIN_USER_PASSWORD')
    else:
        raise SystemExit('Please create "config.json" containing "douban_user_id" field')

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
    
    return {
        'books': books,
        'courses': courses
    }

def main(skip_update=False):
    if not skip_update:
        configuration = get_configuration()

        update_books(configuration['douban_user_id'])
        update_courses(configuration['linkedin_user_name'], configuration['linkedin_user_password'])

    data = get_data()

    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
    template = env.get_template('README.j2')
    template.stream(**data).dump('README.md')

if __name__ == '__main__':
    main(skip_update=False)