"""This module contains the authentication code"""

import hashlib
import json
from functools import wraps

import flask
import mongoengine

from beerpi import db
from beerpi.json import JSONResponse
from beerpi.sort import get_sort_keys

class User(db.Document):
    username = db.StringField(unique=True)
    email = db.EmailField()
    password = db.StringField()

    last_beer_added = db.DateTimeField()


def _basic_auth():
    headers = {
        'WWW-Authenticate': 'Basic realm=\'beerpi\'',
    }

    return flask.Response('Authentication Required', 401, headers)


def authenticate(username, password):
    try:
        user = User.objects.get(username=username)
    except:
        return False

    hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()

    if user.password == hashed:
        return user

    return None


def login_required(func):
    """This decorator protects views"""

    @wraps(func)
    def decorated(*args, **kwargs):
        auth = flask.request.authorization

        if auth is None:
            return _basic_auth()

        user = authenticate(auth.username, auth.password)
        if user is None:
            return _basic_auth()

        setattr(flask.request, 'user', user)

        return func(*args, **kwargs)

    return decorated


###############################################################################
# Views
###############################################################################
bp = flask.Blueprint('users', __name__)

@bp.route('/users', methods=['GET'])
@login_required
def list():
    """Returns a list of all users"""

    users = User.objects.all().exclude('password')

    if 'sort' in flask.request.values:
        props = ['username', 'email']

        keys = get_sort_keys(flask.request.values['sort'].split(','), props)

        if len(keys) > 0:
            users = users.order_by(*keys)

    return JSONResponse(users.to_json())


@bp.route('/users', methods=['POST'])
@login_required
def post():
    """Creates a new user"""

    data = flask.request.get_json()

    if not 'username' in data or not 'password' in data:
        return flask.Response('Username and password are required', 400)

    epass = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()

    user = User(username=data['username'],
                password=epass,
                email='email' in data and data['email'] or None)

    try:
        user.save()
    except mongoengine.NotUniqueError:
        return flask.Response('That user already exists', 409)

    # need to find a cleaner way to serialize an object as json excluding a
    # property...
    clean = json.loads(user.to_json())
    del clean['password']
    clean = json.dumps(clean)

    return JSONResponse(clean)


@bp.route('/users/<id>', methods=['GET'])
@login_required
def get(id):
    """Gets a specific user"""

    try:
        user = User.objects.exclude('password').get(id=id).to_json()
    except mongoengine.DoesNotExist:
        return flask.Response('No user with id {} found'.format(id), 400)
    except mongoengine.errors.ValidationError:
        return flask.Response('Invalid id {}'.format(id), 400)

    return JSONResponse(user.to_json())


@bp.route('/users/<id>', methods=['DELETE'])
@login_required
def delete(id):
    """Deletes a specific user"""

    try:
        User.objects.get(id=id).delete()
    except mongoengine.DoesNotExist:
        return flask.Response('No user with id {} found'.format(id), 400)
    except:
        return flask.Response('Invalid id {}'.format(id), 400)

    return JSONResponse()


@bp.route('/users/<id>', methods=['PUT'])
@login_required
def put(id):
    """Updates a specific user"""

    try:
        user = User.objects.get(id=id)
    except mongoengine.DoesNotExist:
        return flask.Response('No user with id {} found'.format(id), 404)
    except:
        return flask.Response('Invalid id {}'.format(id), 400)

    data = flask.request.get_json()

    # update the email if it's in the data
    if 'email' in data:
        user.email = data['email']

    # if the password is in here, hash it and store it
    if 'password' in data:
        user.password = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()

    user.save()

    return JSONResponse(user.to_json())


