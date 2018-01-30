import importlib
import os
import pkgutil

from flask import Blueprint

def find(app):
    """ Finds all of the blueprints and adds them to the given app """

    path = os.path.dirname(os.path.abspath(__file__))

    for _, name, _ in pkgutil.walk_packages([path], prefix='beerpi.'):
        if name == __name__:
            continue

        mod = importlib.import_module(name, __package__)
        for item in dir(mod):
            symbol = getattr(mod, item)

            if isinstance(symbol, Blueprint):
                app.register_blueprint(symbol)

