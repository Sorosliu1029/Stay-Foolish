#!/usr/bin/python3
"""
Grab podcasts from https://www.shiftyjelly.com/pocketcasts/
"""
import requests
import json
import os
from urllib.parse import urlencode

POCKET_CAST_DOMAIN = 'https://play.pocketcasts.com'
PODCAST_STORE = os.path.join('data', 'podcasts.json')

def login_pocket_cast(sess, user_name, password):
    url = '{domain}/users/sign_in'.format(domain=POCKET_CAST_DOMAIN)
    data = {
        'user[email]': user_name,
        'user[password]': password,
        'user[remember_me]': 1,
        'commit': 'Sign In'
    }
    payload = urlencode(data)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    resp = sess.post(url, data=payload, headers=headers)
    if resp.ok:
        cookies = sess.cookies.keys()
        assert 'XSRF-TOKEN' in cookies
        assert '_social_session' in cookies
        assert 'remember_user_token' in cookies
    resp.raise_for_status()

def get_subscribed_podcasts(sess):
    url = '{domain}/web/podcasts/all.json'.format(domain=POCKET_CAST_DOMAIN)
    resp = sess.post(url, json=dict())
    if resp.ok:
        return resp.json()['podcasts']
    resp.raise_for_status()

def update_podcasts(user_name, password):
    assert user_name
    assert password

    if not os.path.exists(PODCAST_STORE):
        with open(PODCAST_STORE, 'wt', encoding='utf-8') as f:
            json.dump([], f)
    with open(PODCAST_STORE, 'rt', encoding='utf-8') as f:
        podcasts = json.load(f)

    with requests.Session() as s:
        login_pocket_cast(s, user_name, password)
        new_podcasts = get_subscribed_podcasts(s)
    assert new_podcasts
    assert type(new_podcasts) is list

    ids = set([p['id'] for p in podcasts])
    fields = ['id', 'url', 'title', 'description', 'thumbnail_url', 'author']
    get_fields = lambda podcast: dict([(k, v) for k, v in podcast.items() if k in fields])
    new_podcasts = list(map(get_fields, filter(lambda podcast: podcast['id'] not in ids, new_podcasts)))
    if new_podcasts:
        podcasts = new_podcasts + podcasts
        with open(PODCAST_STORE, 'wt', encoding='utf-8') as f:
            json.dump(podcasts, f, indent=2, ensure_ascii=False)
    
def main():
    update_podcasts(None, None)    

if __name__ == '__main__':
    main()