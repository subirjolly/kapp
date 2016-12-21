import configparser
import pkg_resources


class ConfigLoader(object):
    def __init__(self, filename, config_module=None):
        """
        Constructor.

        Args:
            filename (string): Config file to be loaded.
            config_module (string): Module to load config file from.
        """
        if config_module is not None:
            self.config_module = config_module
        else:
            self.config_module = "src.config"

        self.filename = filename

        self.config = self._load()

    def _load(self):
        """
        Loads the config from the specified filename and
        config module in constructor.

        Returns:
            configparser.ConfigParser: Loaded config.
        """
        path = pkg_resources.resource_filename(
            self.config_module, self.filename)
        config = configparser.ConfigParser()
        # Preserve case of property names
        config.optionxform = str

        try:
            with open(path, "r") as fp:
                config.readfp(fp)
        except IOError:
            raise Exception(
                "Failed to load config: {0}".format(self.filename))

        return config

    def get(self, section):
        """
        Return the specified section dictionary from the loaded config.

        Args:
            section (string): Section to be returned from the loaded config.

        Returns:
            dict: Dictionary representation of the section from the
                loaded config.
        """
        return dict(self.config.items(section))
