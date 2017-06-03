import sys


# print sys.argv[1]
label = sys.argv[1]
ip = "10.0.0.244"
port = 9999
commands = {'info'     : '{"system":{"get_sysinfo":{}}}',
			'on'       : '{"system":{"set_relay_state":{"state":1}}}',
			'off'      : '{"system":{"set_relay_state":{"state":0}}}',
			'cloudinfo': '{"cnCloud":{"get_info":{}}}',
			'wlanscan' : '{"netif":{"get_scaninfo":{"refresh":0}}}',
			'time'     : '{"time":{"get_time":{}}}',
			'schedule' : '{"schedule":{"get_rules":{}}}',
			'countdown': '{"count_down":{"get_rules":{}}}',
			'antitheft': '{"anti_theft":{"get_rules":{}}}',
			'reboot'   : '{"system":{"reboot":{"delay":1}}}',
			'reset'    : '{"system":{"reset":{"delay":1}}}',
			'reset'    : '{"system":{"reset":{"delay":1}}}',
			'emeter'   : '{"emeter":{"get_realtime":{}}}'
}

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

def measure_socket(ip,port):
    try:
    	sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	sock_tcp.connect((ip, port))
        cmd = commands['emeter']
    	sock_tcp.send(encrypt(cmd))
    	data = sock_tcp.recv(2048)
    	sock_tcp.close()
        return decrypt(data[4:])
    	# print "Sent:     ", cmd
    	# print "Received: ", decrypt(data[4:])
    except socket.error:
    	quit("Cound not connect to host " + ip + ":" + str(port))

def insertToDB(reuslt,label):

while(1):
    result = measure_socket(ip, port)
    insertToDB(result,label)
