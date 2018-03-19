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
from update_from_xiachufang import update_recipes

CONFIGURATION_FILE = os.path.join('.', 'config.json')
TEMPLATE_PATH = os.path.join('.', 'templates')
README_PATH = os.path.join('.', 'README.md')
INDEX_PATH = os.path.join('docs', 'index.html')

DATAS = ['books', 'movies', 'courses', 'papers', 'codes', 'podcasts', 'games', 'recipes']

def get_configuration():
    if os.path.exists(CONFIGURATION_FILE):
        with open(CONFIGURATION_FILE, 'rt', encoding='utf-8') as f:
            config = json.load(f)
            douban_user_id = config['douban_user_id']
            xiachufang_recipe_list_id = config['xiachufang_recipe_list_id']
            linkedin_user_name = config['linkedin_user_name']
            linkedin_user_password = config['linkedin_user_password']
            pocketcasts_user_name = config['pocketcasts_user_name']
            pocketcasts_password = config['pocketcasts_password']
    elif os.getenv('DOUBAN_USER_ID') and os.getenv('XIACHUFANG_RECIPE_LIST_ID'):
        douban_user_id = os.getenv('DOUBAN_USER_ID')
        xiachufang_recipe_list_id = os.getenv('XIACHUFANG_RECIPE_LIST_ID')
        linkedin_user_name = None
        linkedin_user_password = None
        pocketcasts_user_name = None
        pocketcasts_password = None
    else:
        raise SystemExit('Please create "config.json" containing "douban_user_id", "xiachufang_recipe_list_id", "linkedin_user_name", "linkedin_user_password", "pocketcasts_user_name" and "pocketcasts_password" field')

    return {
        'douban_user_id': douban_user_id,
        'xiachufang_recipe_list_id': xiachufang_recipe_list_id,
        'linkedin_user_name': linkedin_user_name,
        'linkedin_user_password': linkedin_user_password,
        'pocketcasts_user_name': pocketcasts_user_name,
        'pocketcasts_password': pocketcasts_password
    }

def get_data():
    datas = {}
    for data in DATAS:
        with open(os.path.join('data', '{}.json'.format(data)), 'rt', encoding='utf-8') as f:
            datas[data] = json.load(f)
    
    return datas

def main(skip_update):
    if not skip_update:
        configuration = get_configuration()

        update_books(configuration['douban_user_id'])
        update_movies(configuration['douban_user_id'])

        update_recipes(configuration['xiachufang_recipe_list_id'])

        if configuration['linkedin_user_name'] is not None and configuration['linkedin_user_password'] is not None:
            update_courses(configuration['linkedin_user_name'], configuration['linkedin_user_password'])

        if configuration['pocketcasts_user_name'] is not None and configuration['pocketcasts_password'] is not None:
            update_podcasts(configuration['pocketcasts_user_name'], configuration['pocketcasts_password'])
    
    datas = get_data()

    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
    readme_template = env.get_template('README.j2')
    readme_template.stream(**datas).dump(README_PATH)

    html_template = env.get_template('index.html.j2')
    html_template.stream(**datas).dump(INDEX_PATH)

if __name__ == '__main__':
    skip_update = False
    if len(sys.argv) > 1:
        skip_update = True
    main(skip_update)