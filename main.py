#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging.config
from logging import getLogger

import yaml

from box import Box

from src.controller import Controller, ControllerError

logger = getLogger(__name__)

def parse():
    parser = argparse.ArgumentParser(description='operate geme controller')
    parser.add_argument('type', type=str, nargs='?', help='controller type',
                        const='pxkwcr', default='pxkwcr', choices=['pxkwcr',])
    parser.add_argument('--describe', action='store_true', default=False, help='describe event id')
    parser.add_argument('--debug', action='store_true', default=False, help='show debug log')
    return parser.parse_args()

def setUpLogging(debug):
    loglevel = 'INFO' if not debug else 'DEBUG'

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s [%(levelname)7s] %(name)s - %(message)s',
                'datefmt': '%Y/%m/%d %H:%M:%S',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
            }
        },
        'loggers': {
            '': {
                'level': loglevel,
                'handlers': ['console'],
            }
        }
    })

def main(args):
    logger.info('run script using %s.yaml', args.type)
    try:
        with open(f'./conf/{args.type}.yaml', 'r') as f:
            conf = Box(yaml.load(f), frozen_box=True)
            controller = Controller(conf)
            if args.describe:
                controller.describeEvents()
            else:
                controller.publishEvents()
    except ControllerError as e:
        logger.exception('%s, %s', e.cause, e)
    except Exception as e:
        logger.exception(e)
    finally:
        logger.info('stop script')

if __name__ == '__main__':
    args = parse()
    setUpLogging(args.debug)
    main(args)
