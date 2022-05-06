import websocket
import time
import json
import socket
from flask import Flask, render_template, make_response

class MaxuxPower_GPIO():
    def __init__(self):
        self.ws = websocket.create_connection("ws://10.242.1.4:8088/", subprotocols=["muxberrypi"])

        initial = self.read()
        self.status = self.initialize(initial)

        self.priorities = [
            {
                'name': 'lights',
                'delay': 0,
                'channels': ['CH3', 'CH4', 'CH5', 'CH6', 'CH7', 'CH10', 'CH13', 'CH14', 'CH15'],
            },
            {
                'name': 'amplifiers',
                'delay': 0,
                'channels': ['CH11', 'CH12', 'CH16'],
            },
            {
                'name': 'screens',
                'delay': 0,
                'channels': ['CH1', 'CH2', 'CH8'],
            },
            {
                'name': 'sound rack',
                'delay': 1000,
                'channels': ['CH9']
            }
        ]

        self.default_preset = ['CH1', 'CH2', 'CH8', 'CH9', 'CH11', 'CH16']

    def __del__(self):
        self.ws.close()

    def initialize(self, initial):
        data = initial['update']['data']['gpio']
        response = {}

        for gpio in data:
            response[gpio['name']] = gpio

        return response

    def msleep(self, ms):
        time.sleep(ms / 1000.0)

    def read(self):
        data = self.ws.recv()
        return json.loads(data)

    def send(self, payload):
        self.ws.send(json.dumps({'module': 'gpio', 'payload': payload}))

    def poweroff(self):
        for priority in self.priorities:
            print("[+] powering off: %s" % priority['name'])

            if priority['delay']:
                print("[+] waiting for delay: %d ms" % priority['delay'])
                self.msleep(priority['delay'])

            for channel in priority['channels']:
                print("[+] powering off: channel: %s" % channel)
                self.send({'request': 'poweroff', 'gpio': self.status[channel]['id']})

    def poweron(self):
        for channel in self.default_preset:
            print("[+] powering up: %s" % channel)
            self.send({'request': 'poweron', 'gpio': self.status[channel]['id']})


"""
class MaxuxPowerOff_Stripes():
    def __init__(self):
        self.ws = websocket.create_connection("ws://10.241.0.40:7681/")
        self.status = self.read()

    def __del__(self):
        self.ws.close()

    def msleep(self, ms):
        time.sleep(ms / 1000.0)

    def read(self):
        data = self.ws.recv()
        return json.loads(data)

    def send(self, color):
        self.ws.send(json.dumps({'target': 'global', 'color': color}))

    def poweroff(self):
        current = {
            'r': self.status['red'],
            'g': self.status['green'],
            'b': self.status['blue']
        }

        for i in range(1, 50):
            current['r'] = int(current['r'] / 1.1)
            current['g'] = int(current['g'] / 1.1)
            current['b'] = int(current['b'] / 1.1)

            print("[+] stripe led: sending: %s" % current)
            self.send(current)
            self.msleep(25)

            if current['r'] == 0 and current['g'] == 0 and current['b'] == 0:
                break
"""

class MaxuxPower_DMX():
    def __init__(self):
        client = self.connect()
        self.status = self.read(client)

    def connect(self):
        dmx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dmx.connect(("10.241.0.106", 47550))

        return dmx

    def msleep(self, ms):
        time.sleep(ms / 1000.0)

    def read(self, client):
        client.send(b"X")
        status = client.recv(512)

        return bytearray(status)

    def poweroff(self):
        for i in range(1, 50):
            for a in range(1, len(self.status)):
                self.status[a] = int(self.status[a] / 1.1)

            client = self.connect()
            client.send(self.status)
            client.close()

            self.msleep(25)

    def poweron(self):
        value = 30

        for i in range(1, 50):
            # for a in range(1, len(self.status)):
            # self.status[a] = int(self.status[a] * 1.1)
            value = value * 1.02
            self.status[3] = int(value)

            client = self.connect()
            client.send(self.status)
            client.close()

            self.msleep(50)



app = Flask(__name__)

@app.route('/powerdown')
def powerdown():
    gpio = MaxuxPower_GPIO()
    gpio.poweroff()

    try:
        a = MaxuxPower_DMX()
        a.poweroff()

    except:
        print("dmx failed")

    r = make_response(render_template('powerdown.html'))
    r.headers.set('Access-Control-Allow-Origin', '*')

    return r

@app.route('/powerup')
def powerup():
    gpio = MaxuxPower_GPIO()
    gpio.poweron()

    try:
        a = MaxuxPower_DMX()
        a.poweron()

    except:
        print("dmx failed")

    r = make_response(render_template('powerup.html'))
    r.headers.set('Access-Control-Allow-Origin', '*')

    return r


@app.route('/')
def home():
    return 'Hello World'

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")

