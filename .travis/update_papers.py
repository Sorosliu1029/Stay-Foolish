#!/usr/bin/python3
"""
Update data/papers.json
"""
from datetime import datetime
import re
import os
import json

BIBTEX_PATTERN = re.compile(r'(?P<key>\w+)=\{(?P<value>.*?)\}')
WANTED_FIELDS = ['title', 'author', 'journal']
PAPER_STORE = os.path.join('data', 'papers.json')

def parse(line):
    match = BIBTEX_PATTERN.search(line)
    if match:
        return dict([match.groups()])

def main():
    print('Input quotation in BibTex format')
    paper = {}
    line = ''
    while line != '}':
        line = input().strip()
        parsed = parse(line)
        if parsed:
            paper.update(parsed)
    
    brief_paper = dict([(k, v) for k, v in paper.items() if k in WANTED_FIELDS])
    link = input('Input the link to this paper: ')
    brief_paper['link'] = link
    rate = int(input('Input your rating for this paper (1-5): '))
    brief_paper['rate'] = rate
    brief_paper['date'] = datetime.today().strftime('%Y-%m-%d')

    if not os.path.exists(PAPER_STORE):
        with open(PAPER_STORE, 'wt', encoding='utf-8') as f:
            json.dump([], f)
    with open(PAPER_STORE, 'rt', encoding='utf-8') as f:
        papers = json.load(f)

    papers.insert(0, brief_paper)
    with open(PAPER_STORE, 'wt', encoding='utf-8') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()