"""This module contains everything related to breweries"""

import flask
import mongoengine

from beerpi import db
from beerpi.json import JSONResponse
from beerpi.sort import get_sort_keys
from beerpi.users import login_required

class Brewery(db.Document):
    name = db.StringField(unique=True)
    city = db.StringField()
    state = db.StringField()

bp = flask.Blueprint('breweries', __name__)

@bp.route('/breweries', methods=['GET'])
@login_required
def list():
    """Returns a list of all breweries"""

    breweries = Brewery.objects.all()

    if 'sort' in flask.request.values:
        props = ['name', 'city', 'state']

        keys = get_sort_keys(flask.request.values['sort'].split(','), props)

        breweries = breweries.order_by(*keys)

    return JSONResponse(breweries.to_json())


@bp.route('/breweries', methods=['POST'])
@login_required
def post():
    """Creates a new brewery"""

    data = flask.request.get_json()

    if not 'name' in data:
        return flask.Response('No name specified', 400)

    brewery = Brewery(name=data['name'],
                      city='city' in data and data['city'] or None,
                      state='state' in data and data['state'] or None)

    try:
        brewery.save()
    except mongoengine.NotUniqueError as exp:
        brewery = Brewery.objects.get(name=data['name'])

    return JSONResponse(brewery.to_json())


@bp.route('/breweries/<id>', methods=['GET'])
@login_required
def get(id):
    """Gets a brewery by id"""

    brewery = Brewery.objects.get(id=id)

    return JSONResponse(brewery.to_json())


@bp.route('/breweries/<id>', methods=['DELETE'])
@login_required
def delete(id):
    """Deletes the given brewery if no beers are associated with it."""

    brewery = Brewery.objects.get(id=id).delete()

    return JSONResponse()


@bp.route('/breweries/<id>', methods=['PUT'])
@login_required
def put(id):
    """Updates a brewery by id"""

    try:
        brewery = Brewery.objects.get(id=id)
    except mongoengine.DoesNotExist:
        return flask.response('Not found', 404)

    data = flask.request.get_json()

    props = ['name', 'city', 'state']

    for item in props:
        if item in data:
            setattr(brewery, item, data[item])

    brewery.save()

    return JSONResponse(brewery.to_json())

