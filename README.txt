##### About #####

Beer Manager API.

It is written in Python3.6 using Python FrameWork Flask and mongodb.
It runs in a standalone WSGI container and providers only a REST interface.  It only supports `application/json` as a content-type.

##### Dependencies #####

BeerPI depends on the following packages.  The versions are what it was developed against, but may run with others.

 * flask (0.10.1)
 * flask-mongoengine (0.7.0)
 * python-dateutil (2.2)
 * tornado (3.2)

###### Installation #####

create Virtual Environment (virtualenv) and activate it in python3.6.

    . python3.6/bin/activate

After that, you can run the server with the following command:

    python wsgi.py

Once the application is running, open a browser or an API testing tool like Postman and
    go to the `/once` URL.  This will create a user with the username `admin` and a password of `admin` if it does not exist.
    This user should be used to setup other users and it's password should be changed immediately.


###### Endpoints #####

## Sorting

The following is an example URL of sorting the user list by username

    /users/?sort=+username

The following is an example URL of sorting breweries by state, city, and then name

    /breweries/?sort=state,city,name

The following is an example of sorting beers by rating descending and then name ascending

    /beers/?sort=-rating,+name

# Users Endpoints

The /users endpoint is used to manage the collection of users.  There are no
privileges in BeerPI, anyone can create a user.

## /users `GET`

This endpoint has no input and returns `application/json` which is a list of dictionaries for each user.  These dictionaries contain  the following fields:

 * id - The mongodb ObjectId 
 * username - The username of the user which must be unique
 * email - The email address of the user
 * last_beer_added - The last time the user added a beer

This endpoint supports the following sorting fields

 * username
 * email

This endpoint will always return an HTTP 200.

## /users `POST`

This endpoint creates a new user.  It expects a body of `application/json` containing the following fields with all others ignored.

 * username - `required` The username to give to the new user which must be unique. `string`
 * email - The email address to give to the new user `email address`
 * password - `required` The clear-text password to give to the new user.  This will be hashed with sha256 before storage, but since the server has the clear-text version, it should not be considered a secure password store. `string`

If a username and password are not provided a 400 is returned.

If a user with the given username already exists a 409 is returned.

If the user is created successfully a 200 is returned.

## /users/<id> `GET`

This endpoint has no input and returns `application/json` which is a dictionary for the given user `<id>`.  This dictionary contains the following fields:

 * id - The mongodb ObjectId 
 * username - The username of the user which must be unique
 * email - The email address of the user
 * last_beer_added - The last time the user added a beer

If the there is no user with `<id>` a 404 is returned.

If `<id>` is not a valid mongo ObjectId a 400 is returned.

If the user is found, the above mentioned dictionary is returned with a 200 status code.

## /users/<id> `PUT`

This endpoint updates the specified user.  It expects an a body of `application/json` which is a dictionary of values to update.  This dictionary may contain any of the following fields:

 * email `string`
 * password `string`

If there is no user with `<id>` a 404 is returned.

if `<id>` is not a valid mongo ObjectId a 400 is returned.

if the user is found, it is updated with the passed in values.  The updated version of the user will be output with a status code of 200.

## /users/<id> `DELETE`

This endpoint deletes the specified user.  It takes no parameters.

If there is no use r with `<id>` a 404 is returned.

if `<id>` is not a valid mongo ObjectId a 400 is returned.

if the user exists, it is deleted and a status code of 200 is returned.

## /users/<id>/favorites `GET`

This endpoint returns a list of the given user's favorite beers.  It has no inputs and returns `application/json` of a list of dictionaries.  The dictionaries contain the following fields.

 * beer - The id of the beer `ObjectId`
 * user - The id of the user `ObjectId`

This endpoint does not support sorting.

If the given users does not exist, a 404 is returned.

If `<id>` is not a valid mongo ObjectId a 400 is returned.

If the users exists, a 200 will be returned.

## /users/<id>/favorites `POST`

This endpoint adds a new favorite for the given user.  Calls to this endpoint are only allowed if `<id>` matches the logged in user's id.

This endpoint expects `appilcation/json` for a dictionary with the following fields.

 * beer - `required` the ObjectId of the beer

If `<id>` does not match the id of the calling user, a 400 is returned.

If the beer field is not supplied, a 400 is returned.

If the beer field is supplied but does not point to a valid beer, a 404 is returned.

If the beer field is not a valid mongo ObjectId a 400 is returned.

If the user has already favorited this beer, a 400 is returned.

Finally, if none of the above conditions are met, the favorite is added and returned with a status code of 200.

## /users/<id>/favorites/<fid> `GET`

This endpoint returns a specific favorite for the given user.

This endpoint returns a dictionary with the following fields:

 * beer
 * user

If `<id>` is not a valid user id, a 400 is returned.

If `<id>` is not a user id, a 404 is return.

if `<fid>' is not a valid favorite id, a 400 is returned.

if `<fid>` is not a favorite id, a 404 is returned.

Otherwise, the favorite is returned with a status code of 200.

## /users/<id>/favorites/<fid> `DELETE`

This endpoint removes a favorite for the currently logged in user.

If this endpoint is called by a user who's id does not match `<id>` a 400 is returned.

if `<fid>` is not a valid favorite id, a 400 is returned.

if `<fid>` is not a favorite id, a 404 is returned.

Otherwise, the favorite is deleted and a 200 is returned.

## /users/<id>/favorites/<fid> `PUT`

This endpoint updates a favorite for the currently logged in user.

If this endpoint is called by a user who's id does not match `<id>` a 400 is returned.

It expects `application/json` with a field named `beer`.

If `<fid>` is not a valid mongo ObjectId a 400 is returned.

If `<fid>` is not a valid favorite id a 404 is returned.

Otherwise the favorite is updated and a 200 is returned.



Similarly, Implemented for following endpoints

##### Beer Endpoints #####
##### Brewery Endpoints #####
##### Glasses Endpoints #####
