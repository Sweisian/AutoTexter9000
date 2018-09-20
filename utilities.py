import datetime
import os

import plivo
import pytz

import pymongo

#TODO: MAKE THIS A FUNCTION, REPLACE MAIN STUFF WITH FUNCTION
myclient = pymongo.MongoClient("mongodb://admin1:admin1@ds253891.mlab.com:53891/pioneers_of_interactive_entertainment_nu")
mydb = myclient["pioneers_of_interactive_entertainment_nu"]
my_users_col = mydb["users"]

my_number = '+14844840496'

def standalone_send_bulk_text(message_to_send):
    user_data = my_users_col.find()

    client = plivo.RestClient(os.environ['PLIVO_AUTH_ID'], os.environ['PLIVO_AUTH_TOKEN'])
    for curr_user in user_data:
        if curr_user.get("user_enabled"):
            curr_num = curr_user["_id"]
            send_single_text(client, my_number, curr_num, message_to_send)

    return "I did it"


def handle_single_job(job):

        user_date = job["date"]
        user_time = job["time"]
        message_to_send = job["message"]

        my_datetime_s = f"{user_date} {user_time}"
        #print(f"my_datetime_s = {my_datetime_s}")
        naive_scheduled = datetime.datetime.strptime(my_datetime_s, "%Y-%m-%d %H:%M")
        #print(f"JOB DATE TIME = {naive_scheduled}")
        print(f"LOCALIZED JOB SCHEDULED = {naive_scheduled}")

        chicago_tz = pytz.timezone("America/Chicago")
        now_time_chicago = datetime.datetime.now(chicago_tz)
        now_time_chicago = now_time_chicago.replace(tzinfo=None)
        print(f"CURRENT CHICAGO TIME = {now_time_chicago}")

        # my_timedelta = now_time_chicago - naive_scheduled
        # print(f"my_timedelta = {my_timedelta}")

        should_execute = naive_scheduled <= now_time_chicago

        print(f"Will Execute?: {should_execute}")
        print()

        if should_execute:
            standalone_send_bulk_text(message_to_send)
            mydb["jobs"].delete_one(job)


def send_single_text(client, my_number, dest_number, msg):
    print("Sending text to " + dest_number)
    print("Text Content: " + msg)
    try:
        response = client.messages.create(
            src=my_number,
            dst='+' + dest_number,
            text=msg,
        )
        print(response.__dict__)

    except plivo.exceptions.PlivoRestError as e:
        print(e)


# my_jobs_col = mydb["jobs"]
# for job in my_jobs_col.find():
#     handle_single_job(job)
