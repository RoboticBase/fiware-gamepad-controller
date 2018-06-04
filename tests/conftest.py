# -*- coding: utf-8 -*-

import tempfile

import pytest

import yaml
from box import Box

TEST_CONFIG = '''
name: "TEST CONFIG"
controller:
  buttons:
    - key: 0
      value: "triangle"
    - key: 1
      value: "circle"
    - key: 2
      value: "cross"
    - key: 3
      value: "square"
  hats:
    - x: 0
      y: 1
      value: "up"
    - x: 0
      y: -1
      value: "down"
    - x: 1
      y: 0
      value: "right"
    - x: -1
      y: 0
      value: "left"
mqtt:
  host: "mqtt.example.com"
  port: 8883
  topics:
    - key: "controller"
      value: "/demo1/gamepad/attrs"
    '''


@pytest.fixture
def test_config():
    return Box(yaml.load(TEST_CONFIG))


@pytest.fixture
def cafile_path():
    temp = tempfile.NamedTemporaryFile()
    yield temp.name
    temp.close()
