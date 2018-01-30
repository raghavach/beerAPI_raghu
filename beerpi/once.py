"""This module contains the once route for setting up the admin user"""

import flask

from beerpi.users import User

bp = flask.Blueprint('once', __name__)

@bp.route('/once')
def list():
    """Creates the admin user if it doesn't exist.  Always returns a 404"""

    user = User.objects.get(username='admin')

    if user is None:
        password = hash
        user = User(username='admin',
                    password='8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918')
        user.save()

    return flask.Response('Not Found', 404)

