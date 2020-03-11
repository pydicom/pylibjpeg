"""Utilities for managing plugins."""

from importlib import import_module
import logging
import sys

from pylibjpeg._config import PLUGINS


LOGGER = logging.getLogger(__name__)


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


def get_plugin_coders():
    """Return the available plugin decoders and encoders.

    Returns
    -------
    dict, dict
        A ``dict`` containing the available (decoders, encoders) as
        ``{plugin name : {UID : callable}}``.
    """
    decoders = {}
    encoders = {}
    for name in get_plugins():
        decoders[name] = getattr(globals()[name], 'DICOM_DECODERS')
        encoders[name] = getattr(globals()[name], 'DICOM_ENCODERS')

    return decoders, encoders


def get_plugins(as_objects=False):
    """Return the available plugins.

    Returns
    -------
    list of str
        A list containing the names of the available plugins.
    """
    return [nn for nn in PLUGINS if nn in globals()]


def get_transfer_syntaxes(decodable=False, encodable=False):
    """Return a list of decodable or encodable *Transfer Syntax UIDs*.

    Parameters
    ----------
    decodable : bool, optional
        Return a list of decodable *Transfer Syntax UIDs*.
    encodable : bool, optional
        Return a list of encodable *Transfer Syntax UIDs*.

    Returns
    -------
    list of str
        A list containing unique *Transfer Syntax UIDs*.
    """
    if not decodable and not encodable:
        raise ValueError("Either 'decodable' or 'encodable' must be True")

    dec, enc = get_plugin_coders()
    if decodable:
        obj = dec
    else:
        obj = enc

    uids = []
    for name, uid_coder in obj.items():
        uids += uid_coder.keys()

    return list(set(uids))


def get_decoder(uid):
    """Return a callable function that can decode pixel data encoding using
    the *Transfer Syntax UID* `uid`.
    """
    decoders, _ = get_plugin_coders()
    for name in decoders:
        try:
            return decoders[name][uid]
        except KeyError:
            pass

    msg = (
        "No decoder is available for the Transfer Syntax UID - '{}'"
        .format(uid)
    )
    raise NotImplementedError(msg)


def get_decoders():
    decoders = {}
    for name in get_plugins():
        decoders[name] = getattr(globals()[name], 'decode')

    return decoders


def get_uid_decoders():
    uids = get_transfer_syntaxes(decodable=True)
    decoders = {}
    dec, _ = get_plugin_coders()
    for name, uid_coder in dec.items():
        decoders.update(uid_coder)

    return decoders


def get_encoder(uid):
    """Return a callable function that can encode pixel data using
    the *Transfer Syntax UID* `uid`.
    """
    _, encoders = get_plugin_coders()
    for name in encoders:
        try:
            return encoders[name][uid]
        except KeyError:
            pass

    msg = (
        "No encoder is available for the Transfer Syntax UID - '{}'"
        .format(uid)
    )
    raise NotImplementedError(msg)
