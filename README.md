# TTN2OTEL

Translate payloads from [The Things Network](https://www.thethingsnetwork.org/) to an [OpenTelemetry](https://opentelemetry.io/) endpoint.

## Usage

Create a configuration file with the following content:

```yaml
ttn:
    mqtt_user: <your TTN MQTT Username>
    mqtt_pass: <your TTN MQTT Password>
    mqtt_server: <your MQTT Server>
metrics:
    - ttn_name: <TTN Payload Field>
      metric_name: <your custom metric name>
    - ttn_name: <TTN Payload Field>
      metric_name: <your custom metric name>
    - ttn_name: <TTN Payload Field>
      metric_name: <your custom metric name>
```

### Docker


