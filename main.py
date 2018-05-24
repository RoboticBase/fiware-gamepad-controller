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
                        const='pxkwcr-azure', default='pxkwcr-azure', choices=['pxkwcr-azure', 'pxkwcr-minikube',])
    parser.add_argument('--describe', action='store_true', default=False, help='describe event id')
    parser.add_argument('--debug', action='store_true', default=False, help='show debug log')
    return parser.parse_args()

def setup_logging(debug):
    log_level = 'INFO' if not debug else 'DEBUG'

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
                'level': log_level,
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
                controller.describe_events()
            else:
                controller.publish_events()
    except ControllerError as e:
        logger.exception('%s, %s', e.cause, e)
    except Exception as e:
        logger.exception(e)
    finally:
        logger.info('stop script')

if __name__ == '__main__':
    args = parse()
    setup_logging(args.debug)
    main(args)
