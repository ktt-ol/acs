#!/usr/bin/env python3
import configparser
import sys

import paho.mqtt.client as mqtt
import sdnotify


class GlassDoorController:

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        sys.stdout.flush()

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected with result code " + str(rc))
        sys.stdout.flush()
        sys.exit(1)

    def on_state_message(self, client, userdata, message):
        state = str(message.payload.decode("utf-8"))
        self.state = state
        print("received state:", state)
        sys.stdout.flush()

        if state == "none":
            client.publish("/access-control-system/glass-door/RGBLED", payload="ff0000 Z")
        elif state == "keyholder":
            client.publish("/access-control-system/glass-door/RGBLED", payload="ff00ff Z")
        elif state == "member":
            client.publish("/access-control-system/glass-door/RGBLED", payload="ffff00 Z")
        elif state == "open":
            client.publish("/access-control-system/glass-door/RGBLED", payload="00ff00 Z")
        elif state == "open+":
            client.publish("/access-control-system/glass-door/RGBLED", payload="00ff40 -1000 00ffff -1000 00ff40 0")
        else:
            client.publish("/access-control-system/glass-door/RGBLED", payload="0000ff Z")

    def on_reed_message(self, client, userdata, message):
        reed_state = int(str(message.payload.decode("utf-8")))
        print("received reed state:", reed_state)
        sys.stdout.flush()

    def on_bolt_message(self, client, userdata, message):
        bolt_state = int(str(message.payload.decode("utf-8")))
        print("received bolt state:", bolt_state)
        sys.stdout.flush()

    def on_bell_message(self, client, userdata, message):
        bell_state = int(str(message.payload.decode("utf-8")))
        print("received bell state:", bell_state)
        sys.stdout.flush()

        if self.state not in ("none", "keyholder") and bell_state == 1:
            print("=> open door buzzer")
            sys.stdout.flush()
            client.publish("/access-control-system/glass-door/buzzer", payload="3000")  # ms

    def on_message(self, client, userdata, message):
        if message.topic == "/access-control-system/space-state":
            self.on_state_message(client, userdata, message)
        elif message.topic == "/access-control-system/glass-door/bolt-contact":
            self.on_bolt_message(client, userdata, message)
        elif message.topic == "/access-control-system/glass-door/reed-switch":
            self.on_reed_message(client, userdata, message)
        elif message.topic == "/access-control-system/glass-door/bell-button":
            self.on_bell_message(client, userdata, message)
        else:
            print("Unhandled message topic")
            sys.stdout.flush()

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("settings.conf")

        mqttauth = config["mqttauth"]

        self.state = "unknown"
        self.client = mqtt.Client(mqttauth["clientid"])
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_connect = self.on_connect
        self.client.tls_set(mqttauth["certfile"])
        self.client.tls_insecure_set(False)
        self.client.username_pw_set(mqttauth["username"], mqttauth["password"])
        self.client.connect(host=mqttauth["server"], port=int(mqttauth["port"]), keepalive=60)

        self.client.subscribe("/access-control-system/space-state")
        self.client.subscribe("/access-control-system/glass-door/bolt-contact")
        self.client.subscribe("/access-control-system/glass-door/reed-switch")
        self.client.subscribe("/access-control-system/glass-door/bell-button")

    def loop(self):
        return self.client.loop()


systemdnotifier = sdnotify.SystemdNotifier()
ctrl = GlassDoorController()
systemdnotifier.notify("READY=1")

while True:
    systemdnotifier.notify("WATCHDOG=1")
    ctrl.loop()
