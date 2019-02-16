# fiware-gamepad-controller
This python application subscribes for gamepad events, and publishes a command corresponding to the received event to MQTT.

[![TravisCI Status](https://travis-ci.org/RoboticBase/fiware-gamepad-controller.svg?branch=master)](https://travis-ci.org/RoboticBase/fiware-gamepad-controller)

## Description
This python application works on Raspberry Pi 2 or higher.

This applicaton subscribes for gamepad events using [pygame](https://www.pygame.org/docs/). When a gamepad event is received and a command is associated with the event, this application publishes the command to MQTT Broker.

## Requirement

**python 3.6 or higher**

## Install libraries

```bash
$ git clone https://github.com/RoboticBase/fiware-gamepad-controller.git
$ cd fiware-gamepad-controller
$ pip install -r requirements/common.txt
```

## How to Run

```bash
$ python ./main.py [-h] [--describe] [--debug] [type]
```

|option|description|
|:--|:--|
|-h, --help|show help message|
|--describe|show the event of gamepad instead of publishing a command to MQTT|
|--debug|show debug log|
|type|give the configuration type|

When `abc` is given as [type], `conf/abc.yaml` is loaded as the configuration of this application.

## License

[Apache License 2.0](/LICENSE)

## Copyright
Copyright (c) 2018 TIS Inc.
