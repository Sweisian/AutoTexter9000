
from rq import Queue
from worker import conn
import time

from countWords import count_words_at_url
from main import handle_single_job , mydb


def enque_job():
    q = Queue(connection=conn)

    my_jobs_col = mydb["jobs"]
    for job in my_jobs_col.find():
        print(f"\nCURRENT JOB IS: {job}\n")
        q.enqueue(handle_single_job(job))
        time.sleep(5)
    #result = q.enqueue(count_words_at_url, 'http://heroku.com')