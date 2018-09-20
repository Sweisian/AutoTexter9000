from apscheduler.schedulers.blocking import BlockingScheduler
from enqueJobs import enque_job


sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    enque_job()
    print('This job is run every minute.')

sched.start()