import uuid

from flask import Flask, render_template, request, flash, redirect, session
import os
from flask_sqlalchemy import SQLAlchemy
import json
from app_model import User
import aws

app = Flask(__name__)
app.debug = True
app.secret_key = "GoWentGone1290edSt56{io"
project_dir = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
def home():
    if "user_email" in session:
        return redirect("/main")
    else:
        return redirect("/login")

#Create Music Table
@app.route("/create-table")
def create_table():
    aws.create_table(table_name="Music1")
    return "Success"

# Fetching all user details stored in json file
@app.route("/populate-users")
def populate_users():
    users_file = "{}/samples/users_copy.json".format(project_dir)
    data = {}
    with open(users_file, "r") as f:
        data = json.load(f)
    if data:
        for user in data:
            aws.put_user_to_db(item_dict=user)
            print(user.__str__() + "added")
    return "Success"

# Fetching all music details stored in a2.json file
@app.route("/populate-music")
def populate_music():
    music_file = "{}/samples/a2.json".format(project_dir)
    data = {}
    with open(music_file, "r") as f:
        data = json.load(f)
    if data:
        for music in data["songs"]:
            aws.put_music(music)
            aws.upload_to_s3(music.get("img_url", ""))
            print(music.__str__() + "added")
    return "Success"


def valid_login(email, password):
    user = aws.get_user_with_email(email)
    if user:
        return user if password == user.password else None
    else:
        return None

# User validation
@app.route('/login', methods=['POST', 'GET'])
def user_login():
    error = None
    if request.method == 'POST':
        session.pop("message", "")
        user = valid_login(request.form['email'],
                           request.form['password'])
        if user:
            session["user_email"] = user.email
            session["user_name"] = user.username
            return redirect("/main")
        else:
            error = 'Invalid email/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    context = {
        "title": "Login",
        "message": session.get("message", "")
    }
    print(context)
    return render_template('login.html', error=error, context=context)

# Registering user from Register Page and storing it to "user" table in dynamo database
@app.route('/register', methods=['POST', 'GET'])
def user_register():
    session.pop("message", "")
    error = None
    if request.method == 'POST':
        user = aws.get_user_with_email(request.form['email'])
        if user:
            error = "User with email already exists"
        else:
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            aws.put_user_to_db(email=email, password=password, username=username)
            session["message"] = "Successfully registered! Please login"
            return redirect("/login")
    context = {
        "title": "Register"
    }
    return render_template('register.html', error=error, context=context)

# Logout Function
@app.route('/logout')
# @login_required
def logout():
    session.pop("user_email", "")
    session.pop("user_name", "")
    session["message"] = "You have been logged out!"
    return redirect('/login')


@app.route("/subscriptions")
def subscriptions():
    user = session.get("user_email", "")
    if user:
        subs = aws.get_user_subscriptions(user)
        return render_template("subscriptions.html", user=session.get("user_name", ""), subs=subs)
    session["message"] = "Please login to see subscriptions!"
    return redirect("/login")


@app.route("/remove-subscription/<id>")
def remove_subscribe(id):
    success = aws.delete_subscription(id)
    message = "Removed" if success else "Try Again"
    return {
        "success": success,
        "message": message
    }

#Main Page
@app.route("/main", methods=['POST', 'GET'])
def dashboard():
    user = session.get("user_name", "")
    if user:
        subs = aws.get_user_subscriptions(session.get("user_email", ""))
        user_subs = [sub["music"] for sub in subs]
        music_list = aws.get_music_list()
        music_list = [music for music in music_list if music not in user_subs]
        title = request.form.get("title", "")
        year = request.form.get("year", "")
        artist = request.form.get("artist", "")
        if title:
            music_list = [music for music in music_list if str(music["title"]).lower().__contains__(title.lower())]
        if year:
            music_list = [music for music in music_list if str(music["year"]).__eq__(year)]
        if artist:
            music_list = [music for music in music_list if str(music["artist"]).lower().__contains__(artist.lower())]
        return render_template("main.html", user=user, music=music_list)
    else:
        session["message"] = "Please login!"
        return redirect("/login")


@app.route("/subscribe/<title>")
def subscribe(title):
    user = session.get("user_email", "")
    music = aws.get_music_by_title(title)
    if music and user:
        id = uuid.uuid4().hex
        subscription = {
            "id": id,
            "user": user,
            "music": music
        }
        aws.put_subscription(subscription)
        return {
            "success": True,
            "message": "Subscribed"
        }
    else:
        return {
            "success": False,
            "message": "Try again"
        }


if __name__ == '__main__':
    app.run(host="127.0.0.1",port=8080, debug=True)
