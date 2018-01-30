"""This module contains everything related to an individual beer"""

import flask
import mongoengine

from beerpi import db
from beerpi.beer import Beer
from beerpi.json import JSONResponse
from beerpi.users import User, login_required

class Favorite(db.Document):
    beer = db.ReferenceField(Beer, reverse_delete_rule=db.DENY)
    user = db.ReferenceField(User, reverse_delete_rule=db.DENY)


bp = flask.Blueprint('favorites', __name__)

@bp.route('/users/<id>/favorites', methods=['GET'])
@login_required
def list(id):
    """Returns a list of all favorites for the given user"""

    try:
        user = User.objects.get(id=id)
    except mongoengine.DoesNotExist:
        return flask.Response('No user with id {} found'.format(id), 404)
    except:
        return flask.Resposne('Invalid id {}'.format(id), 400)

    return JSONResponse(Favorite.objects.all().filter(user=user).to_json())


@bp.route('/users/<id>/favorites', methods=['POST'])
@login_required
def post(id):
    """Creates a new favorite for the logged in user for the given beer"""

    if id != str(flask.request.user.id):
        return flask.Response('You can not add a favorite beer for another user', 400)

    data = flask.request.get_json()

    if not 'beer' in data:
        return flask.Response('No beer was specified', 400)

    # find the beer
    try:
        beer = Beer.objects.get(id=data['beer'])
    except mongoengine.DoesNotExist:
        return flask.Resposne('No beer with id {} found'.format(data['beer']), 404)
    except:
        return flask.Resposne('Invalid beer id {}'.format(data['beer']), 400)

    # check to see if a favorite was already created for this beer from this
    # user
    try:
        Favorite.objects.get(beer=beer, user=flask.request.user)
    except mongoengine.DoesNotExist:
        pass
    else:
        return flask.Response('You\'ve already favorited beer {}'.format(data['beer']),
                              400)

    favorite = Favorite(user=flask.request.user,
                        beer=beer)
    try:
        favorite.save()
    except mongoengine.ValidationError as exp:
        return flask.Response('{}'.format(exp), 400)

    return JSONResponse(favorite.to_json())


@bp.route('/users/<id>/favorites/<fid>', methods=['GET'])
@login_required
def get(id, fid):
    """Returns the given favorite for the given user by ids"""

    try:
        user = User.objects.get(id=id)
    except mongoengine.DoesNotExist:
        return flask.Response('Failed to find a user with id {}'.format(id), 404)
    except:
        return flask.Response('Invalid user id {}'.format(id), 400)

    try:
        favorite = Favorite.objects.get(id=fid, user=user)
    except mongoengine.DoesNotExist:
        return flask.Resposne('Failed to find a favorite with id {}'.format(fid), 404)
    except:
        return flask.Response('Invalid favorite id {}'.format(fid), 400)

    return JSONResponse(favorite.to_json())


@bp.route('/users/<id>/favorites/<fid>', methods=['DELETE'])
@login_required
def delete(id, fid):
    """Deletes the given favorite for the given logged in user by ids"""

    if id != str(flask.request.user.id):
        return flask.Response('You can not remove a favorite that does not belong to you',
                              400)

    try:
        favorite = Favorite.objects.get(id=fid, user=flask.request.user)
    except mongoengine.DoesNotExist:
        return flask.Response('No favorite with id {} found'.format(fid), 404)
    except:
        return flask.Response('Invalid favorite id {}'.format(fid), 400)

    favorite.delete()

    return JSONResponse()


@bp.route('/users/<id>/favorites/<fid>', methods=['PUT'])
@login_required
def put(id, fid):
    """Updates the given favorite for the logged in user by ids"""

    if id != str(flask.request.user.id):
        return flask.Response('You can not update a favorite that does not belong to you',
                              400)

    try:
        favorite = Favorite.objects.get(id=fid, user=flask.request.user)
    except mongoengine.DoesNotExist:
        return flask.Response('No favorite with id {} found'.format(fid), 404)
    except:
        return flask.Response('Invalid favorite id {}'.format(fid), 400)

    data = flask.request.get_json()

    # update an of our simple fields
    if 'beer' in data:
        try:
            beer = Beer.objects.get(id=data['beer'])
        except mongoengine.DoesNotExist:
            return flask.Response('No beer with id {} found'.format(data['beer']), 404)
        except:
            return flask.Response('Invalid beer id {}'.format(data['beer']), 400)

        favorite.beer = beer

    try:
        favorite.save()
    except mongoengine.ValidationError as exp:
        return flask.Response('{}'.format(exp), 400)

    return JSONResponse(favorite.to_json())


