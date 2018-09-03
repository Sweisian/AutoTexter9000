import csv
import datetime

import pytz
from flask import Flask, flash, render_template, send_from_directory, request, redirect
import os
import plivo
import pymongo
from werkzeug.utils import secure_filename

import inputSanitization

my_number = '+14844840496'

#TODO CHANGE FILE PATH
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['csv'])


myclient = pymongo.MongoClient("mongodb://admin1:admin1@ds253891.mlab.com:53891/pioneers_of_interactive_entertainment_nu")
mydb = myclient["pioneers_of_interactive_entertainment_nu"]
my_users_col = mydb["users"]

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#################### TEST COMMANDS #######################
# for x in my_users_col.find():
#     my_users_col.update_one(x)
#
# for x in my_users_col.find():
#     print(x.get("user_enabled"))
#################### TEST COMMANDS #######################


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/addUsers', methods=["POST"])
def add_users():

    return_message_list = []
    for i in range(0,9):

        curr_first_name = request.form['firstName' + str(i)]
        curr_last_name = request.form['lastName' + str(i)]
        curr_number = request.form['number' + str(i)]

        return_message_list.append(add_single_user(curr_first_name, curr_last_name, curr_number))

    return render_template("addedUsers.html", user_data=return_message_list)


@app.route('/alterUsers', methods=["POST"])
def alter_users():
    if request.values.get("enable_users"):
        print("ENABLE USERS")
        for val in request.values:
            curr_user = my_users_col.find_one({"_id":val})
            if curr_user:
                my_users_col.update_one(curr_user, {"$set": {"user_enabled": True}})
                print(f"USER {curr_user} enabled!")
    if request.values.get("disable_users"):
        print("DISABLE USERS")
        for val in request.values:
            curr_user = my_users_col.find_one({"_id":val})
            if curr_user:
                my_users_col.update_one(curr_user, {"$set": {"user_enabled": False}})
                print(f"USER {curr_user} disabled!")
    if request.values.get("delete_users"):
        print("DELETE USERS")
        for val in request.values:
            curr_user = my_users_col.find_one({"_id":val})
            if curr_user:
                my_users_col.delete_one(curr_user)
                print(f"USER {curr_user} deleted!")

    return redirect('/seeUsers')

# @app.route('/addUsersCompletion', methods=["POST"])
# def add_users():
#     for i in range(0,9):
#         curr_name = request.form['name' + str(i)]
#         curr_number = request.form['num' + str(i)]
#         if(curr_name):
#             mydict = { "username": curr_name,"number": curr_number}
#             x = my_users_col.insert_one(mydict)
#     return redirect('/seeUsers')


@app.route('/seeUsers')
def see_users():
    user_data = my_users_col.find()

    return render_template("displayUsers.html", user_data=user_data)


@app.route('/sendTextForm')
def send_text_form():
    return render_template("sendText.html")


@app.route('/sendBulkText', methods=["POST"])
def send_bulk_text(message_to_send = None):
    if not message_to_send:
        message_to_send = request.values.get("userinput")

    user_data = my_users_col.find()

    client = plivo.RestClient(os.environ['PLIVO_AUTH_ID'], os.environ['PLIVO_AUTH_TOKEN'])
    for curr_user in user_data:
        if curr_user.get("user_enabled"):
            curr_num = curr_user["_id"]
            send_single_text(client, my_number, curr_num, message_to_send)

        # curr_num = curr_user["_id"]
        # print(curr_num)
        # message_id = messaging_api.send_message(from_=my_number, to='+1' + curr_num, text=request.form['userinput'])

    #TODO: REMOVE TEMP HARDCODE
    # message_id = messaging_api.send_message(from_=my_number, to='+1' + "2033219249", text=request.form['userinput'])

    return render_template("sendText.html")


@app.route('/recieveText', methods=["POST"])
def receive_sms():
    # Sender's phone numer
    from_number = request.values.get('From')
    # Receiver's phone number - Plivo number
    to_number = request.values.get('To')
    # The text which was received
    text = request.values.get('Text')

    #Don't do anything if user number is not in database
    curr_user = my_users_col.find_one({"_id": from_number})
    if not curr_user:
        return "Message received", 200

    if str(text).lower() == "stop":
        if curr_user.get("user_enabled"):
            my_users_col.update_one(curr_user, {"$set": {"user_enabled": False}})
            client = plivo.RestClient(os.environ['PLIVO_AUTH_ID'], os.environ['PLIVO_AUTH_TOKEN'])
            send_single_text(client, my_number, from_number, "You are unsubscribed. If you wish to resubscribe, please reply with 'START'")

    if str(text).lower() == "start":
       if not curr_user.get("user_enabled"):
            my_users_col.update_one(curr_user, {"$set": {"user_enabled": True}})

            client = plivo.RestClient(os.environ['PLIVO_AUTH_ID'], os.environ['PLIVO_AUTH_TOKEN'])
            send_single_text(client, my_number, from_number, "You have been resubscribed! To unsubscribe, reply 'STOP'")

    #Print the message
    print('Message received - From: %s, To: %s, Text: %s' % (from_number, to_number, text))

    return "Message received", 200


@app.route('/uploadHandler', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return_string = bulk_upload_to_database(filename)

            return return_string
            #return redirect(url_for('uploaded_file',filename=filename))

    return render_template('uploadFile.html')


@app.route('/scheduleMessage', methods=['GET'])
def schedule_message():
    return render_template('scheduleJob.html')


@app.route('/storeJob', methods=['POST'])
def store_job():
    for val in request.values:
        print(val, request.values[val])

    date = request.form['userdate']
    time = request.form['usertime']
    message = request.form['userinput']

    my_jobs_col = mydb["jobs"]
    mydict = {"date": date,
              "time": time,
              "message": message
              }
    my_jobs_col.insert_one(mydict)
    return render_template('scheduleJob.html')

# Gonna have to do something smarter than this in the future. Not scalable to loop over all entries


@app.route('/get_uploads/<filename>')
def uploaded_file(filename):
    return "Thanks for uploading!"
    # return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)


def is_in_database(curr_number):
    if my_users_col.find_one({"_id": curr_number}):
        print(my_users_col.find({"_id": curr_number}))
        print(f"{curr_number} is already in the database")
        return True
    else:
        return False


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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def handle_job():
    my_jobs_col = mydb["jobs"]
    for job in my_jobs_col.find():

        user_date = job["date"]
        user_time = job["time"]
        message_to_send = job["message"]

        my_datetime_s = f"{user_date} {user_time}"
        naive_scheduled = datetime.datetime.strptime(my_datetime_s, "%Y-%m-%d %H:%M")
        print(f"MY DATE TIME = {naive_scheduled}")

        local = pytz.timezone("America/Chicago")
        now_time_chicago = datetime.datetime.now(local)
        print(f"CHICAGO TIME = {now_time_chicago}")

        utc = pytz.UTC

        naive_scheduled = utc.localize(naive_scheduled)
        #now_time_chicago = utc.localize(now_time_chicago)
        print(f"LOCALIZED NAIVE SCHEDULED = {naive_scheduled}")

        should_execute = naive_scheduled <= now_time_chicago

        print(naive_scheduled <= now_time_chicago)
        print()

        if should_execute:
            send_bulk_text(message_to_send)

        # local_dt = local.localize(naive, is_dst=None)
        # utc_dt = local_dt.astimezone(pytz.utc)



def bulk_upload_to_database(filename):
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

                return_string += add_single_user(curr_first_name, curr_last_name, curr_number)

                line_count += 1
        print(f'Processed {line_count} lines.')
        return return_string


def add_single_user(curr_first_name, curr_last_name, curr_number):
    is_valid_user, sanitization_msg = inputSanitization.input_sanitizer(curr_first_name, curr_last_name,
                                                                        curr_number)

    return_msg = "ERROR. THERE SHOULD BE SOMETHING ELSE HERE"

    if not is_valid_user:
        return_msg = f'NOT ADDED!!! FIRST NAME: ({curr_first_name}) LAST NAME: ({curr_last_name}) PHONE NUMBER: ({curr_number})'
        return_msg += '\n' + sanitization_msg
        print(return_msg)
        return return_msg
    elif is_in_database(curr_number):
        return_msg = f'NOT ADDED!!! FIRST NAME: ({curr_first_name}) LAST NAME: ({curr_last_name}) PHONE NUMBER: ({curr_number})'
        return_msg += '\n' + "USER IS ALREADY IN DATABASE (KEYED FROM PHONE NUMBER)"
        print(return_msg)
        return return_msg
    elif is_valid_user and not is_in_database(curr_number):
        mydict = {"first_name": curr_first_name,
                  "last_name": curr_last_name,
                  "_id": curr_number,
                  "user_enabled": True
                  }
        my_users_col.insert_one(mydict)

        return_msg = f'ADDED TO DATABASE FIRST NAME: ({curr_first_name}) LAST NAME: ({curr_last_name}) PHONE NUMBER: ({curr_number})\n'
    return return_msg