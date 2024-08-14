from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


#Initialize the db
db = SQLAlchemy()
migrate = Migrate()