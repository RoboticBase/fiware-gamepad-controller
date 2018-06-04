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
    parser.add_argument('type', type=str, nargs='?', help='configuration type',
                        const='pxkwcr-azure', default='pxkwcr-azure')
    parser.add_argument('--describe', action='store_true', default=False, help='describe event of gamepad')
    parser.add_argument('--debug', action='store_true', default=False, help='show debug log')
    return parser.parse_args()


def setup_logging(debug):
    try:
        with open('./conf/logging.yaml', 'r') as f:
            y = yaml.load(f)
            logging.config.dictConfig(y)
            if debug:
                for handler in getLogger().handlers:
                    if handler.get_name() in 'console':
                        handler.setLevel('DEBUG')
    except FileNotFoundError:
        pass


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
