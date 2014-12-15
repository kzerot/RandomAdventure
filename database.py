__author__ = 'Max'
import psycopg2
import psycopg2.extensions
from psycopg2.extras import RealDictCursor
import json


class DataBase:
    def __init__(self):
        self.connection_string = "dbname=random host=evillord.ru user=random password=Abatta port=5555"
        self.connection = None

    def connect(self):
        if not self.connection or self.connection.status not in (psycopg2.extensions.STATUS_SETUP,
                                                                 psycopg2.extensions.STATUS_BEGIN):
            self.connection = psycopg2.connect(self.connection_string, cursor_factory=RealDictCursor)

    def check_user(self, login, password):
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute("select id, role from users where name = %s and password = %s", (login, password))
            result = cursor.fetchone()
        finally:
            cursor.close()
        if result and len(result) > 0:
            return [result['id'], result['role']]
        return False

    def get_heroes_for(self, login=None, password=None, user=None):
        if login and password:
            user = self.check_user(login, password)
        self.connect()
        cursor = self.connection.cursor()
        try:
            query = '''select * from heroes h where user_id = %s'''
            cursor.execute(query, (user[0], ))
            result = cursor.fetchall()
        finally:
            cursor.close()
        if result and len(result) > 0:
            return result
        return False

    def get_hero_for(self, hero_id, login=None, password=None, user=None):
        if login and password:
            user = self.check_user(login, password)
        self.connect()
        cursor = self.connection.cursor()
        try:
            query = '''select * from heroes h where user_id = %s and id = %s'''
            cursor.execute(query, (user[0], hero_id))
            result = cursor.fetchone()
        finally:
            cursor.close()
        if result and len(result) > 0:
            return result
        return False

    def save_hero(self, hero):
        self.connect()
        cursor = self.connection.cursor()
        result = False
        try:
            query = '''update heroes set exp = %s, params = %s, bars = %s where id = %s'''
            cursor.execute(query, (hero.exp, json.dumps(hero.params),  json.dumps(hero.bars), hero.id))
            self.connection.commit()
            result = True
        finally:
            cursor.close()
        return result

    def update_hero(self, param_type, hero_id, data):
        self.connect()
        cursor = self.connection.cursor()
        result = False
        try:
            query = '''update  heroes set ''' + param_type + ''' = %s where id = %s'''
            cursor.execute(query, (json.dumps(data), hero_id))
            self.connection.commit()
            result = True
        finally:
            cursor.close()
        return result


db = DataBase()
import atexit


def on_exit():
    if db.connection:
        db.connection.close()


atexit.register(on_exit)