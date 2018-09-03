
from rq import Queue
from worker import conn

from countWords import count_words_at_url
from main import handle_job

def enque_job():
    q = Queue(connection=conn)
    q.enqueue(handle_job())
    #result = q.enqueue(count_words_at_url, 'http://heroku.com')