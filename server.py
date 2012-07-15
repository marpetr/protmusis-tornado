import logging
logging.basicConfig(level=logging.INFO)

from frontend import frontend
from backend import backend

import tornado.web
import tornado.httpserver
import tornado.ioloop

if __name__ == '__main__':
    server = tornado.httpserver.HTTPServer(frontend.app)
    server.listen(40404)
    mgmt_server = tornado.httpserver.HTTPServer(backend.app)
    mgmt_server.listen(50505)
    tornado.ioloop.IOLoop.instance().start()
