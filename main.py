import os
import subprocess
from flask import Flask, flash, request, redirect, url_for, render_template, g
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'svg'}
LOCKFILE="axidraw.lock"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LOCKFILE'] = LOCKFILE

def is_printing():
    return os.path.isfile(app.config['LOCKFILE'])

if is_printing():
    os.remove(app.config['LOCKFILE'])

@app.route("/")
def index():
    return render_template("index.html", uploads=os.listdir(app.config['UPLOAD_FOLDER']), is_printing=is_printing())

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/preview/<filename>")
def preview(filename):
    return subprocess.run(["axicli","-L 2", "-T","--preview",f"uploads/{filename}"], capture_output=True).stderr

@app.route("/toggle")
def toggle():
    subprocess.run(["axicli","-L 2", "-m","toggle"])
    return redirect(url_for('index'))

@app.route("/align")
def align():
    subprocess.run(["axicli","-L 2", "-m","align"])
    return redirect(url_for('index'))


@app.route("/print/<filename>")
def print(filename):
    f = open(app.config['LOCKFILE'], "x")
    a = subprocess.run(["axicli","-L 2",f"uploads/{filename}"], capture_output=True).stderr
    f.close()
    os.remove(app.config['LOCKFILE'])
    return redirect(url_for('index'))


@app.route("/upload", methods=['GET', 'POST'])
def upload_svg():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
    return redirect(url_for('index'))


