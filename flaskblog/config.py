import os

class Config:
    # A secret key protects your website from attacks. Read more in future.
    SECRET_KEY              = os.environ.get("FLASKBLOG_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("FLASKBLOG_SQLALCHEMY_DATABASE_URI")
    MAIL_SERVER             = os.environ.get("FLASKBLOG_MAIL_SERVER")
    MAIL_PORT               = 587
    MAIL_USE_TLS            = True
    MAIL_USERNAME           = os.environ.get("FLASKBLOG_MAIL_USERNAME")
    MAIL_PASSWORD           = os.environ.get("FLASKBLOG_MAIL_PASSWORD")