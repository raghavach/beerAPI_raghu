from flask import Response

def JSONResponse(data=None):
    return Response(data, 200, {'content-type': 'application/json'})


