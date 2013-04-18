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
		tree = api.get('/whoami')
		if 'user' not in tree:
			return []
		# Returns all directories and files in root!
		#pprint.pprint(tree['site'])
		#pprint.pprint(tree['user']['name'].encode("utf-8"))
		
		try:
			api.post("/path/oper/checksum", path='/globe.txt', algorithm='MD5')
		except:
			pass
		
		while True:
			s = api.get('/task')
			for i in s:
				fileAndHash =  i['result']['result']['checksums']
				if '/globed.txt' not in fileAndHash:
					print "Not found  in this iteration"
				else:
					print i['result']['result']['checksums']['/globed.txt']
					return
				
			break
		#s = api.get('/task')
		#print s
		"""
			if s['status'] == 'SUCCESS':
				print "success"
				break
		"""
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
