import os
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    g,
    jsonify,
    current_app,
    send_file,
)
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_mail import Mail, Message
import datetime
from app import app, db, mail, s3
from app.models import User, File
from app.forms import (
    LoginForm,
    RegistrationForm,
    FileUploadForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
    ShareForm,
)
from app.email import send_password_reset_email, send_email
from app.token import generate_confirmation_token, confirm_token


# Below are the utility functions for uploading, listing and deleting files
def upload_file_to_s3(file, s3_key=None):
    if s3_key is None:
        s3_key = file.filename
    s3.upload_fileobj(file, app.config["BUCKET_NAME"], s3_key)
    new_file = File(
        filename=file.filename,
        file_size=file.content_length,
        uploaded_on=datetime.datetime.utcnow(),
        user_id=current_user.id,
    )
    db.session.add(new_file)
    db.session.commit()
    return True


def list_files():
    user_files = []
    # Retrieve the files from S3
    response = s3.list_objects_v2(Bucket=app.config["BUCKET_NAME"])
    if "Contents" in response:
        # Extract the file keys from the response
        file_keys = [obj["Key"] for obj in response["Contents"]]
        # Look up the associated user ID for each file
        for file_key in file_keys:
            filename = file_key.split("/")[-1]  # Get the filename from the file key
            file = File.query.filter_by(filename=filename).first()
            if file and file.user_id == current_user.id:
                user_files.append(file_key)
    return user_files


def delete_file_from_s3(s3_key):
    s3.delete_object(Bucket=app.config["BUCKET_NAME"], Key=s3_key)
    file_to_delete = File.query.filter_by(filename=s3_key).first()
    if file_to_delete:
        db.session.delete(file_to_delete)
        db.session.commit()
    return True


def download_file_from_s3(s3_key, file_path):
    s3.download_file(app.config["BUCKET_NAME"], s3_key, file_path)


# View function for the index page/home page
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


# View function for the registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            registered_on=datetime.datetime.now(),
            confirmed=False,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        token = generate_confirmation_token(user.email)
        confirm_url = url_for("confirm_email", token=token, _external=True)
        html = render_template("activate.html", confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(subject, app.config["MAIL_USERNAME"], [user.email], html, html)
        flash("A confirmation email has been sent via email", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


# View function for the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        flash("You are successfully logged in", "success")
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


# View function to perform file related activities i.e. uploading, downloading, deleting and sharing files,
# A user needs to be registered to perform the actions above
@app.route("/filefunctions", methods=["GET", "POST"])
@login_required
def filefunc():
    if not current_user.confirmed:
        flash(
            "Please confirm your email address to be able to use the file hosting functionality of the application",
            "error",
        )
        return redirect(url_for("index"))
    else:
        files = list_files()
        return render_template("filefunctions.html", files=files)


# Routes for uploading, downloading, deleting and sharing files
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    if file.filename:
        upload_file_to_s3(file)
    return redirect(url_for("filefunc"))


@app.route("/delete", methods=["POST"])
def delete():
    s3_key = request.form["s3_key"]
    delete_file_from_s3(s3_key)
    return redirect(url_for("filefunc"))


@app.route("/download", methods=["POST"])
def download():
    s3_key = request.form["s3_key"]
    file_path = (
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        + f"/downloads/{s3_key}"
    )
    download_file_from_s3(s3_key, file_path)
    print(file_path)
    return send_file(file_path, as_attachment=True)


@app.route("/share", methods=["GET", "POST"])
@login_required
def share():
    form = ShareForm()
    s3_key = request.form.get("s3_key")
    if form.validate_on_submit():
        email = form.email.data
        expiration_time = 3600  # Expirate time in seconds, the pre-signed url will be valid for one hour
        presigned_url = generate_presigned_url(s3_key, expiration_time)
        # Send the email
        subject = "Shared File Link"
        body = f"Click the link below to access the shared file:\n\n{presigned_url}"
        send_sharing_email(email, presigned_url)
        flash("Share link has been sent!", "success")
        return redirect(url_for("share"))
    return render_template("share.html", form=form, s3_key=s3_key)


# Utility function for sending an email with a pre-sigend url when sharing a file
def send_sharing_email(email, presigned_url):
    subject = "Shared File URL"
    sender = app.config["MAIL_USERNAME"]
    recipients = [email]
    body = f"Here is the shared file URL: {presigned_url}"
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = body
    mail.send(msg)


def generate_presigned_url(s3_key, expiration_time):
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": app.config["BUCKET_NAME"], "Key": s3_key},
        ExpiresIn=expiration_time,
    )
    return url


# View function for the logout functionality
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


# View function for the page where users enter their email address to receive the password reset link
@app.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for the instructions to reset your password", "success")
        return redirect(url_for("login"))
    return render_template(
        "reset_password_request.html", title="Reset Password", form=form
    )


# View function for the password reset page, where users enter their new password
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset", "success")
        return redirect(url_for("login"))
    return render_template("reset_password.html", form=form)


# View function for that handles the user email confirmation
# Users must confirm their email to be able to use the file hosting functionality
@app.route("/confirm/<token>")
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash("The confirmation link is Invalid or has expired", "error")
    user = User.query.filter_by(email=email).first()
    if user.confirmed:
        flash("Account has already been confirmed please login", "error")
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("Thank you for confirming your account", "success")
    return redirect(url_for("index"))
