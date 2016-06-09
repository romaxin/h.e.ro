import os.path
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import uuid
import psutil
import cpuinfo
import time
import json
from threading import Thread
from time import sleep

client = None


def threaded_function():
    while True:
        global client
        if isinstance(client, tornado.websocket.WebSocketHandler):
            #print('pushing data to client')
            loop = tornado.ioloop.IOLoop.instance()
            loop.add_callback(callback=lambda: client.pushStatus())

        sleep(1)


class FaviconHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect('/static/favicon.ico')


class WebHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class WSHandler(tornado.websocket.WebSocketHandler):
    def build_response(self, request_id, payload):
        result = json.dumps({
            'replies_to': request_id,
            'time': float(time.time()),
            'payload': payload})
        return result

    def build_message(self, payload):
        result = json.dumps({
            'message_id': str(uuid.uuid4()),
            'time': float(time.time()),
            'payload': payload})
        return result

    def pushStatus(self):
        cpu_load = psutil.cpu_percent(interval=0, percpu=True)
        network_traffic = psutil.net_io_counters()
        boot_time = psutil.boot_time()

        disk_usage = psutil.disk_usage('/')
        disk_io_counters = psutil.disk_io_counters(perdisk=False)

        payload = {'cpu': {'load': cpu_load},
                   'network': {'traffic': network_traffic},
                   'disk': {'disk_usage': disk_usage,
                            'disk_io_counters': disk_io_counters},
                   'boot_time': boot_time}
        self.write_message(self.build_message(payload))

    def handleInfoCommand(self):
        info = cpuinfo.get_cpu_info()
        response = self.build_message(info)
        self.write_message(response)

    def open(self):
        print('new connection')
        self.set_nodelay(True)
        self.write_message('Hi, client: connection is made ...')
        global client
        client = self

    def on_message(self, message):
        print(('message received: \"%s\"' % message))
        self.write_message('Echo: \"" + message + "\"')
        if (message == "green"):
            self.write_message('green!')

    def on_close(self):
        print('connection closed')
        global client
        client = 0

    def test(self):
        self.write_message('scheduled!')

handlers = [
    (r'/favicon.ico', FaviconHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'}),
    (r'/', WebHandler),
    (r'/ws', WSHandler),
]

settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), 'static'),
)

application = tornado.web.Application(handlers, **settings)


if __name__ == '__main__':

    thread = Thread(target=threaded_function, args=())
    thread.start()

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
