"""This is the WSGI runner for the application"""


from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from beerpi import app


def main():
    server = HTTPServer(WSGIContainer(app))
    server.listen(8080)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
