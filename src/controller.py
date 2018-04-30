# -*- coding: utf-8 -*-
import os
import time
import signal
from logging import getLogger

import pygame
from pygame.locals import JOYBUTTONDOWN, JOYBUTTONUP, JOYHATMOTION, JOYAXISMOTION

import paho.mqtt.client as mqtt

from src.utils import findItem

logger = getLogger(__name__)

TOPIC_KEY = 'controller'

class ControllerError(Exception):
    def __init__(self, *args, **kwargs):
        self.cause = kwargs.pop('cause') if 'cause' in kwargs else None
        super().__init__(*args, **kwargs)

class Controller:
    def __init__(self, conf):
        try:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.init()
            pygame.display.init()
            pygame.joystick.init()
            controller = pygame.joystick.Joystick(0)
            controller.init()
            self.__conf = conf
            self.__client = None
            logger.info('initialized %s', conf.name)
        except pygame.error as e:
            raise ControllerError('init error', cause=e)

    @property
    def client(self):
        if self.__client is None:
            def __on_connect(client, userdata, flags, response_code):
                logger.info('connected mqtt broker[%s:%d], response_code=%d',
                            self.__conf.mqtt.host, self.__conf.mqtt.port, response_code)
            def __on_disconnect(client, userdata, response_code):
                logger.info('disconnected mqtt broker, response_code=%d', response_code)

            self.__client = mqtt.Client(protocol=mqtt.MQTTv311)
            self.__client.on_connect = __on_connect
            self.__client.on_disconnect = __on_disconnect

            self.__client.connect(self.__conf.mqtt.host, port=self.__conf.mqtt.port, keepalive=60)
            self.__client.loop_start()
        return self.__client

    def describeEvents(self):
        logger.info('start describing...')
        def callback(event):
            if event.type == JOYBUTTONDOWN:
                logger.info('Button down event, event.button=%s', event.button)
            elif event.type == JOYBUTTONUP:
                logger.info('Button up event, event.button=%s', event.button)
            elif event.type == JOYHATMOTION:
                logger.info('Hat event, event.hat=%s, event.value=%s', event.hat, event.value)
            elif event.type == JOYAXISMOTION:
                logger.info('Axis event, event.axis=%s, event.value=%s', event.axis, event.value)
        self.__subscribeEvent(callback)

    def publishEvents(self):
        logger.info('start publishing...')
        def callback(event):
            if event.type == JOYBUTTONDOWN:
                item = findItem(self.__conf.controller.buttons, lambda item: item.key == event.button)
                if item:
                    self.__publish_mqtt(item.value)
            elif event.type == JOYHATMOTION:
                item = findItem(self.__conf.controller.hats,
                                lambda item: item.x == event.value[0] and item.y == event.value[1])
                if item:
                    self.__publish_mqtt(item.value)
            else:
                logger.debug('ignore event, %s', event)
        self.__subscribeEvent(callback)

    def __publish_mqtt(self, payload):
        topic = findItem(self.__conf.mqtt.topics, lambda item: item.key == TOPIC_KEY)
        if topic:
            self.client.publish(topic.value, payload)
            logger.info('published "%s" to "%s"', payload, topic.value)
        else:
            logger.warning('no topic found, key=%s', TOPIC_KEY)

    def __subscribeEvent(self, callback):
        signal.signal(signal.SIGINT, self.__stopLoop)
        try:
            while True:
                for event in pygame.event.get():
                    callback(event)
                time.sleep(0.1)
        except pygame.error as e:
            raise ControllerError('subscribe event error', cause=e)

    def __stopLoop(self, signal, frame):
        if self.__client is not None:
            self.__client.loop_stop()
            self.__client.disconnect()

        logger.info('stop main loop')
        exit(0)
