"""This module contains everything related to an individual beer"""

import flask
import mongoengine

from beerpi import db
from beerpi.beer import Beer
from beerpi.json import JSONResponse
from beerpi.sort import get_sort_keys
from beerpi.users import User, login_required

class Review(db.Document):
    beer = db.ReferenceField(Beer, reverse_delete_rule=db.DENY)
    user = db.ReferenceField(User, reverse_delete_rule=db.DENY)

    aroma = db.IntField(min_value=1, max_value=5)
    appearance = db.IntField(min_value=1, max_value=5)
    taste = db.IntField(min_value=1, max_value=10)
    palate = db.IntField(min_value=1, max_value=5)
    bottle_style = db.IntField(min_value=1, max_value=5)

    overall = db.DecimalField(precision=2)


    total = 30 # update this if anything is changed in the fields


    def calculate(self):
        """This method updates the calculated rating of a review.  It takes
        the currently assigned ratings for each property, adds them up, then
        divides by the total points to calculate the percentage of points
        given.  Once that value is calculated, it is divided by 0.2 to the
        value into a "5 star" rating.
        """

        rating = 0

        props = ['aroma', 'appearance', 'taste', 'palate', 'bottle_style']
        for item in props:
            rating += getattr(self, item, 0)

        self.overall = (rating / self.total) / .2


###############################################################################
# Views
###############################################################################
bp = flask.Blueprint('reviews', __name__)

@bp.route('/beers/<id>/reviews', methods=['GET'])
@login_required
def list(id):
    """Returns a list of all reviews for the given beer"""

    try:
        beer = Beer.objects.get(id=id)
    except mongoengine.DoesNotExist:
        return flask.Response('No beer with id {} found'.format(id), 404)
    except:
        return flask.Resposne('Invalid id {}'.format(id), 400)

    reviews = Review.objects.all().filter(beer=beer)

    if 'sort' in flask.request.values:
        props = ['aroma', 'appearance', 'taste', 'palate', 'bottle_style',
                 'overall']

        keys = get_sort_keys(flask.request.values['sort'].split(','), props)

        if len(keys) > 0:
            reviews = reviews.order_by(*keys)

    return JSONResponse(reviews.to_json())


@bp.route('/beers/<id>/reviews', methods=['POST'])
@login_required
def post(id):
    """Creates a new review for the given beer"""

    try:
        beer = Beer.objects.get(id=id)
    except mongoengine.DoesNotExist:
        return flask.Response('No beer with id {} found'.format(id), 404)
    except:
        return flask.Response('Invalid id {}'.format(id), 400)

    data = flask.request.get_json()

    # check to see if a review was already created for this beer from this
    # user
    try:
        Review.objects.get(beer=beer, user=flask.request.user)
    except mongoengine.DoesNotExist:
        pass
    else:
        return flask.Response('You\'ve already created a review for beer {}'.format(id),
                              400)

    review = Review(beer=beer,
                    user=flask.request.user)

    props = ['aroma', 'appearance', 'taste', 'palate', 'bottle_style']
    for item in props:
        if item in data:
            setattr(review, item, data[item])

    review.calculate()

    try:
        review.save()
    except mongoengine.ValidationError as exp:
        return flask.Response('{}'.format(exp), 400)

    beer.rating = Review.objects.all().filter(beer=beer).average('overall')
    beer.save()

    return JSONResponse(review.to_json())


@bp.route('/beers/<id>/reviews/<rid>', methods=['GET'])
@login_required
def get(id, rid):
    """Returns the given review for the given beer by ids"""

    try:
        beer = Beer.objects.get(id=id)
    except mongoengine.DoesNotExist:
        return flask.Response('Failed to find a beer with id {}'.format(id), 404)
    except:
        return flask.Response('Invalid beer id {}'.format(id), 400)

    try:
        review = Review.objects.get(id=rid, beer=beer)
    except mongoengine.DoesNotExist:
        return flask.Resposne('Failed to find a review with id {}'.format(id), 404)
    except:
        return flask.Response('Invalid review id {}'.format(rid), 400)

    return JSONResponse(review.to_json())


@bp.route('/beers/<id>/reviews/<rid>', methods=['DELETE'])
@login_required
def delete(id, rid):
    """Deletes the given review for the given beer by ids"""

    try:
        beer = Beer.objects.get(id=id)
    except mongoengine.DoesNotExist:
        return flask.Response('No beer with id {} found'.format(id), 404)
    except:
        return flask.Response('Invalid beer id {}'.format(id), 400)

    try:
        review = Review.objects.get(id=rid, beer=beer)
    except mongoengine.DoesNotExist:
        return flask.Response('No review with id {} found'.format(rid), 404)
    except:
        return flask.Response('Invalid review id {}'.format(id), 400)

    review.delete()

    return JSONResponse()


@bp.route('/beers/<id>/reviews/<rid>', methods=['PUT'])
@login_required
def put(id, rid):
    """Updates the given review for a beer by ids"""

    try:
        beer = Beer.objects.get(id=id)
    except mongoengine.DoesNotExist:
        return flask.Response('No beer with id {} found'.format(id), 404)
    except:
        return flask.Resposne('Invalid beer id {}'.format(id), 400)

    try:
        review = Review.objects.get(id=rid, beer=beer)
    except mongoengine.DoesNotExist:
        return flask.Response('No review with id {} found'.format(rid), 404)
    except:
        return flask.Response('Invalid review id {}'.format(id), 400)

    data = flask.request.get_json()

    # update an of our simple fields
    props = ['aroma', 'appearance', 'taste', 'palate', 'bottle_style']
    for item in props:
        if item in data:
            setattr(review, item, data[item])

    review.calculate()

    try:
        review.save()
    except mongoengine.ValidationError as exp:
        return flask.Response('{}'.format(exp), 400)

    beer.rating = Review.objects.all().filter(beer=beer).average('overall')
    beer.save()

    return JSONResponse(review.to_json())


