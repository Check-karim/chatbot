class Config:
    # SESSION_COOKIE_SECURE=True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@127.0.0.1:3306/college-inquiry'
    SQLALCHEMY_TRACK_MODIFICATIONS = False