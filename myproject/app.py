from flask import Flask, render_template, request, redirect, flash, abort, url_for
import os
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt, generate_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import LoginManager, login_user

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
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(userid):
    return User.query.filter(User.id == userid).first()


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log in')

    def is_correct_password(self, plaintext):
        if bcrypt.check_password_hash(self._password, plaintext):
            return True
        return False


class Register(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = password = PasswordField(
        'Password', validators=[DataRequired()])
    submit = SubmitField(label=('Sign up'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True, unique=True)
    _password = db.Column(db.String(128))
    pics = db.relationship('Pic', backref='owner', lazy="dynamic")

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def __repr__(self):
        print(self.id)
        print(self.username)
        return


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
    print("it worked1")

    if register.validate_on_submit():
        new_user = User()
        # id field is automatically populated
        new_user.username = register.username.data
        new_user.password = register.password.data
        db.session.add(new_user)
        db.session.commit()
        print("it worked")
        return redirect(url_for('index'))

    return render_template('register.html', register=register)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first_or_404()
        if user.is_correct_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        return redirect(url_for('login'))
    return render_template('login.html', form=form)


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
