"""This module contains a helper for getting the sorting arguements figured
out"""


def get_sort_keys(given, allowed):
    """Check the list of given values and coerce them into the sort keys for mongo"""

    keys = []

    for key in given:
        asc = True

        if key[0] == ' ' or key[0] == '+':
            asc = True
            key = key[1:]

        if key[0] == '-':
            asc = False
            key = key[1:]

        if key in allowed:
            keys.append('{}{}'.format(asc and '+' or '-', key))

    return keys

