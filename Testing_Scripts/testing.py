import requests
from rq import Queue
from worker import conn


def count_words_at_url(url):
    resp = requests.get(url)
    word_count = len(resp.text.split())
    print(word_count)
    return word_count


q = Queue(connection=conn)
result = q.enqueue(count_words_at_url, 'http://heroku.com')