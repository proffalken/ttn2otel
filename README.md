# TTN2OTEL

Translate payloads from [The Things Network](https://www.thethingsnetwork.org/) to an [OpenTelemetry](https://opentelemetry.io/) endpoint.

## Usage

Create a configuration file with the following content:

```yaml
ttn:
  mqtt_user: <your TTN MQTT Username>
  mqtt_pass: <your TTN MQTT Password>
  mqtt_server: <your MQTT Server>
  mqtt_tls: True
lookups:
  enabled: True
  server: https://<your device api server>
```

### Lookups

The data lookup functionality allows you to retrieve more information about the device via a remote API.

Initially we only support the lookup of static lat/long coordinates via the [Make Monmouth Sensor Management Portal](https://github.com/MakeMonmouth/SensorManagement) as part of our Air Quality Sensor network, allowing us to update the location of the sensor on a map without needing the additional cost of a GPS module in the sensor itself.

Pull Requests to improve this part of the code are welcome!

### Run the code

Make sure you have an Open Telemetry endpoint available, then run the following:

```bash
poetry run opentelemetry-instrument \
  --traces_exporter console,otlp \
  --metrics_exporter console,otlp \
  --logs_exporter console,otlp \
  --service_name ttn2otel \
  --exporter_otlp_endpoint http://127.0.0.1:4318 \
  --exporter_otlp_protocol http/protobuf \ 
  python src/ttn2otel.py
```
