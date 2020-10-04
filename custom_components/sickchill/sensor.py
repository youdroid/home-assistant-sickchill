"""Platform for sensor integration."""
import json
import logging
import os
import re
import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.const import *
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)
DEFAULT_NAME = "sickchill"
DEFAULT_HOST = "localhost"
DEFAULT_PROTO = "http"
DEFAULT_PORT = "8081"
DEFAULT_SORTING = "name"
CONF_SORTING = "sort"
CONF_WEB_ROOT = "webroot"
DEFAULT_WEB_ROOT = ""
CONF_RETURN_VALUE = "json"
DEFAULT_JSON_RETURN = True

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TOKEN): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.string,
    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_PROTOCOL, default=DEFAULT_PROTO): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SORTING, default=DEFAULT_SORTING): cv.string,
    vol.Optional(CONF_WEB_ROOT, default=DEFAULT_WEB_ROOT): cv.string,
    vol.Optional(CONF_RETURN_VALUE, default=DEFAULT_JSON_RETURN): cv.boolean
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([SickChillSensor(config, hass)])


class SickChillSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, config, hass):
        self._state = None
        self._name = config.get(CONF_NAME)
        self.token = config.get(CONF_TOKEN)
        self.host = config.get(CONF_HOST)
        self.protocol = config.get(CONF_PROTOCOL)
        self.port = config.get(CONF_PORT)
        self.base_dir = str(hass.config.path()) + '/'
        self.data = None
        self.sort = config.get(CONF_SORTING)
        self.web_root = config.get(CONF_WEB_ROOT)
        self.json = config.get(CONF_RETURN_VALUE)

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
        card_shows = []
        init = {}
        """Initialized JSON Object"""
        init['title_default'] = '$title'
        init['line1_default'] = '$episode'
        init['line2_default'] = '$release'
        init['line3_default'] = '$number - $rating - $runtime'
        init['line4_default'] = '$genres'
        init['icon'] = 'mdi:eye-off'
        card_json.append(init)

        ifs_tv_shows = self.get_infos(self.protocol, self.host, self.port, self.token, self.web_root, 'shows')
        shows = ifs_tv_shows['data']

        directory = "{0}/www/custom-lovelace/{1}/images/".format(self.base_dir, self._name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        regex_img = re.compile(r'\d+-(fanart|poster)\.jpg')
        lst_images = list(filter(regex_img.search,
                                 os.listdir(directory)))

        for id in shows:
            if shows[id]['next_ep_airdate'] != "":
                card_items = {}
                card_items['airdate'] = shows[id]['next_ep_airdate']
                card_items['release'] = "$day, $date $time"
                card_items["title"] = shows[id]['show_name']

                fanart = "{0}-fanart.jpg".format(id)
                poster = "{0}-poster.jpg".format(id)

                card_items["poster"] = self.save_img(lst_images, directory, 'poster', poster, id, card_items)

                card_items["fanart"] = self.save_img(lst_images, directory, 'fanart', fanart, id, card_items)

                card_items['studio'] = shows[id]["network"]

                season_list = self.get_infos(self.protocol, self.host, self.port, self.token, self.web_root,
                                             'show.seasonlist&indexerid=' + id + '&sort=desc')

                nb_seasons = season_list["data"][0]

                last_season_detail = self.get_infos(self.protocol, self.host, self.port, self.token, self.web_root,
                                                    'show.seasons&indexerid=' + id + '&season=' + str(nb_seasons))

                last_season = last_season_detail["data"]

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
                        break
                card_shows.append(card_items)

        if self.sort == "date":
            card_shows.sort(key=lambda x: x.get('airdate'))
        card_json = card_json + card_shows

        if self.json:
            attributes['data'] = json.dumps(card_json)
        else:
            attributes['data'] = card_json

        self._state = ifs_tv_shows["result"]
        self.data = attributes
        self.delete_old_tvshows(lst_images, directory)

    def get_infos(self, proto, host, port, token, web_root, cmd):
        url = "{0}://{1}:{2}{3}/api/{4}/?cmd={5}".format(
            proto, host, port, web_root, token, cmd)
        ifs_movies = requests.get(url).json()
        return ifs_movies

    def get_img(self, type, id):
        url = "{0}://{1}:{2}{3}/api/{4}/?cmd=show.get{5}&indexerid={6}".format(
            self.protocol, self.host, self.port, self.web_root, self.token, type, id)
        img = requests.get(url)
        return img

    def save_img(self, lst_images, directory, type, image, id, card_items):
        if image in lst_images:
            lst_images.remove(image)
        else:
            img_data = self.get_img(type, id)
            if not img_data.status_code.__eq__(200):
                _LOGGER.error('No ' + type + ' found for ' + card_items['title'])
                return ""

            try:
                open(directory + image, 'wb').write(img_data.content)
            except IOError:
                _LOGGER.error("Unable to create file.")
        return "/local/custom-lovelace/{0}/images/{1}".format(self._name, image)

    def delete_old_tvshows(self, lst_images, directory):
        for img in lst_images:
            try:
                os.remove(directory + img)
                _LOGGER.info("Delete finished tv show images")
            except IOError:
                _LOGGER.error("Unable to delete file.")
