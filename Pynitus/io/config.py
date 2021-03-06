"""
    Pynitus - A free and democratic music playlist
    Copyright (C) 2017  Noah Hummel

    This file is part of the Pynitus program, see <https://github.com/strangedev/Pynitus>.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from typing import Any

import yaml

from Pynitus.framework import memcache


def init_config():
    """
    Should be called once on server startup.
    Initializes the persistent cache and loads all config values from disk.
    :return: None
    """

    # TODO: absolute poth for config path in bootstrap script
    # TODO: log errors
    with open("./pynitus.yaml") as f:
        config = yaml.safe_load(f)

    memcache.set("config", config)


def get(key: str) -> Any:
    """
    Gets a value from the config by it's key.
    :param key: The key of the value
    :return: The value or None
    """
    return memcache.get("config").get(key)
