#Smartfile test application
import os, pprint
from smartfile import OAuthClient

def main():
	print "Testing the Smartfile API..."
	api = OAuthClient("zGSJpILRq2889Ne2bPBdEmEZLsRHpe", "KOb97irJG84PJ8dtEkoYt2Kqwz3VJa")
	try:
		api.get_request_token()
		client_token = api.get_authorization_url()
		print client_token
		client_verification = raw_input("What was the verification? :")
		api.get_access_token(None, client_verification)
		#pprint.pprint(api.get('/path/info', children = True))
		
		#Get JSON for root
		tree = api.get('/path/info', children = True)
		if 'children' not in tree:
			return []
		# Returns all directories and files in root!
		pprint.pprint([i['path'].encode("utf-8") for i in tree['children']])
		'''
		************ OUTPUT *********************
		['/Test',
		 '/Test Folder',
		 '/logs',
		 '/newhome',
		 '/Chapter 1 Response.docx',
		 '/Ordinary Men.docx',
		 '/build_linux.sh',
		 '/configuration.cfg',
		 '/globe.txt',
		 '/hello.txt',
		 '/move-test.py',
		 '/traytest.py']
		
		'''
	except:
		print "There was an error connecting with OAuth"
		raise
	
	#newapi = OAuthClient("oIu1b8MY9G72DSkwZC75vpEknY3Vsd", "10VxVIk7IZV6fIJ9vJWvmx5ow5nyxi", client_token, client_verification)
	
	#pprint.pprint(newapi.get('/path/info', '/?children=on'))
main()

"""
task = api.post('/path/oper/move', src='/globe.txt', dst='/globecopy.txt')
		while True:
			status = api.get('/task', task['uuid'])
			if status['status'] == 'SUCCESS':
				print "success"
				break
				"""
