"""Utilities for managing plugins."""

from importlib import import_module
import logging
import sys

from pylibjpeg._config import PLUGINS


LOGGER = logging.getLogger(__name__)


def get_decoders():
    """Return a :class:`dict` of {plugin: decoder func}."""
    decoders = {}
    for name in get_plugins():
        try:
            decoders[name] = getattr(globals()[name], 'decode')
        except AttributeError:
            pass

    return decoders


def get_encoders():
    """Return a :class:`dict` of {plugin: encoder func}."""
    encoders = {}
    for name in get_plugins():
        try:
            encoders[name] = getattr(globals()[name], 'encode')
        except AttributeError:
            pass

    return encoders


def get_plugins():
    """Return the available plugins.

    Returns
    -------
    list of str
        A list containing the names of the available plugins.
    """
    return [nn for nn in PLUGINS if nn in globals()]


def load_plugins(plugins):
    """Load the `plugins` and add them to the namespace."""
    for plugin in plugins:
        try:
            LOGGER.debug("Importing {}".format(plugin))
            module = import_module(plugin)
        except ImportError as exc:
            LOGGER.debug("Failed to import {}".format(plugin))
            continue

        # Add successful imported modules to the namespace
        globals()[plugin] = module
        sys.modules['pylibjpeg.plugins.{}'.format(plugin)] = module
