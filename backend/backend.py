# coding: utf-8

import tornado.web

import os
import redis as pyredis

redis = pyredis.Redis()

class AuthBaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('authuser')

class FrontPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('<a href="/dashboard">Dashboard</a>')

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('<form action="/login" method="post">'
                '<input type="password" name="password" />'
                '</form>')
    def post(self):
        if self.get_argument('password', '') == redis.get('global:adminkey'):
            self.set_secure_cookie('authuser', 'admin')
            self.redirect('/')
        else:
            self.redirect('/login')

class DashboardHandler(AuthBaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('templates/dashboard.html')

class DashboardStatusFragmentHandler(AuthBaseHandler):
    @tornado.web.authenticated
    def get(self):
        class Team(object):
            def __init__(self, id):
                self.id = id
        teams = [Team(id) for id in range(1, 17)]
        question_ids = redis.lrange('questions', 0, -1)
        questions = []
        for qid in question_ids:
            questions.append(dict(
                id = qid,
                text = redis.get('question:%s:text' % qid),
                image_path = redis.get('question:%s:image_path' % qid),
                solution = redis.get('question:%s:solution' % qid),
            ))
        self.render('templates/dashboard-status.html', teams=teams,
                questions=questions)

settings = dict(
    debug = True,
    static_path = os.path.join(os.path.dirname(__file__), 'static'),
    cookie_secret = 'cyiumovfjflewjfmwu8cm8l3ua29mvr0bmtvsnfdksai2iv0a9nvyf',
    login_url = '/login',
)

app = tornado.web.Application([
       (r'/', FrontPageHandler),
       (r'/login', LoginHandler),
       (r'/dashboard', DashboardHandler),
       (r'/dashboard/status', DashboardStatusFragmentHandler),
], **settings)

