import csv
import datetime
import os

import plivo
import pytz

import pymongo

#TODO: MAKE THIS A FUNCTION, REPLACE MAIN STUFF WITH FUNCTION
import inputSanitization
from main import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

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

        cur_col = job["collection"]

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


def col_list_santitized():
    collection_list = mydb.list_collection_names()
    #TODO: this is not a great way to do this either
    collection_list.remove("jobs")
    collection_list.remove("system.indexes")
    return collection_list

# my_jobs_col = mydb["jobs"]
# for job in my_jobs_col.find():
#     handle_single_job(job)
def add_single_user(curr_first_name, curr_last_name, curr_number, collection):
    is_valid_user, sanitization_msg = inputSanitization.input_sanitizer(curr_first_name, curr_last_name,
                                                                        curr_number)

    return_msg = "ERROR. THERE SHOULD BE SOMETHING ELSE HERE"

    print(f"COLLECTION IS {collection}")

    if not is_valid_user:
        return_msg = f'NOT ADDED TO {collection}!!! FIRST NAME: ({curr_first_name}) LAST NAME: ({curr_last_name}) PHONE NUMBER: ({curr_number})'
        return_msg += '\n' + sanitization_msg
        print(return_msg)
        return return_msg
    elif is_in_database(curr_number, collection):
        return_msg = f'NOT ADDED!!! FIRST NAME: ({curr_first_name}) LAST NAME: ({curr_last_name}) PHONE NUMBER: ({curr_number})'
        return_msg += '\n' + f"USER IS ALREADY IN  COLLECTION {collection} (KEYED FROM PHONE NUMBER)"
        print(return_msg)
        return return_msg
    elif is_valid_user and not is_in_database(curr_number, collection):
        mydict = {"first_name": curr_first_name,
                  "last_name": curr_last_name,
                  "_id": curr_number,
                  "user_enabled": True
                  }
        mydb[collection].insert_one(mydict)

        return_msg = f'ADDED TO COLLECTION {collection} FIRST NAME: ({curr_first_name}) LAST NAME: ({curr_last_name}) PHONE NUMBER: ({curr_number})\n'
    return return_msg


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def bulk_upload_to_database(filename, cur_col):
    with open(UPLOAD_FOLDER + "/" + filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        return_string = ""
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                print(f'\t FIRST NAME:{row[0]} LAST NAME:{row[1]} PHONE NUMBER: {row[2]}.')

                curr_first_name = row[0]
                curr_last_name = row[1]
                curr_number = row[2]

                return_string += add_single_user(curr_first_name, curr_last_name, curr_number, cur_col)

                line_count += 1
        print(f'Processed {line_count} lines.')
        return return_string


def is_in_database(curr_number, collection):
    if mydb[collection].find_one({"_id": curr_number}):
        print(mydb[collection].find({"_id": curr_number}))
        print(f"{curr_number} is already in this collection")
        return True
    else:
        return False