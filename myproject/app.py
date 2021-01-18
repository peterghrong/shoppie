from flask import Flask, render_template, request, redirect, flash, abort, url_for
import os
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

# some configurations
app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS
app.config["APP_ROOT"] = APP_ROOT
UPLOAD_FOLDER = os.path.join(app.config["APP_ROOT"], "static/")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'anystringthatyoulike'
# extra security
app.config["MAX_CONTENT_LENGTH"] = 1024*1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class Register(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = password = PasswordField(
        'Password', validators=[DataRequired()])


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    pics = db.relationship('Pic', backref='owner', lazy="dynamic")


class Pic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# lets display all the images first
@app.route('/', methods=["GET"])
def index():
    # by default flask looks for template folder in the root directory
    pictures = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template("gallery.html", pictures=pictures)

# helper function to check for allowed_files, increase security


@app.route('/register', methods=["GET", "POST"])
def registration():
    register = Register()
    if register.validate_on_submit():
        new_user = User()
        # id field is automatically populated
        new_user.username = register.username.data
        new_user.password_hash = register.username.data
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('register.html', register=register)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me = {}'.format(
            form.username.data, form.remember_me.data))
        return redirect("/index")
    print("what")
    return render_template('login.html', title='Login', form=form)


def register():
    pass


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


@app.route('/upload', methods=["POST"])
def upload():
    if request.method == 'POST':
        # if the request is empty then its bad for security
        if 'pics' not in request.files:
            flash("Missing file part")
            return redirect('/')

        files = request.files.getlist("pics")

        for file in files:
            # check if file names are missing
            if file.filename == '':
                flash("Missing file name")
                return redirect('/')

            if file and allowed_file(file.filename):
                # secure_file name protects the file structure
                filename = secure_filename(file.filename)

                # check if the upload folder exists in the file structure
                if not os.path.isdir(app.config["UPLOAD_FOLDER"]):
                    os.makedir(app.config["UPLOAD_FOLDER"])

                dest = "/".join([app.config["UPLOAD_FOLDER"], filename])
                file.save(dest)
            else:
                abort(400)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
