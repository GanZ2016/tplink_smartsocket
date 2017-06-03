import socket
def encrypt(string):
	key = 171
	result = "\0\0\0\0"
	for i in string:
		a = key ^ ord(i)
		key = a
		result += chr(a)
	return result

def decrypt(string):
	key = 171
	result = ""
	for i in string:
		a = key ^ ord(i)
		key = ord(i)
		result += chr(a)
	return result

# cmd = '{"system":{"set_relay_state":{"state":1}}}'
# with open("cmd.txt","w") as f:
#     f.write(encrypt(cmd))

with open("cmd.txt","r") as f:
	cmd = f.read()
	# print decrypt(st)
ip = "10.0.0.244"
port = 9999
try:
	sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock_tcp.connect((ip, port))
	sock_tcp.send(cmd)
	data = sock_tcp.recv(2048)
	sock_tcp.close()
	# print type(data)

	# with open('data.json','a') as f:
	# 	f.write('\n')
	# 	f.write(decrypt(data[4:]))

	print "Sent:     ", cmd
	print "Received: ", decrypt(data[4:])
except socket.error:
	quit("Cound not connect to host " + ip + ":" + str(port))
