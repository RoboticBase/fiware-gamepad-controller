#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.controller import Controller, ControllerError

def main():
    try:
        controller = Controller()
        controller.describeEvents()
    except ControllerError as e:
        print(f'{str(e)}, cause={str(e.cause)}')

if __name__ == '__main__':
    main()
