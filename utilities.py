import csv
import datetime
import os

import plivo
import pytz

import pymongo

#TODO: MAKE THIS A FUNCTION, REPLACE MAIN STUFF WITH FUNCTION
import inputSanitization

#TODO CHANGE FILE PATH
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['csv'])

myclient = pymongo.MongoClient("mongodb://admin1:admin1@ds253891.mlab.com:53891/pioneers_of_interactive_entertainment_nu")
mydb = myclient["pioneers_of_interactive_entertainment_nu"]
my_users_col = mydb["users"]

MY_NUMBER = '+14844840496'

FIRSTNAME = "$$FIRSTNAME$$"


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
    #TODO: I should probably change the way input_sanitizer works to return correct stuff instead of boolean and a message
    curr_number = inputSanitization.purify_digits(curr_number)
    is_valid_user, sanitization_msg = inputSanitization.input_sanitizer(curr_first_name, curr_last_name,
                                                                        curr_number)
    return_msg = "ERROR. THERE SHOULD BE SOMETHING ELSE HERE"

    #print(f"COLLECTION IS {collection}")

    if not is_valid_user:
        return_msg = f'NOT ADDED TO ({collection})!!! FIRST NAME: ({curr_first_name}) LAST NAME: ({curr_last_name}) PHONE NUMBER: ({curr_number})'
        return_msg += '\n' + sanitization_msg
        print(return_msg)
        return return_msg
    elif is_in_database(curr_number, collection):
        return_msg = f'NOT ADDED TO ({collection})!!! FIRST NAME: ({curr_first_name}) LAST NAME: ({curr_last_name}) PHONE NUMBER: ({curr_number})'
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

        return_msg = f'ADDED TO COLLECTION ({collection}) FIRST NAME: ({curr_first_name}) LAST NAME: ({curr_last_name}) PHONE NUMBER: ({curr_number})\n'
    return return_msg


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def bulk_upload_to_database(filename, cur_col):
    with open(UPLOAD_FOLDER + "/" + filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        return_string_list = []
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                print(f'\t FIRST NAME:{row[0]} LAST NAME:{row[1]} PHONE NUMBER: {row[2]}.')

                curr_first_name = row[0]
                curr_last_name = row[1]
                curr_number = row[2]

                return_string_list.append(add_single_user(curr_first_name, curr_last_name, curr_number, cur_col))

                line_count += 1
        print(f'Processed {line_count} lines.')
        return return_string_list


def is_in_database(curr_number, collection):
    if mydb[collection].find_one({"_id": curr_number}):
        print(mydb[collection].find({"_id": curr_number}))
        print(f"{curr_number} is already in this collection")
        return True
    else:
        return False


def filler_replacement(first_name, message):
    message = message.replace(FIRSTNAME, first_name)
    return message
