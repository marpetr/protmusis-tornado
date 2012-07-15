# coding: utf-8

import tornado.web

import os
import redis as pyredis

redis = pyredis.Redis()

class AuthBaseHandler(tornado.web.RequestHandler):
    def get_current_team(self):
        return int(self.get_secure_cookie('team_id') or 0) or None
    current_team = property(get_current_team)

    def get_current_user(self):
        return self.current_team

class FrontPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect('/main')

class TeamViewHandler(AuthBaseHandler):
    @tornado.web.authenticated
    def get(self):
        class Team(object): pass
        team = Team()
        team.name = 'test team, number %d' % self.current_team
        self.render('templates/main.html', team=team)

class SyncHandler(AuthBaseHandler):
    @tornado.web.authenticated
    def post(self):
        user_id = 123
        qid = self.get_argument('currentQID', None)
        if qid:
            qid = int(qid)
            new_answer = self.get_argument('currentText', '')
            redis.set('answer:%d:%d' % (user_id, qid), new_answer)

        view = redis.get('global:view') or 'idle'
        resp = dict(view=view)
        if view == 'question':  # dummy data
            qid = int(redis.get('global:qid') or 1)
            resp.update(dict(
                qid=qid,
                cur_answer=redis.get('answer:%d:%d' % (user_id, qid)) or '',
                num=qid,
                time_left=42,
            ))
        self.write(resp)

class RegisterTeamHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/login.html')
    def post(self):
        team_id = int(self.get_argument('team_id'))
        pin = self.get_argument('pin', '')
        if redis.get('team:%d:pin' % team_id) == pin:
            self.set_secure_cookie('team_id', unicode(team_id))
            self.redirect('/main')
        else:
            self.redirect('/login?wrong_pin=true')
    def get_available_teams(self):
        class TeamRecord(object):
            def __init__(self, id):
                self.id = id

        return [TeamRecord(id) for id in range(1, 17)]

class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie('team_id')
        self.redirect('/login')

settings = dict(
    debug = True,
    static_path = os.path.join(os.path.dirname(__file__), 'static-fe'),
    cookie_secret = 'cyiumovq;vmeinfy843v7l32m9dlvny8s8laduvnu3l0ai2iv0a9nvyf',
    login_url = '/login',
)

frontend = tornado.web.Application([
       (r'/', FrontPageHandler),
       (r'/main', TeamViewHandler),
       (r'/sync', SyncHandler),
       (r'/login', RegisterTeamHandler),
       (r'/logout', LogoutHandler),
], **settings)

