__author__ = 'Max'
import tornado

class HeroEntry(tornado.web.UIModule):
    def render(self, hero):
        return self.render_string(
            "hero.html", hero=hero)
