"""This module contains everything related to an individual beer"""

import flask
import mongoengine

from datetime import datetime
from dateutil.relativedelta import relativedelta

from beerpi import db
from beerpi.brewery import Brewery
from beerpi.glasses import Glass
from beerpi.json import JSONResponse
from beerpi.sort import get_sort_keys
from beerpi.users import User, login_required

class Beer(db.Document):
    name = db.StringField(unique=True)
    ibu = db.IntField()
    calories = db.IntField()
    abv = db.FloatField()
    style = db.StringField()
    brewery = db.ReferenceField(Brewery, reverse_delete_rule=db.DENY)
    glass = db.ReferenceField(Glass, reverse_delete_rule=db.DENY)

    rating = db.DecimalField(precision=2)

    added_by = db.ReferenceField(User, reverse_delete_rule=db.DENY)


bp = flask.Blueprint('beers', __name__)

@bp.route('/beers', methods=['GET'])
@login_required
def list():
    """Returns a list of all beers"""

    beers = Beer.objects.all()

    if 'sort' in flask.request.values:
        props = ['name', 'ibu', 'calories', 'abv', 'style', 'rating']

        keys = get_sort_keys(flask.request.values['sort'].split(','), props)

        if len(keys) > 0:
            beers = beers.order_by(*keys)

    return JSONResponse(beers.to_json())


@bp.route('/beers', methods=['POST'])
@login_required
def post():
    """Creates a new beer"""

    # figure out who's adding this beer, and if they've added one within the
    # last 24 hours
    if flask.request.user.last_beer_added is not None:
        wait = flask.request.user.last_beer_added + relativedelta(hours=+24)

        if wait > datetime.now():
            return flask.Response('You can only add one beer every 24 hours. ' \
                                  'You can add another beer on {}'.format(wait),
                                  400)

    data = flask.request.get_json()

    if not 'name' in data:
        return flask.Response('No name specified', 400)

    # create the beer
    beer = Beer(name=data['name'],
                ibu='ibu' in data and data['ibu'] or None,
                calories='calories' in data and data['calories'] or None,
                abv='abv' in data and data['abv'] or None,
                style='style' in data and data['style'] or None)


    # now look for the brewery by id
    if 'brewery' in data:
        brewery = Brewery.objects.get(id=data['brewery'])
        if brewery is not None:
            beer.brewery = brewery

    # now look for the glass by id
    if 'glass' in data:
        glass = Glass.objects.get(id=data['glass'])
        if glass is not None:
            beer.glass  = glass

    try:
        beer.save()
    except mongoengine.NotUniqueError as exp:
        return flask.Response('A beer with the name "{}" already exists' \
                              .format(data['name']), 409)

    flask.request.user.last_beer_added = datetime.now()
    flask.request.user.save()

    return JSONResponse(beer.to_json())


@bp.route('/beers/<id>', methods=['GET'])
@login_required
def get(id):
    """Returns the given beer by id"""

    beer = Beer.objects.get(id=id)

    return JSONResponse(beer.to_json())


@bp.route('/beers/<id>', methods=['DELETE'])
@login_required
def delete(id):
    """Deletes the given beer by id"""

    try:
        Beer.objects.get(id=id).delete()
    except mongoengine.DoesNotExist:
        return flask.Response('No beer with id {} found'.format(id), 404)

    return JSONResponse()


@bp.route('/beers/<id>', methods=['PUT'])
@login_required
def put(id):
    """Updates the given beer by it's id"""

    try:
        beer = Beer.objects.get(id=id)
    except mongoengine.DoesNotExist:
        return flask.Response('Not found', 404)

    data = flask.request.get_json()

    # update an of our simple fields
    props = ['name', 'ibu', 'calories', 'abv', 'style']
    for item in props:
        if item in data:
            setattr(beer, item, data[item])

    # check if we got a brewery update
    if 'brewery' in data:
        brewery = Brewery.objects.get(id=data['brewery'])
        if brewery is not None:
            beer.brewery = brewery

    # check if we got a glass update
    if 'glass' in data:
        glass = Glass.objectsget(id=data['glass'])
        if glass is not None:
            beer.glass = glass

    beer.save()

    return JSONResponse(beer.to_json())


