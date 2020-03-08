"""Utilities for managing plugins."""


class PluginManager(object):
    """The plugin manager."""
    def __init__(self, plugins):
        # dict {str name: module object, ...}
        self._plugins = {}
        for pkg_name in plugins:
            plugin = self.import_package(pkg_name)
            if plugin and plugin not in self._plugins:
                self._plugins[pkg_name] = plugin

    def add_plugin(self, plugin):
        """Add a plugin."""
        raise NotImplementedError()

    def import_package(pkg):
        """Return the plugin for a package or ``None`` if not importable."""
        raise NotImplementedError()

    @property
    def plugins(self):
        """Return a list of available and enabled plugins."""
        out = {}
        for (pkg_name, plugin) in self._plugins:
            if plugin.is_available and plugin.enabled:
                out[pkg_name] = plugin

        return out

    def remove_plugin(self, plugin):
        """Remove a plugin."""
        raise NotImplementedError()

    @property
    def transfer_syntaxes(self):
        """Return a list of DICOM Transfer Syntax UIDs supported by the
        plugins.

        """
        uids = []
        for (pkg_name, plugin) in self.plugins:
            uids += plugin.transfer_syntaxes

        return list(set(uids))


class Plugin(object):
    """Base class for plugins."""
    def __init__(self, meta, enabled=True):
        """Create a new Plugin object."""
        self.meta = meta
        self._enabled = enabled
        self._uids = []
        self._is_available = True

    @property
    def enabled(self):
        """Returns ``True`` if the plugin is enabled, ``False`` otherwise."""
        return self._enabled

    @enabled.setter
    def enabled(self, is_enabled):
        """Enable or disable the plugin."""
        self._enabled = bool(is_enabled)

    @property
    def is_available(self):
        """Return ``True`` if the plugin is available for use, ``False``
        otherwise.
        """
        return self._is_available

    @property
    def transfer_syntaxes(self):
        """Return a list of supported DICOM Transfer Syntax UIDs."""
        return self._uids
