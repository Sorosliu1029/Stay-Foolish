#!/usr/bin/python3
"""
Grab cooked recipes from www.xiachufang.com
"""
import requests
from bs4 import BeautifulSoup
import os
import json

XIACHUFANG = 'https://www.xiachufang.com'
RECIPE_STORE = os.path.join('data', 'recipes.json')

def get_recipe_list_html(sess, url):
    r = sess.get('{domain}{url}'.format(domain=XIACHUFANG, url=url))
    if r.ok:
        return r.text
    r.raise_for_status()

def get_cooked_recipes(sess, recipe_list_id, most_recent_recipe):
    next_page_url = '/recipe_list/{recipe_list_id}/'.format(recipe_list_id=recipe_list_id)
    while True:
        html = get_recipe_list_html(sess, next_page_url)
        assert html

        soup = BeautifulSoup(html, 'lxml')
        recipe_list = soup.find('div', class_='normal-recipe-list')
        for recipe in recipe_list.find_all('div', class_='recipe'):
            cover_link = recipe.find('div', class_='cover').a.img['data-src']
            name_block = recipe.find('p', class_='name').a
            name = name_block.text.strip()
            link = '{domain}{href}'.format(domain=XIACHUFANG, href=name_block['href'])
            assert cover_link
            assert name
            assert link
            if name == most_recent_recipe:
                return
            
            yield {
                'cover_link': cover_link,
                'name': name,
                'link': link
            }
        
        next_page = soup.find('div', class_='pager').find('a', class_='next')
        if next_page is not None:
            next_page_url = next_page['href']
        else:
            return

def update_recipes(recipe_list_id):
    assert recipe_list_id

    if not os.path.exists(RECIPE_STORE):
        with open(RECIPE_STORE, 'wt', encoding='utf-8') as f:
            json.dump([], f)
    with open(RECIPE_STORE, 'rt', encoding='utf-8') as f:
        recipes = json.load(f)

    assert recipes is not None

    if recipes:
        most_recent_recipe = recipes[0]['name']
    else:
        most_recent_recipe = 'unnamed'
    
    with requests.Session() as s:
        new_recipes = list(get_cooked_recipes(s, recipe_list_id, most_recent_recipe))

    if new_recipes:
        recipes = new_recipes + recipes
        with open(RECIPE_STORE, 'wt', encoding='utf-8') as f:
            json.dump(recipes, f, indent=2, ensure_ascii=False)

def main():
    update_recipes(recipe_list_id)

if __name__ == '__main__':
    main()