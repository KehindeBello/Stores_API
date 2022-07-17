import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt import JWT
from datetime import timedelta

from security import authenticate, identity
from resources.user import UserRegister, User
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_CUSTOM_URL','sqlite:///data.db')#"postgresql://kehinde:kehindebello@localhost:5432/kehinde" #os.environ.get('DATABASE_CUSTOM_URL')#,'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Kehinde'
api = Api(app)

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

#Api works with resource and every resource has to be a class
app.config['JWT_AUTH_URL_RULE'] = '/login' #changed the authentication endpoint
jwt = JWT(app, authenticate, identity) #/auth

#configure JWT to expire within an hour
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=600)
#config JWT auth key name to be 'email' instead of default 'username'
#app.config['JWT_AUTH_USERNAME_KEY'] = 'email'

app.config['PROPAGATE_EXCEPTIONS'] = True

#customize JWT auth response, include user_id in response body
# Remember that the identity should be what you’ve returned by the authenticate() function
@jwt.auth_response_handler
def customized_response_handler(access_token, identity):
    return jsonify({
        'access_token':access_token.decode('utf-8'),
        'user_id': identity.id
    })

api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(User, '/user/<int:user_id>')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
