#!/bin/python
import requests
import json
import os
import logging
import yaml

from opentelemetry.metrics import get_meter
from opentelemetry.propagate import extract
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.trace import (
    SpanKind,
    get_tracer_provider,
    set_tracer_provider,
)

set_tracer_provider(TracerProvider())
tracer = get_tracer_provider().get_tracer(__name__)

get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

otel_meter = get_meter("ttn2otel")

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

import paho.mqtt.client as MqttClient

# Load the configuration
cfg = {}
try:
    with open("config.yaml", "r") as cfgfile:
        cfg = yaml.load(cfgfile, Loader=yaml.Loader)
except:
    logger.warning("No configuration file found, proceeding with environment variables")

# Setup the MQTT Client
mclient = MqttClient.Client(MqttClient.CallbackAPIVersion.VERSION2, "ttn2otel")

ttn_mqtt_user = cfg['ttn']['mqtt_user']
ttn_mqtt_pass = cfg['ttn']['mqtt_pass']
ttn_mqtt_host,ttn_mqtt_port = cfg['ttn']['mqtt_host'].split(":")
ttn_mqtt_tls = cfg['ttn']['mqtt_tls']

lookup_enabled = False

if "lookups" in cfg:
    lookup_enabled = cfg['lookups']['enabled']

# Config TLS Support if necessary
if ttn_mqtt_tls == True:
    mclient.tls_set()

# Set the credentials
mclient.username_pw_set(ttn_mqtt_user, ttn_mqtt_pass)

# Define our message callback
def on_message(client, userdata, message):
    with tracer.start_as_current_span("process_ttn_payload",
                                      kind=SpanKind.CONSUMER):
        msg = json.loads(message.payload.decode("utf-8"))
        logger.info(f"Message received on {message.topic}")
        try:
            logger.debug(f"Message payload was: {msg['uplink_message']['decoded_payload']}")
            payload = msg["uplink_message"]["decoded_payload"]
            with tracer.start_as_current_span("add_metrics_to_gauge"):
                for metric in payload:
                    metric_gauge = otel_meter.create_gauge(f"{metric}", description=f"{metric}")
                    if type(payload[metric]) is not list and metric != "port" and metric != "timesync_seqno":
                        metric_value = payload[metric]
                        labels = {
                                "ttn.device.name": msg["end_device_ids"]["device_id"],
                                "ttn.application.name": msg["end_device_ids"]["application_ids"]["application_id"]
                                }
                        if lookup_enabled:
                            with tracer.start_as_current_span("lookup_device_details",
                                                              kind=SpanKind.CLIENT):
                                device_details = requests.get(f"{cfg['lookups']['server']}/devices/{msg['end_device_ids']['device_id']}/")
                                logger.debug(f"Device Details: {device_details.text}")
                                lat,lng = device_details.json()['geolocation'].split(',')
                                labels['latitude'] = lat
                                labels['longitude'] = lng
                        with tracer.start_as_current_span("set_gauge_value"):
                            metric_gauge.set(metric_value, labels)
                    else:
                        logger.warning(f"Type was a list or matched a discarded metric, skipping {metric}")
        except:
            logger.warning(f"Issue decoding fields from {msg}")




def on_connect(client, userdata, flags, rc, properties=None):
    with tracer.start_as_current_span("connect_to_mqtt"):
        if rc==0:
            logger.info(f"Connected OK Returned code={rc}")
        else:
            if rc==1: 
                logger.error("Connection refused – incorrect protocol version")
            elif rc==2: 
                logger.error("Connection refused – invalid client identifier")
            elif rc==3: 
                logger.error("Connection refused – server unavailable")
            elif rc==4: 
                logger.error("Connection refused – bad username or password")
            elif rc==5:
                logger.error("Connection refused – not authorised")
            else:
                logger.error(f"Connection refused - Error code {rc} is an unknown error")

for metric in cfg['metrics']:
    pass
     

logger.info(f"Connecting to {ttn_mqtt_host} as {ttn_mqtt_user}")


mclient.on_message = on_message
mclient.on_connect = on_connect
mclient.connect(ttn_mqtt_host, port=int(ttn_mqtt_port))
mclient.subscribe('#')

mclient.loop_forever()
