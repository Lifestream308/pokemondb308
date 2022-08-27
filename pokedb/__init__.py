from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_cors import CORS

app = Flask(__name__)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
# Below is elephant sql database 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://jowfndzs:s_fKMzxmDIg6D1gpNd2s_fLNlahUzEh3@heffalump.db.elephantsql.com/jowfndzs'
# Below is Heroku database  
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://lldbmokvitqdzv:b907bebfd62170edc9b76cef753774986c254f2f326897b971d884346c4076a3@ec2-52-72-56-59.compute-1.amazonaws.com:5432/d5cg5ig2v1po9f'
CORS(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from pokedb import routes

# To create Database go into Python, >>>from carflask import db           >>>db.create_all()     
# To delete Database go into Python, >>>from carflask import db           >>>db.drop_all()