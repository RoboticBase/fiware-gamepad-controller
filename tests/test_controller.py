# -*- cofing: utf-8 -*-

import re
import ssl
import threading
import time
from unittest.mock import call

from pygame.locals import JOYBUTTONDOWN, JOYBUTTONUP, JOYHATMOTION, JOYAXISMOTION

import pytest

from src.controller import Controller, ControllerError, TOPIC_KEY


class TestController:

    def test_describe_events(self, mocker, test_config):
        counter = type('', (), {'count': 0})()
        stopper = type('', (), {'is_stop': False})()

        def mocked_get():
            counter.count += 1
            if counter.count == 1:
                return [type('', (), {'type': JOYBUTTONDOWN, 'button': 1})(), ]
            elif counter.count == 2:
                return [type('', (), {'type': JOYBUTTONUP, 'button': 2})(), ]
            elif counter.count == 3:
                return [type('', (), {'type': JOYHATMOTION, 'hat': 3, 'value': (0, 1)})(), ]
            elif counter.count == 4:
                return [type('', (), {'type': JOYAXISMOTION, 'axis': 4, 'value': 0.0})(), ]
            else:
                stopper.is_stop = True
                return []

        def stop():
            while not stopper.is_stop:
                time.sleep(0.1)
            controller._is_stop = True

        mocked_pygame = mocker.patch('src.controller.pygame')
        mocked_mqtt = mocker.patch('src.controller.mqtt')
        mocked_logger = mocker.patch('src.controller.logger')

        controller = Controller(test_config)
        mocked_pygame.init.assert_called_once_with()
        mocked_pygame.display.init.assert_called_once_with()
        mocked_pygame.joystick.init.assert_called_once_with()
        mocked_pygame.joystick.Joystick.assert_called_once_with(0)
        mocked_pygame.joystick.Joystick.return_value.init.assert_called_once_with()
        assert not mocked_mqtt.called
        assert mocked_logger.info.call_args_list[0] == call('initialized %s', test_config.name)

        mocked_pygame.event.get.side_effect = mocked_get

        t1 = threading.Thread(target=controller.describe_events)
        t2 = threading.Thread(target=stop)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert not mocked_mqtt.called
        assert not mocked_mqtt.Client.return_value.connect.called
        assert not mocked_mqtt.Client.return_value.loop_start.called
        assert not mocked_mqtt.Client.return_value.publish.called
        assert not mocked_mqtt.Client.return_value.loop_stop.called
        assert not mocked_mqtt.Client.return_value.disconnect.called

        assert mocked_logger.info.call_args_list[1] == call('start describing...')
        assert mocked_logger.info.call_args_list[2] == call('Button down event, event.button=%s', 1)
        assert mocked_logger.info.call_args_list[3] == call('Button up event, event.button=%s', 2)
        assert mocked_logger.info.call_args_list[4] == call('Hat event, event.hat=%s, event.value=%s', 3, (0, 1))
        assert mocked_logger.info.call_args_list[5] == call('Axis event, event.axis=%s, event.value=%s', 4, 0.0)
        assert mocked_logger.info.call_args_list[6] == call('stop describing...')

    @pytest.mark.parametrize('cafile', [None, '', 'not_exists', 'exists'])
    @pytest.mark.parametrize('username', [None, '', 'user1'])
    @pytest.mark.parametrize('password', [None, '', 'password1'])
    @pytest.mark.freeze_time('2018-01-02T03:04:05')
    def test_publish_events(self, mocker, test_config, cafile_path, cafile, username, password):
        if cafile == 'exists':
            test_config.mqtt.cafile = cafile_path
        elif cafile is not None:
            test_config.mqtt.cafile = cafile

        if username is not None:
            test_config.mqtt.username = username
        if password is not None:
            test_config.mqtt.password = password

        counter = type('', (), {'count': 0})()
        stopper = type('', (), {'is_stop': False})()

        def mocked_get():
            counter.count += 1
            if counter.count == 1:
                return [type('', (), {'type': JOYBUTTONDOWN, 'button': 0})(), ]
            elif counter.count == 2:
                return [type('', (), {'type': JOYBUTTONDOWN, 'button': 1})(), ]
            elif counter.count == 3:
                return [type('', (), {'type': JOYBUTTONDOWN, 'button': 2})(), ]
            elif counter.count == 4:
                return [type('', (), {'type': JOYBUTTONDOWN, 'button': 3})(), ]
            elif counter.count == 5:
                return [type('', (), {'type': JOYHATMOTION, 'hat': 'joyhat', 'value': (0, 1)})(), ]
            elif counter.count == 6:
                return [type('', (), {'type': JOYHATMOTION, 'hat': 'joyhat', 'value': (0, -1)})(), ]
            elif counter.count == 7:
                return [type('', (), {'type': JOYHATMOTION, 'hat': 'joyhat', 'value': (1, 0)})(), ]
            elif counter.count == 8:
                return [type('', (), {'type': JOYHATMOTION, 'hat': 'joyhat', 'value': (-1, 0)})(), ]
            elif counter.count == 9:
                return [type('', (), {'type': JOYBUTTONDOWN, 'button': 4,
                                      '__repr__': lambda self: 'joybutton down 4'})(), ]
            elif counter.count == 10:
                return [type('', (), {'type': JOYHATMOTION, 'hat': 'joyhat', 'value': (0, 0),
                                      '__repr__': lambda self: 'joyhat value (0, 0)'})(), ]
            elif counter.count == 11:
                return [type('', (), {'type': JOYBUTTONUP, 'button': 0,
                                      '__repr__': lambda self: 'joybutton_up'})(), ]
            elif counter.count == 12:
                return [type('', (), {'type': JOYAXISMOTION, 'axis': 1, 'value': 0.0,
                                      '__repr__': lambda self: 'joybutton_up'})(), ]
            else:
                stopper.is_stop = True
                return []

        def stop():
            while not stopper.is_stop:
                time.sleep(0.1)
            controller._is_stop = True

        mocked_pygame = mocker.patch('src.controller.pygame')
        mocked_mqtt = mocker.patch('src.controller.mqtt')
        mocked_logger = mocker.patch('src.controller.logger')

        controller = Controller(test_config)
        mocked_pygame.init.assert_called_once_with()
        mocked_pygame.display.init.assert_called_once_with()
        mocked_pygame.joystick.init.assert_called_once_with()
        mocked_pygame.joystick.Joystick.assert_called_once_with(0)
        mocked_pygame.joystick.Joystick.return_value.init.assert_called_once_with()
        assert not mocked_mqtt.called
        assert mocked_logger.info.call_args_list[0] == call('initialized %s', test_config.name)

        mocked_pygame.event.get.side_effect = mocked_get

        controller.connect()

        t1 = threading.Thread(target=controller.publish_events)
        t2 = threading.Thread(target=stop)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        mocked_mqtt.Client.assert_called_once_with(protocol=mocked_mqtt.MQTTv311)
        mocked_client = mocked_mqtt.Client.return_value
        if cafile == 'exists':
            mocked_client.tls_set.assert_called_once_with(cafile_path, tls_version=ssl.PROTOCOL_TLSv1_2)
        else:
            mocked_client.tls_set.assert_not_called()
        if username is not None and password is not None:
            mocked_client.username_pw_set.assert_called_once_with(username, password)
        else:
            mocked_client.username_pw_set.assert_not_called()
        mocked_client.connect.assert_called_once_with('mqtt.example.com', port=8883, keepalive=60)
        mocked_client.loop_start.assert_called_once_with()
        assert mocked_client.publish.call_args_list[0] == call(
            '/demo1/gamepad/attrs', '2018-01-02T03:04:05.000000+0000|button|triangle')
        assert mocked_client.publish.call_args_list[1] == call(
            '/demo1/gamepad/attrs', '2018-01-02T03:04:05.000000+0000|button|circle')
        assert mocked_client.publish.call_args_list[2] == call(
            '/demo1/gamepad/attrs', '2018-01-02T03:04:05.000000+0000|button|cross')
        assert mocked_client.publish.call_args_list[3] == call(
            '/demo1/gamepad/attrs', '2018-01-02T03:04:05.000000+0000|button|square')
        assert mocked_client.publish.call_args_list[4] == call(
            '/demo1/gamepad/attrs', '2018-01-02T03:04:05.000000+0000|button|up')
        assert mocked_client.publish.call_args_list[5] == call(
            '/demo1/gamepad/attrs', '2018-01-02T03:04:05.000000+0000|button|down')
        assert mocked_client.publish.call_args_list[6] == call(
            '/demo1/gamepad/attrs', '2018-01-02T03:04:05.000000+0000|button|right')
        assert mocked_client.publish.call_args_list[7] == call(
            '/demo1/gamepad/attrs', '2018-01-02T03:04:05.000000+0000|button|left')
        mocked_client.loop_stop.assert_called_once_with()
        mocked_client.disconnect.assert_called_once_with()

        assert mocked_logger.info.call_args_list[0] == call('initialized %s', test_config.name)
        assert mocked_logger.info.call_args_list[1] == call('start publishing...')
        assert mocked_logger.info.call_args_list[2] == call(
            'published "%s" to "%s"', '2018-01-02T03:04:05.000000+0000|button|triangle', '/demo1/gamepad/attrs')
        assert mocked_logger.info.call_args_list[3] == call(
            'published "%s" to "%s"', '2018-01-02T03:04:05.000000+0000|button|circle', '/demo1/gamepad/attrs')
        assert mocked_logger.info.call_args_list[4] == call(
            'published "%s" to "%s"', '2018-01-02T03:04:05.000000+0000|button|cross', '/demo1/gamepad/attrs')
        assert mocked_logger.info.call_args_list[5] == call(
            'published "%s" to "%s"', '2018-01-02T03:04:05.000000+0000|button|square', '/demo1/gamepad/attrs')
        assert mocked_logger.info.call_args_list[6] == call(
            'published "%s" to "%s"', '2018-01-02T03:04:05.000000+0000|button|up', '/demo1/gamepad/attrs')
        assert mocked_logger.info.call_args_list[7] == call(
            'published "%s" to "%s"', '2018-01-02T03:04:05.000000+0000|button|down', '/demo1/gamepad/attrs')
        assert mocked_logger.info.call_args_list[8] == call(
            'published "%s" to "%s"', '2018-01-02T03:04:05.000000+0000|button|right', '/demo1/gamepad/attrs')
        assert mocked_logger.info.call_args_list[9] == call(
            'published "%s" to "%s"', '2018-01-02T03:04:05.000000+0000|button|left', '/demo1/gamepad/attrs')
        assert mocked_logger.info.call_args_list[10] == call('stop publishing...')

        assert mocked_logger.debug.call_args_list[0] == call('ignore event, %s', 'joybutton down 4')
        assert mocked_logger.debug.call_args_list[1] == call('ignore event, %s', 'joyhat value (0, 0)')
        assert mocked_logger.debug.call_args_list[2] == call('ignore event, %s', 'joybutton_up')
        assert mocked_logger.debug.call_args_list[3] == call('ignore event, %s', 'joybutton_up')

    def test_no_topic(sefl, mocker, test_config):
        test_config.mqtt.topics[0].key = 'invalid'

        counter = type('', (), {'count': 0})()
        stopper = type('', (), {'is_stop': False})()

        def mocked_get():
            counter.count += 1
            if counter.count == 1:
                return [type('', (), {'type': JOYBUTTONDOWN, 'button': 0})(), ]
            elif counter.count == 2:
                return [type('', (), {'type': JOYHATMOTION, 'hat': 'joyhat', 'value': (0, 1)})(), ]
            elif counter.count == 3:
                return [type('', (), {'type': JOYBUTTONUP, 'button': 0,
                                      '__repr__': lambda self: 'joybutton_up'})(), ]
            elif counter.count == 4:
                return [type('', (), {'type': JOYAXISMOTION, 'axis': 1, 'value': 0.0,
                                      '__repr__': lambda self: 'joybutton_up'})(), ]
            else:
                stopper.is_stop = True
                return []

        def stop():
            while not stopper.is_stop:
                time.sleep(0.1)
            controller._is_stop = True

        mocked_pygame = mocker.patch('src.controller.pygame')
        mocked_mqtt = mocker.patch('src.controller.mqtt')
        mocked_logger = mocker.patch('src.controller.logger')

        controller = Controller(test_config)
        mocked_pygame.init.assert_called_once_with()
        mocked_pygame.display.init.assert_called_once_with()
        mocked_pygame.joystick.init.assert_called_once_with()
        mocked_pygame.joystick.Joystick.assert_called_once_with(0)
        mocked_pygame.joystick.Joystick.return_value.init.assert_called_once_with()
        assert not mocked_mqtt.called
        assert mocked_logger.info.call_args_list[0] == call('initialized %s', test_config.name)

        mocked_pygame.event.get.side_effect = mocked_get

        t1 = threading.Thread(target=controller.publish_events)
        t2 = threading.Thread(target=stop)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert not mocked_mqtt.called
        assert not mocked_mqtt.Client.return_value.connect.called
        assert not mocked_mqtt.Client.return_value.loop_start.called
        assert not mocked_mqtt.Client.return_value.publish.called
        assert not mocked_mqtt.Client.return_value.loop_stop.called
        assert not mocked_mqtt.Client.return_value.disconnect.called

        assert mocked_logger.info.call_args_list[0] == call('initialized %s', test_config.name)
        assert mocked_logger.info.call_args_list[1] == call('start publishing...')
        assert mocked_logger.info.call_args_list[2] == call('stop publishing...')

        assert mocked_logger.debug.call_args_list[0] == call('ignore event, %s', 'joybutton_up')
        assert mocked_logger.debug.call_args_list[1] == call('ignore event, %s', 'joybutton_up')

        assert mocked_logger.warning.call_args_list[0] == call('no topic found, key=%s', TOPIC_KEY)
        assert mocked_logger.warning.call_args_list[1] == call('no topic found, key=%s', TOPIC_KEY)

    def test_pygame_init_error(self, mocker, test_config):
        mocked_pygame = mocker.patch('src.controller.pygame')
        mocked_mqtt = mocker.patch('src.controller.mqtt')
        mocked_pygame.error = Exception

        mocked_pygame.init.side_effect = Exception()

        err = re.compile(r'^.*init error')

        with pytest.raises(ControllerError) as e:
            Controller(test_config)
        assert err.match(str(e))
        assert not mocked_mqtt.called
        assert not mocked_mqtt.Client.return_value.connect.called
        assert not mocked_mqtt.Client.return_value.loop_start.called
        assert not mocked_mqtt.Client.return_value.publish.called
        assert not mocked_mqtt.Client.return_value.loop_stop.called
        assert not mocked_mqtt.Client.return_value.disconnect.called

    @pytest.mark.parametrize('method', ['describe_events', 'publish_events'])
    def test_pygame_subscribe_events_error(self, mocker, test_config, method):
        mocked_pygame = mocker.patch('src.controller.pygame')
        mocked_mqtt = mocker.patch('src.controller.mqtt')
        mocked_logger = mocker.patch('src.controller.logger')
        mocked_pygame.error = Exception

        controller = Controller(test_config)
        mocked_pygame.init.assert_called_once_with()
        mocked_pygame.display.init.assert_called_once_with()
        mocked_pygame.joystick.init.assert_called_once_with()
        mocked_pygame.joystick.Joystick.assert_called_once_with(0)
        mocked_pygame.joystick.Joystick.return_value.init.assert_called_once_with()
        assert not mocked_mqtt.called
        assert mocked_logger.info.call_args_list[0] == call('initialized %s', test_config.name)

        mocked_pygame.event.get.side_effect = Exception()

        err = re.compile(r'^.*subscribe event error')

        with pytest.raises(ControllerError) as e:
            getattr(controller, method)()
        assert err.match(str(e))
        assert not mocked_mqtt.called
        assert not mocked_mqtt.Client.return_value.connect.called
        assert not mocked_mqtt.Client.return_value.loop_start.called
        assert not mocked_mqtt.Client.return_value.publish.called
        assert not mocked_mqtt.Client.return_value.loop_stop.called
        assert not mocked_mqtt.Client.return_value.disconnect.called

    def test_mqtt_connection_error(self, mocker, test_config):
        mocked_pygame = mocker.patch('src.controller.pygame')
        mocked_mqtt = mocker.patch('src.controller.mqtt')
        mocked_logger = mocker.patch('src.controller.logger')
        mocked_pygame.error = ControllerError

        controller = Controller(test_config)
        mocked_pygame.init.assert_called_once_with()
        mocked_pygame.display.init.assert_called_once_with()
        mocked_pygame.joystick.init.assert_called_once_with()
        mocked_pygame.joystick.Joystick.assert_called_once_with(0)
        mocked_pygame.joystick.Joystick.return_value.init.assert_called_once_with()
        assert not mocked_mqtt.called
        assert mocked_logger.info.call_args_list[0] == call('initialized %s', test_config.name)

        mocked_pygame.event.get.return_value = [type('', (), {'type': JOYBUTTONDOWN, 'button': 0})(), ]
        mocked_mqtt.Client.return_value.connect.side_effect = OSError

        with pytest.raises(OSError):
            controller.connect()

        mocked_mqtt.Client.assert_called_once_with(protocol=mocked_mqtt.MQTTv311)
        mocked_client = mocked_mqtt.Client.return_value
        mocked_client.tls_set.assert_not_called()
        mocked_client.username_pw_set.assert_not_called()
        mocked_client.connect.assert_called_once_with('mqtt.example.com', port=8883, keepalive=60)
        mocked_client.loop_start.assert_not_called()
        mocked_client.loop_stop.assert_not_called()
        mocked_client.disconnect.assert_not_called()
