import tornado.ioloop
import tornado.web
from Model.nnmodel import Vocabulary
from Model.PretrainedModel import img2words
import os
import time
import json

m = img2words()
#m = 0

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        with open('templates/test.html','r',encoding='UTF-8') as html:
            self.write(html.read())

class ApiHandler(tornado.web.RequestHandler):
    def post(self):
        ret = {'result': 'OK'}
        base64str = ""
        try:
            base64str = self.get_argument("imgbase64")
        except:
            ret['result'] = "NO"
        if base64str != "":
            ret['sentence'], ret['sentence_ch'] = m.get_sentence(base64str)
        self.write(json.dumps(ret, ensure_ascii=False))
    def get(self):
        self.write("<h1>不提供Get方法</h1>")


settings = dict(
        template_path = os.path.join(os.path.dirname(__file__),"templates"),
        static_path = os.path.join(os.path.dirname(__file__), "static"),
        #debug = True
    )

class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('test ok')

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/api", ApiHandler),
        (r"/test", TestHandler),
    ],
    **settings
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(80)
    print('server start')
    tornado.ioloop.IOLoop.current().start()
    
 
