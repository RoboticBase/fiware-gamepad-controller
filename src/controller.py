# -*- coding: utf-8 -*-
import os
import time
import signal
from logging import getLogger

import pygame
from pygame.locals import JOYBUTTONDOWN, JOYBUTTONUP, JOYHATMOTION, JOYAXISMOTION

from src.utils import findItem

logger = getLogger(__name__)

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
            self.conf = conf
            logger.info('initialized %s', conf.name)
        except pygame.error as e:
            raise ControllerError('init error', cause=e)

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
                item = findItem(self.conf.controller.buttons, lambda item: item.key == event.button)
                if item:
                    logger.info('published %s', item.value)
            elif event.type == JOYHATMOTION:
                item = findItem(self.conf.controller.hats,
                                lambda item: item.x == event.value[0] and item.y == event.value[1])
                if item:
                    logger.info('published %s', item.value)
            else:
                logger.debug('ignore event, %s', event)
        self.__subscribeEvent(callback)

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
        logger.info('stop main loop')
        exit(0)
