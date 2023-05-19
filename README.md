**Cirrus**\
Cirrus, a very simple and lightweight cloud filestore that utilizes Flask and Boto3

**Features**\
The app also implements the following features:

* User registration
* Ability to send confirmation emails to registered users
* Login and logout
* Password reset
* Uploading, listing, downloading, deleting and sharing files through S3 pre-signed urls (Users must confirm their email addresses after registration to use these features)

**Setup**
1. Clone the project to your local system **git clone https://github.com/MikeKamau/cirrus.git**

2. Create a python virtual environment using conda and the provided environment.yml file

3. Set the following environment variables on your system e.g. in your ~/.bashrc file in Linux

  * **SECRET_KEY** - The secret key that will be used for securely signing the session cookie and can be used for any other security related needs by extensions or your application
  * **SECURITY_PASSWORD_SALT** - Specifies the HMAC salt. This is only used if the password hash type is set to something other than plain text. Defaults to None
  * **SQLALCHEMY_DATABASE_URI** - The database URI that should be used for the connection, for this app it'll be the path to the sqlite database
  * **SQLALCHEMY_TRACK_MODIFICATIONS** - Whether to track modifications to the SQLAlchemy session
  * **MAIL_SERVER** - Hostname of the mail server to be used for sending emails
  * **MAIL_PORT** - Port number used by the mail server
  * **MAIL_USE_TLS** - Whether or not the mail server utilizes TLS
  * **MAIL_USERNAME** - Username of the account to be used for sending out emails from the app
  * **MAIL_PASSWORD** - Password of the account to be used for sending out emails from the app
  * **ADMINS** - Email address of the individual that should receive alerts as per the set logging level
  * **FLASK_ENV** - What context Flask is running in i.e development or production. It defaults to production
  * **AWS_ACCESS_KEY_ID** - The AWS access key id that Boto3 will use in the background to access S3 (The access key must belong to a user with the necessary S3 permissions to upload, list, download and delete files)
  * **AWS_SECRET_ACCESS_KEY** - The AWS secret access key corresponding to the access key id you've specified.
  * **BUCKET_NAME** - The S3 bucket name to be used for storing files.
  * **BUCKET_NAME** - The region in which the S3 bucket above resides in.

4. Change directory into the project folder i.e cd /path/to/cirrus/folder 

5. Run the app using the flask run command i.e. flask run  

6. Access the app on http://localhost:5000
