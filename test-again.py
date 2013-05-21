from smartfile import OAuthClient


def main():
    #print "Testing the Smartfile API..."
    api = OAuthClient("0mddZEPSt6L4M2H5QBfOqgXd0EDdMQ", "Holyp8auMI0Ye6B5Rq0VRNmL6Sskoe")
    try:
        api.get_request_token()
        client_token = api.get_authorization_url()
        print client_token
        client_verification = raw_input("What was the verification? :")
        print client_verification
        token, verifier = api.get_access_token(None, client_verification)
        print token
        print verifier
        print(api.get('/path/info', children=True))
    except:
        #"There was an error connecting with OAuth"
        raise

main()
