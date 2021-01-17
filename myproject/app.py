from flask import Flask, render_template, request, redirect, flash, abort
import os
from werkzeug.utils import secure_filename

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

# lets display all the images first
@app.route('/', methods=["GET"])
def index():
    # by default flask looks for template folder in the root directory
    pictures = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template("gallery.html", pictures=pictures)

# helper function to check for allowed_files, increase security


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


@app.route('/public', methods=['GET'])
def public_pics():
    pass


@app.route('/private', methods=["GET"])
def private_pics():
    pass


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
