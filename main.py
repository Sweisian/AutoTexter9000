from flask import Flask, render_template, request, redirect
import pymongo

myclient = pymongo.MongoClient("mongodb://admin1:admin1@ds253891.mlab.com:53891/pioneers_of_interactive_entertainment_nu")

mydb = myclient["pioneers_of_interactive_entertainment_nu"]

my_users_col = mydb["users"]

app = Flask(__name__)


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
        elif my_users_col.find_one({"number" : curr_number}):
            print(my_users_col.find({"number": curr_number}))
            print(f"{curr_number} at row {i} is already in the database")
            continue
        mydict = { "first_name": curr_first_name, "last_name" : curr_last_name, "number": curr_number}
        x = my_users_col.insert_one(mydict)
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
    return_string = ""
    for x in my_users_col.find({},{"_id": 0, "name": 1, "number": 1}):
        return_string = return_string + str(x) + "<br>"
    return return_string


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)