from flask import Flask, render_template, request, redirect
import os
import plivo
import pymongo



myclient = pymongo.MongoClient("mongodb://admin1:admin1@ds253891.mlab.com:53891/pioneers_of_interactive_entertainment_nu")
mydb = myclient["pioneers_of_interactive_entertainment_nu"]
my_users_col = mydb["users"]
app = Flask(__name__)

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
    for i in range(0,9):
        curr_first_name = request.form['firstName' + str(i)]
        curr_last_name = request.form['lastName' + str(i)]
        curr_number = request.form['number' + str(i)]
        if curr_first_name == '' or curr_number == '':
            print(f"Did not insert name for row {i}. Data is missing.")
            continue
        elif my_users_col.find_one({"number": curr_number}):
            print(my_users_col.find({"number": curr_number}))
            print(f"{curr_number} at row {i} is already in the database")
            continue
        mydict = { "first_name": curr_first_name,
                   "last_name": curr_last_name,
                   "_id": curr_number,
                   "user_enabled": True
                    }
        x = my_users_col.insert_one(mydict)
    return redirect('/seeUsers')

# print("nigeria best country")


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


@app.route('/sendText', methods=["POST"])
def send_text():
    my_number = '+14844840496'

    user_data = my_users_col.find()

    client = plivo.RestClient(os.environ['PLIVO_AUTH_ID'], os.environ['PLIVO_AUTH_TOKEN'])
    for curr_user in user_data:
        curr_num = curr_user["_id"]
        try:
            response = client.messages.create(
                src=my_number,
                dst='+1' + curr_num,
                text=request.form['userinput'],
            )
            print(response.__dict__)
        except plivo.exceptions.PlivoRestError as e:
            print(e)

        # curr_num = curr_user["_id"]
        # print(curr_num)
        # message_id = messaging_api.send_message(from_=my_number, to='+1' + curr_num, text=request.form['userinput'])

    #TODO: REMOVE TEMP HARDCODE
    # message_id = messaging_api.send_message(from_=my_number, to='+1' + "2033219249", text=request.form['userinput'])

    return render_template("sendText.html")



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)