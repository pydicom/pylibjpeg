"""Utilities for managing plugins."""

from importlib import import_module
import logging
from pkg_resources import iter_entry_points
import sys


LOGGER = logging.getLogger(__name__)


def discover_plugins():
    """Return a :class:`dict` containing all registered plugins.

    .. versionadded:: 1.1

    Returns
    -------
    dict
        The available plugins as ``{plugin name: plugin module}``.
    """
    plugins = {
        val.name: val.load() for val in iter_entry_points('pylibjpeg.plugins')
    }
    return plugins


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
    return list(discover_plugins().keys())


def load_plugins():
    """Load the available plugins and add them to the namespace.

    .. versionchanged:: 1.1

        No longer takes any parameters.
    """
    plugins = discover_plugins()
    for name, module in plugins.items():
        try:
            LOGGER.debug("Importing {}".format(name))
        except ImportError as exc:
            LOGGER.debug("Failed to import {}".format(name))
            continue

        # Add successful imported modules to the namespace
        globals()[name] = module
        sys.modules['pylibjpeg.plugins.{}'.format(name)] = module
