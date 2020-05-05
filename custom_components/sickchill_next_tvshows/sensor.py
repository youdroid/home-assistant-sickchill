"""Platform for sensor integration."""
import logging
from datetime import datetime

import requests
import json
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.const import *

_LOGGER = logging.getLogger(__name__)
DEFAULT_NAME = "sickchill_next_tvshows"
DEFAULT_HOST = "localhost"
DEFAULT_PROTO = "http"
DEFAULT_PORT = "8081"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TOKEN): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.string,
    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_PROTOCOL, default=DEFAULT_PROTO): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([SickChillSensor(config)])


class SickChillSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, config):
        self._state = None
        self._name = config.get(CONF_NAME)
        self.token = config.get(CONF_TOKEN)
        self.host = config.get(CONF_HOST)
        self.protocol = config.get(CONF_PROTOCOL)
        self.port = config.get(CONF_PORT)
        self.data = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.data

    def update(self):
        attributes = {}
        card_json = []

        init = {}
        """Initialized JSON Object"""
        init['title_default'] = '$title'
        init['line1_default'] = '$episode'
        init['line2_default'] = '$release'
        init['line3_default'] = '$number - $rating - $runtime'
        init['line4_default'] = '$genres'
        init['icon'] = 'mdi:eye-off'
        card_json.append(init)

        ifs_tv_shows = self.get_infos(self.protocol, self.host, self.port, self.token, 'shows')
        shows = ifs_tv_shows['data']

        for id in shows:
            if shows[id]['next_ep_airdate'] != "":
                card_items = {}
                card_items['airdate'] = shows[id]['next_ep_airdate']
                card_items['release'] = "$day, $date $time"
                card_items["title"] = shows[id]['show_name']
                card_items["poster"] = "{0}://{1}:{2}/cache/images/thumbnails/{3}.poster.jpg".format(self.protocol,
                                                                                                     self.host,
                                                                                                     self.port, id)
                card_items['studio'] = shows[id]["network"]
                all_season_show = self.get_infos(self.protocol, self.host, self.port, self.token,
                                                 'show.seasons&indexerid=' + id)
                nb_seasons = len(all_season_show['data'])
                last_season = all_season_show['data'][str(nb_seasons)]
                next_episode = "S"
                for episode in last_season:
                    if last_season[episode]['airdate'] == shows[id]['next_ep_airdate']:
                        card_items['episode'] = last_season[episode]['name']
                        if nb_seasons < 10:
                            next_episode += "0" + str(nb_seasons)
                        else:
                            next_episode += str(nb_seasons)
                        if int(episode) < 10:
                            next_episode += "E0" + str(episode)
                        else:
                            next_episode += "E" + str(episode)
                        card_items['number'] = next_episode
                card_json.append(card_items)
        attributes['data'] = json.dumps(card_json)
        self._state = ifs_tv_shows["result"]
        self.data = attributes

    def get_infos(self, proto, host, port, token, cmd):
        url = "{0}://{1}:{2}/api/{3}/?cmd={4}".format(
            proto, host, port, token, cmd)
        ifs_movies = requests.get(url).json()
        return ifs_movies