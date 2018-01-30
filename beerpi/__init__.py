# vi:et:ts=4 sw=4 sts=4

"""This is the beerapi package"""

from flask import Flask
from flask_mongoengine import MongoEngine

from beerpi import blueprints


app = Flask(__package__, instance_relative_config=True)

app.config.from_object('beerpi.settings')
#app.config.from_pyfile('settings.cfg')

db = MongoEngine(app)

blueprints.find(app)

