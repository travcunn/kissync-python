import os

try:
    import simplejson as json
except ImportError:
    import json


class Config(object):
    """ Configuration manager object. Specify a config_file path. """
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = {'login-token': None,
                            'login-verifier': None,
                            'first-run': True,
                            'autostart': True,
                            'network-timeout': 30}

        try:
            self.read()
        except:
            pass

    def read(self):
        """Reads the configuration from the disk"""
        try:
            # read json data from the disk
            with open(self.config_file, 'rb') as f:
                self.config_data = json.load(f)
        except IOError, err:
            # No such file or directory, so save default values
            if err.errno == 2:
                self.save()

    def save(self):
        """Saves the configuration to the disk"""
        # create the appropriate folder it is missing
        filename = os.path.basename(self.config_file)
        if not os.path.exists(self.config_file.strip(filename)):
            os.makedirs(self.config_file.strip(filename))

        # write json data to the disk
        with open(self.config_file, 'wb') as f:
            json.dump(self.config_data, f)

    def get(self, key):
        """ Returns a value based upon the key. """
        self.read()
        return self.config_data[key]

    def set(self, key, value):
        """ Set an option given a key and a value. """
        self.read()
        self.config_data[key] = value
        self.save()
