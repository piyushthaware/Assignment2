from flask_login import UserMixin
from flask import session


class User(UserMixin):
    username: str = ""
    email: str = ""
    password: str = ""

    def __int__(self, username, email, password):
        self.username = username
        self.password = password
        self.email = email

    def add_user(self):
        pass

    def __str__(self):
        return self.username

    def log_in(self):
        session["user_email"] = self.email
