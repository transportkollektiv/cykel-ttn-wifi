import atexit
import json
import os
import sys
import time

import paho.mqtt.client as mqtt
import requests
from prometheus_client import Gauge, start_http_server

MOZ_GEOLOCATION_URL = "https://location.services.mozilla.com/v1/geolocate"

ttn_host = os.environ["TTN_HOST"]
ttn_username = os.environ["TTN_USERNAME"]
ttn_api_key = os.environ["TTN_API_KEY"]

endpoint = os.environ["ENDPOINT"]
auth_header = os.getenv("ENDPOINT_AUTH_HEADER", "")
port = int(os.getenv("PORT", 8080))
host = os.getenv("HOST", "")

moz_geolocation_key = os.getenv("MOZLOC_KEY", "test")


voltgauge = Gauge("tracker_battery_volts", "bike battery voltage", ["device_id"])
timegauge = Gauge("tracker_last_data_update", "bike last data timestamp", ["device_id"])
packgauge = Gauge("ttn_last_package_received", "last ttn package received timestamp")

headers = {}
if auth_header != "":
    headers = {"Authorization": auth_header}


def uplink_callback(msg):
    try:
        dev_id = msg["end_device_ids"]["device_id"]
        print("Received uplink from %s" % (dev_id))
        print(msg)
        data = msg["uplink_message"]["decoded_payload"]
        print(data)
        mr = requests.post(
            "%s?key=%s" % (MOZ_GEOLOCATION_URL, moz_geolocation_key), data=data
        )

        update = {"device_id": dev_id}
        if mr.status_code == 200:
            locationdata = mr.json()
            update = {
                "device_id": dev_id,
                "lat": locationdata["location"]["lat"],
                "lng": locationdata["location"]["lng"],
                "accuracy": locationdata["accuracy"],
            }
            print(locationdata)

        if "voltage" in data:
            update["battery_voltage"] = data["voltage"]

        resp = requests.post(endpoint, headers=headers, data=update)
        print(resp)
        if "voltage" in data:
            voltgauge.labels(device_id=dev_id).set(data["voltage"])
        timegauge.labels(device_id=dev_id).set(int(time.time()))
        packgauge.set(int(time.time()))
    except Exception as e:
        print(e)


def on_connect(client, userdata, flags, rc):
    if rc > 0:
        print("connection to ttn mqtt failed")
        client.close()
        sys.exit(1)

    print("connected to ttn")
    client.subscribe(f"v3/{ttn_username}/devices/+/up")


def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode("utf-8"))
    uplink_callback(data)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(ttn_username, ttn_api_key)
# client.tls_set(ca_certs=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)

ttn_hostname, ttn_port = ttn_host.split(":")


def close_mqtt():
    # client.loop_stop()
    client.disconnect()


atexit.register(close_mqtt)

print("starting cykel-ttn-wifi")
client.connect(ttn_hostname, port=int(ttn_port), keepalive=60)
start_http_server(port, addr=host)
print("serving metrics on %s:%s" % (host, port))

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("exiting")
    sys.exit(0)
