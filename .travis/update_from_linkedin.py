#!/usr/bin/python3
"""
Grab courses from www.linkedin.com
"""
import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urlencode

COURSE_STORE = os.path.join('data', 'courses.json')
LINKEDIN_DOMAIN = 'https://www.linkedin.com/'

def login_linkedin(sess, user_name, password):
    assert 'bcookie' in sess.cookies.keys()
    csrf = sess.cookies.get('bcookie', domain='.linkedin.com', path='/').strip('"')
    csrf = csrf[4:]
    url = '{domain}uas/login-submit'.format(domain=LINKEDIN_DOMAIN)
    data = {
        'session_key': user_name,
        'session_password': password,
        'isJsEnabled': 'false',
        'loginCsrfParam': csrf
    }
    payload = urlencode(data)
    headers = {
        'Referer': LINKEDIN_DOMAIN,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    print(dict(sess.cookies))
    print(payload)
    resp = sess.request("POST", url, data=payload, headers=headers)
    if resp.ok:
        assert 'soros' in resp.text
        return
    resp.raise_for_status()

def get_course_platform(platform_verification):
    if 'coursera' in platform_verification.lower():
        return 'Coursera'
    else:
        return 'UNKNOWN'

def get_courses(sess, latest_course):
    url = "http://www.linkedin.com/public-profile/settings"
    resp = sess.request("GET", url)
    if resp.ok:
        html = resp.text
        assert html
        soup = BeautifulSoup(html, 'lxml')
        certificatoins = soup.find_all('li', class_='certification')
        for cert in certificatoins:
            title = cert.header.find('h4', class_='item-title')
            title = title.a.text
            if title == latest_course:
                return
            platform = cert.header.find('h5', class_='item-subtitle')
            platform = platform.a.text
            platform = get_course_platform(platform)
            yield {
                'title': title,
                'platform': platform
            }

    resp.raise_for_status()

def update_courses(user_name, password):
    assert user_name
    assert password

    if not os.path.exists(COURSE_STORE):
        with open(COURSE_STORE, 'wt', encoding='utf-8') as f:
            json.dump([], f)
    with open(COURSE_STORE, 'rt', encoding='utf-8') as f:
        courses = json.load(f)

    assert courses is not None

    if courses:
        latest_course = courses[0]['title']
    else:
        latest_course = 'No course name would be like this'
    
    with requests.Session() as s:
        s.get('{domain}'.format(domain=LINKEDIN_DOMAIN))
        login_linkedin(s, user_name, password)
        new_courses = list(get_courses(s, latest_course))
    
    if new_courses:
        courses = new_courses + courses
        with open(COURSE_STORE, 'wt', encoding='utf-8') as f:
            json.dump(courses, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    # update_courses(None, None)