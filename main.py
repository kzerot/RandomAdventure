import tornado
import psycopg2

import tornado.ioloop
import tornado.web
from consts import *
from database import *
import uimodules
from hero import *


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = self.get_secure_cookie("user", None)
        password = self.get_secure_cookie("password", None)
        if user and password :
            result = db.check_user(user.decode('utf-8'), password.decode('utf-8'))
            if result:
                return user.decode('utf-8')
        return None

    def get_user_credit(self):
        user = self.get_secure_cookie("user", None)
        password = self.get_secure_cookie("password", None)
        if user and password:
            return user.decode('utf-8'), password.decode('utf-8')
        return None

    def get_user_data(self):
        login, password = self.get_user_credit()
        result = db.check_user(login, password)
        if result:
            return result
        return None, None


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        #name = tornado.escape.xhtml_escape(self.current_user)
        heroentries = [Hero(h) for h in db.get_heroes_for(user=self.get_user_data())]
        self.render("heroes.html", heroes=heroentries)


class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        if db.check_user(self.get_argument("name"), self.get_argument("password")):
            self.set_secure_cookie("user", self.get_argument("name"))
            self.set_secure_cookie("password", self.get_argument("password"))
        self.redirect("/")


class JsonHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        pass

    @tornado.web.authenticated
    def post(self):
        """
        Types of data:
        Refresh hero: {'action': 'refresh', 'hero':hero_id} -> {'hero': hero_id, 'data': hero_data}
        Refresh heroes: {'action': 'refresh'} -> [{'hero': hero_id, 'data': hero_data},...]
        Update characteristic: {'action': 'update', 'hero': hero_id, 'type': param|bars|inventory,
                                'name':'str', 'delta': -1} ->
                               {'hero': hero_id, 'data': hero_data}
        """
        result = {}
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        if data and 'action' in data:
            if data['action'] == 'refresh':
                heroes = db.get_heroes_for(user=self.get_user_data())
                heroes = [Hero(h).json() for h in heroes]
                result = {'data': heroes}
            elif data['action'] == 'update':
                hero = db.get_hero_for(data['hero'], user=self.get_user_data())
                hero = Hero(hero)
                dictionary = hero.increase_param(data['type'], data['name'], data['delta'])
                db.update_hero(data['type'], hero.id, dictionary)
                result = {'data': [hero.json()]}
            elif data['action'] == 'level_up':
                hero = db.get_hero_for(data['hero'], user=self.get_user_data())
                hero = Hero(hero)
                for p in data['data']:
                    hero.increase_param(data['type'], p, data['data'][p])
                    hero.exp -= hero.params[p]['cost']
                db.save_hero(hero)
                result = {'data': [hero.json()]}
                print('Return hero:')
                print(hero.json())
        self.set_header("Content-Type", "application/json")
        self.write(result)

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    (r"/json", JsonHandler),
], cookie_secret="h54r57jdlkkl;kl;ddsdfy5t677667iy7mmjg",
template_path='template',
static_path='static',
login_url="/login",
ui_modules=uimodules,
debug=True,)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()