from app import app, db
from models import *
from views import *


def create_tables():
    with db:
        db.create_tables([Order])
    
if __name__ == '__main__' or __name__ == 'main':
    create_tables()
    app.run()