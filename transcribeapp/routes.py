from transcribeapp import application
from flask import render_template, request, redirect, flash, session, abort
from werkzeug.utils import secure_filename
from .helpers import (allowed_file, upload_file_to_s3, get_word_list_from_s3,
                      scan_transcribe_table, check_user)


@application.route("/", methods=["GET"])
@application.route("/<string:id>", methods=['GET'])
def home(id=None):
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        job_list = scan_transcribe_table()

        if not job_list:
            flash("No transcription job found.")
        key_list = ["JobId", "CreatedAt", "CompletedAt", "Status", "FileName", "FileFormat"]
        word_list = []
        if id:
            for job in job_list:
                if job["JobId"] == id:
                    if "S3Key" in job.keys():
                        word_list = get_word_list_from_s3(job['S3Key'])
                    else:
                        word_list = ['Transcript file not exist.']
                
        return render_template("index.html", job_list=job_list,
                               key_list=key_list, word_list=word_list,
                               username=session.get('username'))


@application.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', None)
    password = request.form.get('password', None)
    note = 'Please fill in username and password.'
    if username and password:
        verified, note = check_user(username, password)
        if verified:
            session['logged_in'] = True
            session['username'] = username
    flash(note)
    return redirect("/")


@application.route("/logout")
def logout():
    session['logged_in'] = False
    session['username'] = None
    flash("Successfully logged out.")
    return redirect("/")


@application.route("/", methods=["POST"])
def upload_file():
    if "files[]" not in request.files:
        print("Please select a file")
    else:
        files = request.files.getlist("files[]")
        for f in files:
            if f.filename == "":
                flash("Please select a file")
            elif f and allowed_file(f.filename):
                f.filename = secure_filename(f.filename)
                output = upload_file_to_s3(f)
    return redirect("/")



if __name__ == "__main__":
    application.run()
