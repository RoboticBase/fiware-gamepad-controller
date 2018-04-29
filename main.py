#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

import yaml

from src.controller import Controller, ControllerError

def parse():
    parser = argparse.ArgumentParser(description='operate geme controller')
    parser.add_argument('type', type=str, nargs='?', help='controller type',
                        const='pxkwcr', default='pxkwcr', choices=['pxkwcr',])
    parser.add_argument('--describe', action='store_true', default=False, help='describe event id')
    return parser.parse_args()

def main(args):
    with open(f'./conf/{args.type}.yaml', 'r') as f:
        conf = yaml.load(f)
        try:
            controller = Controller(conf)
            if args.describe:
                controller.describeEvents()
            else:
                controller.publishEvents()
        except ControllerError as e:
            print(f'{str(e)}, cause={str(e.cause)}')

if __name__ == '__main__':
    args = parse()
    main(args)
