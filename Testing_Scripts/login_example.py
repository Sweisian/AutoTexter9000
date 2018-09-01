from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'pioneers_of_interactive_entertainment_nu'
app.config['MONGO_URI'] = 'mongodb://admin1:admin1@ds253891.mlab.com:53891/pioneers_of_interactive_entertainment_nu'

mongo = PyMongo(app)

@app.route('/')
def index():
    # if 'username' in session:
    #     return 'You are logged in as ' + session['username']

    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'


@app.route('/addUser', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')


@app.route('/removeUser', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')


@app.route('/printUsers', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        users = mongo.db.users
        for user in users
            print(user["name"], user["password"])



        return 'That username already exists!'

    return render_template('register.html')

    return


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host='127.0.0.1', port=8080, debug=True)

