# -*- coding: utf-8 -*-
import os
import time
import signal

import pygame
from pygame.locals import JOYBUTTONDOWN, JOYBUTTONUP, JOYHATMOTION, JOYAXISMOTION

class ControllerError(Exception):
    def __init__(self, *args, **kwargs):
        self.cause = kwargs.pop('cause') if 'cause' in kwargs else None
        super().__init__(*args, **kwargs)

class Controller:
    def __init__(self):
        try:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.init()
            pygame.display.init()
            pygame.joystick.init()
            controller = pygame.joystick.Joystick(0)
            controller.init()
        except pygame.error as e:
            raise ControllerError('init error', cause=e)

    def describeEvents(self):
        signal.signal(signal.SIGINT, self.stopLoop)
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == JOYBUTTONDOWN:
                        print(f'Button down event, event.button={event.button}')
                    elif event.type == JOYBUTTONUP:
                        print(f'Button up event, event.button={event.button}')
                    elif event.type == JOYHATMOTION:
                        print(f'Hat event, event.hat={event.hat}, event.value={event.value}')
                    elif event.type == JOYAXISMOTION:
                        print(f'Axis event, event.axis={event.axis}, event.value={event.value}')
                time.sleep(0.1)
        except pygame.error as e:
            raise ControllerError('subscribe error', cause=e)

    def stopLoop(self, signal, frame):
        print('stop main loop')
        exit(0)
