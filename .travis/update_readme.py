#!/usr/bin/python3
"""
Update README file
"""
import os
import json
from jinja2 import Environment, FileSystemLoader
from update_from_douban import update_books

CONFIGURATION_FILE = os.path.join('.', 'config.json')
TEMPLATE_PATH = os.path.join('.', 'templates')
BOOK_STORE = os.path.join('data', 'books.json')

def get_configuration():
    if os.path.exists(CONFIGURATION_FILE):
        with open(CONFIGURATION_FILE, 'rt', encoding='utf-8') as f:
            config = json.load(f)
            douban_user_id = config['douban_user_id']
    elif os.getenv('DOUBAN_USER_ID'):
        douban_user_id = os.getenv('DOUBAN_USER_ID')
    else:
        raise SystemExit('Please create "config.json" containing "douban_user_id" field')

    return {
        'douban_user_id': douban_user_id
    }

def get_data():
    with open(BOOK_STORE, 'rt', encoding='utf-8') as f:
        books = json.load(f)
    
    return {
        'books': books
    }

def main():
    configuration = get_configuration()

    update_books(configuration['douban_user_id'])

    data = get_data()

    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
    template = env.get_template('README.template')
    template.stream(**data).dump('README.md')

if __name__ == '__main__':
    main()