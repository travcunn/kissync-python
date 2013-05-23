import os
import sys
import urllib
import urlparse
import requests
from smartfile import Client
from smartfile import OAuthToken
from smartfile.errors import APIError

from requests_oauthlib import OAuth1
from oauthlib.oauth1 import SIGNATURE_PLAINTEXT


class SmartFileClient(Client):
    """Overrides Client from the smartfile library"""
    def __init__(self, **kwargs):
        self.cert_path = self.resource_path('cacert.pem')
        super(SmartFileClient, self).__init__(**kwargs)

    def get(self, endpoint, id=None, **kwargs):
        return self._request('get', endpoint, id=id, params=kwargs, verify=self.cert_path)

    def put(self, endpoint, id=None, **kwargs):
        return self._request('put', endpoint, id=id, data=kwargs, verify=self.cert_path)

    def post(self, endpoint, id=None, **kwargs):
        return self._request('post', endpoint, id=id, data=kwargs, verify=self.cert_path)

    def delete(self, endpoint, id=None, **kwargs):
        return self._request('delete', endpoint, id=id, data=kwargs, verify=self.cert_path)


class OAuthClient(SmartFileClient):
    def __init__(self, client_token=None, client_secret=None, access_token=None,
                 access_secret=None, **kwargs):
        self._client = OAuthToken(client_token, client_secret)
        if not self._client.is_valid():
            raise APIError('You must provide a client_token and client_secret '
                           'for OAuth.')
        self._access = OAuthToken(access_token, access_secret)
        super(OAuthClient, self).__init__(**kwargs)

    def _do_request(self, *args, **kwargs):
        if not self._access.is_valid():
            raise APIError('You must obtain an access token before making API '
                           'calls.')
        # Add the OAuth parameters.
        kwargs['auth'] = OAuth1(self._client.token,
                                client_secret=self._client.secret,
                                resource_owner_key=self._access.token,
                                resource_owner_secret=self._access.secret,
                                signature_method=SIGNATURE_PLAINTEXT)
        return super(OAuthClient, self)._do_request(*args, **kwargs)

    def _resource_path(self, relative):
        return os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), relative)

    def get_request_token(self, callback=None):
        "The first step of the OAuth workflow."
        if callback:
            callback = unicode(callback)
        oauth = OAuth1(self._client.token,
                       client_secret=self._client.secret,
                       callback_uri=callback,
                       signature_method=SIGNATURE_PLAINTEXT)
        cert_path = self._resource_path('cacert.pem')
        r = requests.post(urlparse.urljoin(self.url, 'oauth/request_token/'), auth=oauth, verify=cert_path)
        credentials = urlparse.parse_qs(r.text)
        self.__request = OAuthToken(credentials.get('oauth_token')[0],
                                    credentials.get('oauth_token_secret')[0])
        return self.__request

    def get_authorization_url(self, request=None):
        "The second step of the OAuth workflow."
        if request is None:
            if not self.__request.is_valid():
                raise APIError('You must obtain a request token to request '
                               'and access token. Use get_request_token() '
                               'first.')
            request = self.__request
        url = urlparse.urljoin(self.url, 'oauth/authorize/')
        return url + '?' + urllib.urlencode(dict(oauth_token=request.token))

    def get_access_token(self, request=None, verifier=None):
        """The final step of the OAuth workflow. After this the client can make
        API calls."""
        if verifier:
            verifier = unicode(verifier)
        if request is None:
            if not self.__request.is_valid():
                raise APIError('You must obtain a request token to request '
                               'and access token. Use get_request_token() '
                               'first.')
            request = self.__request
        oauth = OAuth1(self._client.token,
                       client_secret=self._client.secret,
                       resource_owner_key=request.token,
                       resource_owner_secret=request.secret,
                       verifier=unicode(verifier),
                       signature_method=SIGNATURE_PLAINTEXT)
        cert_path = self.resource_path('cacert.pem')
        r = requests.post(urlparse.urljoin(self.url, 'oauth/access_token/'), auth=oauth, verify=cert_path)
        credentials = urlparse.parse_qs(r.text)
        self._access = OAuthToken(credentials.get('oauth_token')[0],
                                  credentials.get('oauth_token_secret')[0])
        return self._access
