from smartfile import OAuthClient


def main():
    #print "Testing the Smartfile API..."
    api = OAuthClient("zGSJpILRq2889Ne2bPBdEmEZLsRHpe", "KOb97irJG84PJ8dtEkoYt2Kqwz3VJa")
    try:
        api.get_request_token()
        client_token = api.get_authorization_url()
        #print client_token
        client_verification = raw_input("What was the verification? :")
        api.get_access_token(None, client_verification)
        #print(api.get('/path/info', children = True))
    except:
        #"There was an error connecting with OAuth"
        raise

main()
