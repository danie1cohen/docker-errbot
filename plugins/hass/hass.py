"""
Errbot module for interacting with home assistant.
"""
# pylint: disable=no-self-use,unused-argument
from itertools import chain
import os
from pprint import pformat
import subprocess

from errbot import BotPlugin, botcmd
from homeassistant import remote
import requests


HASS_TEMPLATE = {
    'HASS_URL': os.environ.get('HASS_URL', 'http://localhost'),
    'PASSWORD': os.environ.get('HASS_PASS', 'yourpassword'),
}


class HomeAssistant(BotPlugin):
    """
    Interact with Home Assistant via Errbot
    """
    def activate(self):
        """
        Triggers on plugin activation

        You should delete it if you're not using it to override any default behaviour
        """
        super(HomeAssistant, self).activate()
        self.api = remote.API(self.config['HASS_URL'], self.config['PASSWORD'])

    def configure(self, configuration):
        """Set the configuration for the kodi plugin."""
        if configuration is not None and configuration != {}:
            config = dict(chain(HASS_TEMPLATE.items(),
                                configuration.items()))
        else:
            config = HASS_TEMPLATE
        super(HomeAssistant, self).configure(config)

    def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports

        You should delete it if your plugin doesn't use any configuration like this
        """
        return HASS_TEMPLATE

    def _build_headers(self):
        """
        Create the headers for interacting with hass.
        """
        headers = {
            'x-ha-access': self.config['PASSWORD'],
            'content-type': 'application/json'
        }
        return headers

    def get(self, url, **kwargs):
        """
        Send a get request.
        """
        headers = self._build_headers()
        return requests.get(self.config['HASS_URL'] + url, headers=headers, **kwargs)

    def post(self, url, **kwargs):
        """
        Send a get request.
        """
        headers = self._build_headers()
        return requests.post(self.config['HASS_URL'] + url, headers=headers, **kwargs)

    @botcmd
    def hass_ping(self, message, args):
        """Return a simple ping of the hass api."""
        data = self.get('/api/').json()
        if 'message' in data:
            return data['message']
        else:
            return data

    def print_response(self, endpoint):
        """Returns a pretty pritned string of the endpoints response."""
        return pformat(self.get(endpoint).json())

    @botcmd
    def hass_config(self, message, args):
        """Return config information of the current connection."""
        return self.print_response('/api/config')

    @botcmd
    def hass_discovery(self, message, args):
        """Return discovery info of the hass instance."""
        return self.print_response('/api/discovery_info')

    @botcmd
    def hass_bootstrap(self, message, args):
        """Returns bootstrap info."""
        return self.print_response('/api/bootstrap')

    @botcmd
    def hass_events(self, message, args):
        """Return an array of events."""
        return self.print_response('/api/events')

    @botcmd
    def hass_services(self, message, args):
        """Return all services."""
        return self.print_response('/api/services')

    @botcmd
    def hass_states(self, message, args):
        """Prints the states."""
        return self.print_response('/api/states')

    def domain_service(self, domain, service, data):
        """Post a data dict to a domain service."""
        url = '/api/services/%s/%s' % (domain, service)
        return self.post(url, data=data)

    def call_service(self, domain, command, entity=None):
        """
        Call a service with a given command.
        """
        if entity is not None:
            result = remote.call_service(self.api, domain, command, entity)
        else:
            result = remote.call_service(self.api, domain, command)
        if result is True:
            result = 'Ok.'
        elif result is False:
            result = 'Uh oh! Something went wrong.'
        return result

    @botcmd
    def lights_on(self, message, args):
        """Turn the lights on."""
        domain = 'light'
        entity = {'entity_id': 'light.livingroom'}
        return self.call_service(domain, 'turn_on', entity)

    @botcmd
    def lights_off(self, message, args):
        """Turn the lights off."""
        domain = 'light'
        entity = {'entity_id': 'light.livingroom'}
        return self.call_service(domain, 'turn_off', entity)

    @botcmd
    def dim_lights(self, message, args):
        """Set the lights to dimmed."""
        domain = 'light'
        data = {
            'group_name': 'LivingRoom',
            'scene_name': 'Dimmed'
        }
        return self.call_service(domain, 'hue_activate_scene', data)

    @botcmd
    def hass_update(self, message, args):
        """Update hass via pip."""
        cmds = [
            '/opt/envs/artoo/bin/pip', 'install', '--upgrade', 'hass'
        ]
        subprocess.Popen(cmds)
        return 'Updating...'
