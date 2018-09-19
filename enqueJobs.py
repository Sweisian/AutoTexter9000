
from rq import Queue
from worker import conn

from main import mydb
from utilities import handle_single_job


def enque_job():
    q = Queue(connection=conn)

    my_jobs_col = mydb["jobs"]
    for job in my_jobs_col.find():
        print(f"\nCURRENT JOB IS: {job}\n")
        q.enqueue(handle_single_job, job)
    #result = q.enqueue(count_words_at_url, 'http://heroku.com')