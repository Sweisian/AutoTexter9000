import os


PLIVO_AUTH_ID = None
PLIVO_AUTH_TOKEN = None

def config():
    is_heroku = os.environ.get('IS_HEROKU', None)

    if is_heroku:
        PLIVO_AUTH_ID = os.environ.get('PLIVO_AUTH_ID', None)
        PLIVO_AUTH_TOKEN = os.environ.get('PLIVO_AUTH_TOKEN', None)
    else:
        return
