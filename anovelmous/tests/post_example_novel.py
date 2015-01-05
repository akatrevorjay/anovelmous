import argparse
from nltk.corpus import brown
import requests
import arrow
import json


parser = argparse.ArgumentParser()
parser.add_argument('host')
args = parser.parse_args()


def create_new_novel():
    url = 'http://{host}/api/novel'.format(host=args.host)
    response = requests.post(url, json={'title': 'Test Novel {}'.format(arrow.utcnow())})
    return json.loads(response)['id']


def create_new_chapter(novel_id):
    url = 'http://{host}/api/chapter'.format(host=args.host)
    chapter_title = 'Chapter {}'.format(arrow.utcnow())
    response = requests.post(url, json={'title': chapter_title, 'novel_id': novel_id})
    return json.loads(response)['id']


def post_example_text_to_chapter(chapter_id):
    url = 'http://{host}/api/novel_token'.format(host=args.host)
    words = brown.words(categories=['lore'])
    for ordinal, word in enumerate(words):
        requests.post(url, json={'token': word, 'ordinal': ordinal, 'chapter_id': chapter_id})


if __name__ == '__main__':
    novel_id = create_new_novel()
    chapter_id = create_new_chapter(novel_id)
    post_example_text_to_chapter(chapter_id)