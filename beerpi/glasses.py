"""This module contains the implementations of the glasses collection and
resource.
"""

import flask
import mongoengine

from beerpi import db
from beerpi.json import JSONResponse
from beerpi.sort import get_sort_keys
from beerpi.users import login_required

class Glass(db.Document):
    name = db.StringField(unique=True)

bp = flask.Blueprint('glasses', __name__)

@bp.route('/glasses', methods=['GET'])
@login_required
def list():
    """ returns a list of all glasses """

    glasses = Glass.objects.all()

    if 'sort' in flask.request.values:
        props = ['name']

        keys = get_sort_keys(flask.request.values['sort'].split(','), props)

        if len(keys) > 0:
            glasses = glasses.order_by(*keys)

    return JSONResponse(glasses.to_json())


@bp.route('/glasses', methods=['POST'])
@login_required
def post():
    data = flask.request.get_json()

    if not 'name' in data:
        return flask.Response('No name specified', 400)

    glass = Glass(name=data['name'])

    try:
        glass.save()
    except mongoengine.NotUniqueError as exp:
        glass = Glass.objects.get(name=data['name'])

    return JSONResponse(glass.to_json())


@bp.route('/glasses/<id>', methods=['GET'])
@login_required
def get(id):
    glass = Glass.objects.get(id=id)

    return JSONResponse(glass.to_json())


@bp.route('/glasses/<id>', methods=['DELETE'])
@login_required
def delete(id):
    Glass.objects.get(id=id).delete()

    return JSONResponse()


@bp.route('/glasses/<id>', methods=['PUT'])
@login_required
def put(id):
    try:
        glass = Glass.objects.get(id=id)
    except mongoengine.DoesNotExist:
        return flask.response('Not found', 404)

    data = flask.request.get_json()

    if 'name' in data:
        glass.name = data['name']

    glass.save()

    return JSONResponse(glass.to_json())

