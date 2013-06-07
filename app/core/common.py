import imp
import os
import platform
import sys

from pkg_resources import resource_filename


def main_is_frozen():
    """
    Returns whether or not it is frozen in an executable
    #http://www.py2exe.org/index.cgi/HowToDetermineIfRunningFromExe
    :rtype : bool
    """
    return (hasattr(sys, "frozen") or  # new py2exe
            hasattr(sys, "importers")  # old py2exe
            or imp.is_frozen("__main__"))  # tools/freeze


def get_main_dir():
    """
    Returns the directory in which it is being run
    :rtype : str
    """
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0])


def cert_path():
    """
    Returns the certificate path depending on the platform
    :rtype : str
    """
    if platform.system() == 'Windows':
        app_dir = os.path.join(
            os.getenv('appdata', os.path.expanduser('~')), 'Kissync'
        )
        if not os.path.exists(app_dir):
            os.mkdir(app_dir)
        stored_cert = os.path.join(app_dir, 'cacert.pem')
        if not os.path.exists(stored_cert):
            cert_content = open(os.path.join(get_main_dir(), 'cacert.pem')).read()
            with open(stored_cert, 'w') as f:
                f.write(cert_content)
        return stored_cert
    else:
        possible_cert_paths = [
            '/usr/local/share/certs/ca-root-nss.crt',
            '/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem',
            '/etc/pki/tls/certs/ca-bundle.crt',
            '/etc/ssl/ca-bundle.pem',
            '/etc/ssl/certs/ca-bundle.crt',
            '/etc/ssl/certs/ca-certificates.crt',
        ]
        for path in possible_cert_paths:
            if os.path.exists(path):
                return path
        return resource_filename(__name__, 'cacert.pem')
