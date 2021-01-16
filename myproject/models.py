from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# 3 slashes for relative path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)

#     def __repr__(self):
#         return '<User %r>' % self.username

class Image(db.Model):
    name = db.Column(db.String(256), nullable=False)
    characteristics = db.relationship(
        'Characteristics', backref='image', lazy=True)


class Characteristics(db.Model):
    characteristic = db.Column(db.String(64))
