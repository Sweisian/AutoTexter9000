
from rq import Queue
from worker import conn

from countWords import count_words_at_url


def enque_job():
    q = Queue(connection=conn)
    result = q.enqueue(count_words_at_url, 'http://heroku.com')