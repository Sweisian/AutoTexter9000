from flask import Flask, flash, render_template, url_for, request, redirect
import os
import plivo
import pymongo
from werkzeug.utils import secure_filename

import json

import utilities
from bson.objectid import ObjectId
from inputSanitization import input_sanitizer, purify_digits


my_number = '+14844840496'


#TODO: MAKE THIS A FUNCTION, REPLACE MAIN STUFF WITH FUNCTION
myclient = pymongo.MongoClient("mongodb://admin1:admin1@ds253891.mlab.com:53891/pioneers_of_interactive_entertainment_nu")
mydb = myclient["pioneers_of_interactive_entertainment_nu"]
my_users_col = mydb["users"]

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['UPLOAD_FOLDER'] = utilities.UPLOAD_FOLDER

#################### TEST COMMANDS #######################
# for x in my_users_col.find():
#     my_users_col.update_one(x)
#
# for x in my_users_col.find():
#     print(x.get("user_enabled"))
#################### TEST COMMANDS #######################


@app.route('/', methods=["GET"])
def index():
    collection_list = utilities.col_list_santitized()
    return render_template('index.html', collection_list=collection_list)


@app.route('/addUsers', methods=["POST"])
def add_users():
    return_message_list = []
    for i in range(0, 9):
        curr_first_name = request.form['firstName' + str(i)]
        curr_last_name = request.form['lastName' + str(i)]
        curr_number = request.form['number' + str(i)]
        curr_collection = request.values['collectionName']
        return_message_list.append(utilities.add_single_user(curr_first_name, curr_last_name, curr_number, curr_collection))
    return render_template("addedUsers.html", user_data=return_message_list, )


@app.route('/alterUsers', methods=["POST"])
def alter_users():
    cur_col = request.values.get("collectionName")

    if request.values.get("enable_users"):
        print("ENABLE USERS")
        for val in request.values:
            curr_user = mydb[cur_col].find_one({"_id": val})
            if curr_user:
                mydb[cur_col].update_one(curr_user, {"$set": {"user_enabled": True}})
                print(f"USER {curr_user} enabled!")
    if request.values.get("disable_users"):
        print("DISABLE USERS")
        for val in request.values:
            curr_user = mydb[cur_col].find_one({"_id": val})
            if curr_user:
                mydb[cur_col].update_one(curr_user, {"$set": {"user_enabled": False}})
                print(f"USER {curr_user} disabled!")
    if request.values.get("delete_users"):
        print("DELETE USERS")
        for val in request.values:
            curr_user = mydb[cur_col].find_one({"_id": val})
            if curr_user:
                mydb[cur_col].delete_one(curr_user)
                print(f"USER {curr_user} deleted!")

    messages = json.dumps({"collectionName": cur_col})
    return redirect(url_for("see_users", messages=messages))

# @app.route('/addUsersCompletion', methods=["POST"])
# def add_users():
#     for i in range(0,9):
#         curr_name = request.form['name' + str(i)]
#         curr_number = request.form['num' + str(i)]
#         if(curr_name):
#             mydict = { "username": curr_name,"number": curr_number}
#             x = my_users_col.insert_one(mydict)
#     return redirect('/seeUsers')

@app.route('/createCollection', methods=["POST"])
def create_collection():
    collection_name = request.values["collectionName"]

    if collection_name == "system.indexes" or collection_name == "jobs":
        #TODO: Put flash in here
        return redirect(url_for("index"))

    new_collection = mydb[collection_name]
    temp_dict = {"_id": "test"}
    new_collection.insert_one(temp_dict)
    new_collection.delete_one(temp_dict)

    return redirect(url_for("index"))

@app.route('/deleteCollection', methods=["POST"])
def delete_collection():
    name = request.values["collectionName"]
    curr_col = mydb[name]
    curr_col.drop()
    return redirect(url_for("index"))


@app.route('/seeUsers', methods=["GET", "POST"])
def see_users():
    for val in request.values:
        print("val", val, request.values[val], type(val))

    if request.values.get("messages"):
        collection = json.loads(request.values.get("messages")).get("collectionName")
    else:
        collection = request.values.get("collectionName")

    if collection:
        user_data = mydb[collection].find()
        cur_col = collection
    else:
        #Dummy filler data
        user_data = [{"first_name": "No Collection selected",
                      "last_name": "No Collection selected",
                      "_id": "No Collection selected",
                      "user_enabled": False
                      }]
        cur_col = "None Selected"

    collection_list = utilities.col_list_santitized()
    return render_template("displayUsers.html", user_data=user_data, collection_list=collection_list, cur_col=cur_col)


@app.route('/sendTextForm', methods=["GET", "POST"])
def send_text_form():

    collection = request.values.get("collectionName")
    if collection:
        cur_col = collection
    else:
        cur_col = None

    collection_list = utilities.col_list_santitized()
    return render_template("sendText.html", collection_list=collection_list, cur_col=cur_col)


@app.route('/sendBulkText', methods=["POST"])
def send_bulk_text(message_to_send=None):

    #This is when we are triggering a message manually
    if not message_to_send:
        message_to_send = request.values["userinput"]

    collection = request.values["collectionName"]

    if not collection:
        #TODO: add flash here or something
        return redirect(url_for("send_text_form"))

    user_data = mydb[collection].find()

    client = plivo.RestClient(os.environ['PLIVO_AUTH_ID'], os.environ['PLIVO_AUTH_TOKEN'])
    for curr_user in user_data:
        if curr_user.get("user_enabled"):
            curr_num = curr_user["_id"]
            utilities.send_single_text(client, my_number, curr_num, message_to_send)
    return redirect(url_for("send_text_form"))


# @app.route('/recieveText', methods=["POST"])
# def receive_sms():
#     # Sender's phone numer
#     from_number = request.values.get('From')
#     # Receiver's phone number - Plivo number
#     to_number = request.values.get('To')
#     # The text which was received
#     text = request.values.get('Text')
#
#     #Don't do anything if user number is not in database
#     curr_user = my_users_col.find_one({"_id": from_number})
#     if not curr_user:
#         return "Message received", 200
#
#     if str(text).lower() == "stop":
#         if curr_user.get("user_enabled"):
#             my_users_col.update_one(curr_user, {"$set": {"user_enabled": False}})
#             client = plivo.RestClient(os.environ['PLIVO_AUTH_ID'], os.environ['PLIVO_AUTH_TOKEN'])
#             utilities.send_single_text(client, my_number, from_number, "You are unsubscribed. If you wish to resubscribe, please reply with 'START'")
#
#     if str(text).lower() == "start":
#        if not curr_user.get("user_enabled"):
#             my_users_col.update_one(curr_user, {"$set": {"user_enabled": True}})
#
#             client = plivo.RestClient(os.environ['PLIVO_AUTH_ID'], os.environ['PLIVO_AUTH_TOKEN'])
#             utilities.send_single_text(client, my_number, from_number, "You have been resubscribed! To unsubscribe, reply 'STOP'")
#
#     #Print the message
#     print('Message received - From: %s, To: %s, Text: %s' % (from_number, to_number, text))
#
#     return "Message received", 200


@app.route('/uploadHandler', methods=['GET', 'POST'])
def upload_file():

    collection_list = utilities.col_list_santitized()

    collection = request.values.get("collectionName")
    cur_col = collection
    print("\ncurrent collection is: ", cur_col)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print("\nNO FILE")
            flash('No file part')
            return render_template('uploadFile.html', collection_list=collection_list, cur_col=cur_col)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print("\nNO SELECTED FILE")
            flash('No selected file')
            return render_template('uploadFile.html', collection_list=collection_list, cur_col=cur_col)
        if file and utilities.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            if cur_col:
                return_string = utilities.bulk_upload_to_database(filename, cur_col)
            else:
                return_string = "Sorry, you did not select a database"

            return return_string
            # return redirect(url_for('uploaded_file',filename=filename))

    return render_template('uploadFile.html', collection_list=collection_list, cur_col=cur_col)


@app.route('/scheduleMessage', methods=['GET', "POST"])
def schedule_message():

    if request.method == "GET":
        collection_list = utilities.col_list_santitized()
        my_jobs_col = mydb["jobs"]
        job_data = my_jobs_col.find()
        return render_template('scheduleJob.html', job_data=job_data, collection_list=collection_list)
    elif request.method == "POST":
        for val in request.values:
            print(val, request.values[val])

        date = request.form['userdate']
        time = request.form['usertime']
        message = request.form['userinput']
        cur_col = request.form['collectionName']

        my_jobs_col = mydb["jobs"]
        mydict = {"date": date,
                  "time": time,
                  "message": message,
                  "collection": cur_col
                  }
        my_jobs_col.insert_one(mydict)
        return redirect(url_for('schedule_message'))


# Gonna have to do something smarter than this in the future. Not scalable to loop over all entries

@app.route('/alterJobs', methods=["POST"])
def alter_jobs():
    my_jobs_col = mydb["jobs"]
    if request.values.get("delete_jobs"):
        print("DELETE JOBS")
        for val in request.values:
            print("this is val for alter jobs", val)

            # TODO: This is kinda jank, find a better way to only get _id values
            if val != "delete_jobs":
                curr_job = my_jobs_col.find_one({"_id": ObjectId(val)})
            else:
                continue

            if curr_job:
                my_jobs_col.delete_one(curr_job)
                print(f"JOB {curr_job} deleted!")

    return redirect('/scheduleMessage')


@app.route('/get_uploads/<filename>')
def uploaded_file(filename):
    return "Thanks for uploading!"
    # return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/PIE-Form', methods=["POST"])
def pie_form_handler():
    data = request.get_json()

    first_name = data["first_name"]
    last_name = data["last_name"]

    phone_number = data.get("phone_number")
    if phone_number:
        phone_number = purify_digits(phone_number)
        is_valid = input_sanitizer(first_name, last_name, phone_number)
        if is_valid:
            return_message = utilities.add_single_user(first_name, last_name, phone_number, "PIE")
            print(return_message)

            client = plivo.RestClient(os.environ['PLIVO_AUTH_ID'], os.environ['PLIVO_AUTH_TOKEN'])
            message = f"Hello {first_name}! You have been subscribed to the PIE AutoTexter9000. Reply 'STOP' at any time to unsubscribe and 'START to re-subscribe. (AutoTexter9000 developed in house by PIE Exec with love)"
            utilities.send_single_text(client, utilities.MY_NUMBER, phone_number, message)

    return "Thanks for posting"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)


