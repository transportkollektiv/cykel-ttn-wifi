# cykel-ttn-wifi
A The Things Network adapter for sending bike-tracker positions to [cykel](https://github.com/stadtulm/cykel).
This adapter is for trackers using wifi for location calculations. for GPS based trackers use [cykel-ttn](https://github.com/stadtulm/cykel-ttn). cykel-ttn-wifi uses [mozilla location services](https://location.services.mozilla.com/) for position calculation.

## Prerequisites

* Python (≥3.7)

## Installation

Install the required packages using `pip install -r requirements.txt`. It is recommended to use a virtualenv with your choice of tool, e.g. `pipenv`, in which case you can run `pipenv install` (and `pipenv shell` or prefix `pipenv run` to run commands).

## Decoder
To use the cykel-ttn-wifi adapter you need to bring the incoming bytes from your lora device into a readable format. The TTN Console supports decoders/converters and validators for this use case. You can find the [decoder script in the Tracker Repo](https://github.com/stadtulm/Lora-Wifi-Location-Tracker/blob/master/ttn-decoder-script.js).

Visit `https://console.thethingsnetwork.org/applications/<application-id>/payload-formats` to set the *Payload Format* to *Custom* and enter the decoder function there.

## Configuration

cykel-ttn is configured with environment variables. You may want to create a `.env` file, which you can `source .env` before running cykel-ttn.

The following envionment variables are needed:
```
export TTN_APP_ID="<your ttn application id>"
export TTN_ACCESS_KEY="<your ttn application access key>"
export ENDPOINT="https://<your cykel host>/api/bike/updatelocation"
export ENDPOINT_AUTH_HEADER="Api-Key <your api key for cykel>"
export PORT=8081
export MOZLOC_KEY="<your MLS-API Key from https://location.services.mozilla.com/api>"
```

You can create the *ttn application access key* on the ttn console, the only needed capability is `messages`.

For the cykel API Key (`ENDPOINT_AUTH_HEADER`), visit your cykel administrative interface and create a new API key.

## Run it

(load your virtualenv, if you have one)

`python3 app.py`

## Metrics

On your configured port (env `PORT`) cykel-ttn serves metrics at `/metrics` in the [Prometheus Text-based format](https://prometheus.io/docs/instrumenting/exposition_formats/). You may use this to build monitoring and alerting for your devices.
