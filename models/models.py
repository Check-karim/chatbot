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


#  course_tracking table
class Course_tracking(db.Model):
    __tablename__ = 'course_tracking'

    course_tracking_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(255),nullable=False)
    user_id = db.Column(db.Integer,nullable=False)
    created_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now(),onupdate=db.func.now())

    def __init__(self,course_id,status):
        self.course_id = course_id
        self.status = status
    
    def __repr__(self):
         return{
            'order_id':self.order_id,
            'status':self.status
        }
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.order_id == id).first()
    

# course items table
class Course_items(db.Model):
    __tablename__ = 'course_items'

    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False,unique=True)
    label = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now(),onupdate=db.func.now())

    def __init__(self,item_id,name,label):
        self.item_id = item_id
        self.name = name
        self.label = label
    
    def __repr__(self):
         return{
            'item_id':self.item_id,
            'name':self.name,
            'label':self.label
        }
    


# course tables
class Courses(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer,nullable=False)
    item_id = db.Column(db.Integer,nullable=False)
    user_id = db.Column(db.Integer,nullable=False)
    label = db.Column(db.Integer,nullable=False)
    created_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(),nullable=False, server_default=db.func.now(),onupdate=db.func.now())

    def __init__(self,course_id,item_id,user_id,label):
        self.course_id = course_id
        self.item_id = item_id
        self.user_id = user_id
        self.label = label
    
    def __repr__(self):
         return{
            'course_id':self.course_id,
            'item_id':self.item_id,
            'user_id':self.user_id,
            'label':self.label,
        }

