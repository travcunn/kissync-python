#Smartfile test application
import os, pprint
from smartfile import OAuthClient

def main():
	print "Testing the Smartfile API..."
	api = OAuthClient("Oft45O8bsR6nJm7tO9Ppwj76KSODFt", "1Um8yXH5sb2JyIbzl3CKrG9WhlFYmX")
	try:
		api.get_request_token()
		client_token = api.get_authorization_url()
		print client_token
		client_verification = raw_input("What was the verification? :")
		api.get_access_token(None, client_verification)
		pprint.pprint(api.get('/path/info', '/'))
	except:
		print "There was an error connecting with OAuth"
		raise
	
	#newapi = OAuthClient("oIu1b8MY9G72DSkwZC75vpEknY3Vsd", "10VxVIk7IZV6fIJ9vJWvmx5ow5nyxi", client_token, client_verification)
	
	#pprint.pprint(newapi.get('/path/info', '/?children=on'))
main()
