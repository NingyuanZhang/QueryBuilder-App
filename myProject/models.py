from myProject import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

# Load the current user and get their ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class Record(db.Model, UserMixin):

    # Create a table in the db
    __tablename__ = 'records'

    Query = db.Column(db.String(128), primary_key = True)
    TableName = db.Column(db.String(64), unique=True, index=True)

    def __init__(self,Query,TableName):
        self.Query = Query
        self.TableName = TableName

db.drop_all()
db.create_all()
