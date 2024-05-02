from extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255),nullable=False,unique=True)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now(),onupdate=db.func.now())

    @property
    def data(self):
        return{
            'id':self.id,
            'email':self.email,
            'password':self.password
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_all(cls):
        r = cls.query.all()
        result = []

        for i in r:
            result.append(i.data)
        return result
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id == id).first()

    @classmethod
    def get_by_email_password(cls, email,password):
        return cls.query.filter(cls.email == email, cls.password == password).first()
