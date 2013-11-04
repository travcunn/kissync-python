import imp
import os
import platform
import requests
import sys

try:
    import winshell
    from win32com.client import Dispatch
    win32Loaded = True
except:
    win32Loaded = False

from pkg_resources import resource_filename


def create_shortcut():
    if win32Loaded:
        path = os.path.join(winshell.startup(), 'SmartFile Sync.lnk')
        target = os.path.join(get_main_dir(), 'SmartFile.exe')
        workingDir = get_main_dir()
        iconpath = os.path.join(get_main_dir(), 'icon.ico')

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = workingDir
        shortcut.IconLocation = iconpath
        shortcut.save()


def delete_shortcut():
    if win32Loaded:
        path = os.path.join(winshell.startup(), 'SmartFile Sync.lnk')
        if os.path.isfile(path):
            os.remove(path)


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
        stored_cert = os.path.join(get_main_dir(), 'cacert.pem')
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


def check_latest_version():
    """ Checks the server for the latest version number """
    version = requests.get("http://www.kissync.com/check-version").text
    return version


def is_latest_version(current_version):
    """ Checks a specified current_version with the latest version """
    latest_version = check_latest_version()
    if (version(current_version) < version(latest_version)):
        return False
    else:
        return True


def version(version_number):
    return tuple(map(int, (version_number.split("."))))


def settingsDirectory():
    if platform.system() == 'Windows':
        app_dir = os.path.join(
            os.getenv('appdata', os.path.expanduser('~')), 'Smartfile'
        )
        if not os.path.exists(app_dir):
            os.mkdir(app_dir)
    else:
        app_dir = os.path.join(os.path.expanduser("~"), ".smartfile")
    return app_dir


def settingsFile():
    if platform.system() == 'Windows':
        settings_file = os.path.join(
            os.getenv('appdata', os.path.expanduser('~')), 'Smartfile', 'config.cfg'
        )
    else:
        settings_file = os.path.join(os.path.expanduser("~"), ".smartfile", "config.cfg")
    return settings_file
