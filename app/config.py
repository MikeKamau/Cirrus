import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "YhU6yiKNFufjZOnIlUIAkhisgIIKfztTaMVzcY3dHuQ="
    )
    SECURITY_PASSWORD_SALT = (
        os.environ.get("SECURITY_PASSWORD_SALT")
        or "YhU6yiKNFufjZOnIlUIAkhisgIIKfztTaMVzcY3dHuQ="
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ["admin@domain.com"]
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    BUCKET_NAME = os.environ.get("BUCKET_NAME")
    REGION_NAME = os.environ.get("REGION_NAME")
