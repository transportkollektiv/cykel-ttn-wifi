import time
import ttn
import sys
import atexit
import requests
import os
import json

from prometheus_client import Gauge, start_http_server

MOZ_GEOLOCATION_URL = 'https://location.services.mozilla.com/v1/geolocate'

app_id = os.environ['TTN_APP_ID']
access_key = os.environ['TTN_ACCESS_KEY']
endpoint = os.environ['ENDPOINT']
auth_header = os.getenv('ENDPOINT_AUTH_HEADER', '')
port = int(os.getenv('PORT', 8080))
host = os.getenv('HOST', '')

moz_geolocation_key = os.getenv('MOZLOC_KEY', 'test')


voltgauge = Gauge('tracker_battery_volts', 'bike battery voltage', ['device_id'])
timegauge = Gauge('tracker_last_data_update', 'bike last data timestamp', ['device_id'])
packgauge = Gauge('ttn_last_package_received', 'last ttn package received timestamp')

headers = {}
if auth_header != '':
	headers = {
		'Authorization': auth_header
	}

def uplink_callback(msg, client):
	try:
		print("Received uplink from ", msg.dev_id)
		print(msg)
		data = msg.payload_fields.data
		#js = json.dumps(data)
		print(data)
		mr = requests.post('%s?key=%s' % (MOZ_GEOLOCATION_URL, moz_geolocation_key), data=data)
		if mr.status_code != 200:
			# mr.json().error.message
			print(mr)
			print(mr.json())
			return
		data = mr.json()
		print(data)
		update = {
			'device_id': msg.dev_id,
			'lat': data['location']['lat'],
			'lng': data['location']['lng'],
			'accuracy': data['accuracy']
		}
		if hasattr(msg.payload_fields, 'voltage'):
			update['battery_voltage'] = msg.payload_fields.voltage

		resp = requests.post(endpoint, headers=headers, data=update)
		print(resp)
		if hasattr(msg.payload_fields, 'voltage'):
			voltgauge.labels(device_id=msg.dev_id).set(msg.payload_fields.voltage)
		timegauge.labels(device_id=msg.dev_id).set(int(time.time()))
		packgauge.set(int(time.time()))
	except e:
		print(e)

def connect_callback(res, client):
	if not res:
		print('connection to ttn mqtt failed')
		client.close()
		sys.exit(1)
	else:
		print('connected to ttn')

handler = ttn.HandlerClient(app_id, access_key)
mqtt_client = handler.data()

def close_mqtt():
	mqtt_client.close()

atexit.register(close_mqtt)

mqtt_client.set_connect_callback(connect_callback)
mqtt_client.set_uplink_callback(uplink_callback)

print('starting cykel-ttn-wifi')
mqtt_client.connect()
start_http_server(port, addr=host)
print('serving metrics on %s:%s' % (host, port))

try:
	while 1:
		time.sleep(1)
except KeyboardInterrupt:
	print('exiting')
	sys.exit(0)
