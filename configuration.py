import ConfigParser


class Configuration(ConfigParser.RawConfigParser):
    def __init__(self, configFile=None):
        object.__init__(self)
        self.configuration = ConfigParser.RawConfigParser()

        if (configFile) is not None:
            self.configFile = configFile
            self.read()
        else:
            try:
                raise ConfigException()
            except ConfigException, e:
                print e

    def read(self):
        try:
            with open(self.configFile):
                pass
        except IOError:
            self.setupConfig()
        else:
            self.configuration.read(self.configFile)

    def setupConfig(self):
        self.configuration.add_section('Login')
        self.configuration.set('Login', 'username', None)
        self.configuration.set('Login', 'password', None)
        self.configuration.add_section('LocalSettings')
        self.configuration.set('LocalSettings', 'first-run', True)
        self.configuration.set('LocalSettings', 'network-timeout', 30)
        self.configuration.set('LocalSettings', 'notifications', True)
        self.configuration.set('LocalSettings', 'sync-offline', False)
        self.configuration.set('LocalSettings', 'sync-dir', None)
        with open(self.configFile, 'wb') as configuration:
            self.configuration.write(configuration)

    def get(self, section, key):
        return self.configuration.get(section, key)

    def set(self, section, key, value):
        self.configuration.set(section, key, value)


class ConfigException(Exception):
    pass
