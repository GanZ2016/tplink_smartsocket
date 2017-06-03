import socket
import SocketServer

# Check if IP is valid
def validIP(ip):
	try:
		socket.inet_pton(socket.AF_INET, ip)
	except socket.error:
		parser.error("Invalid IP Address.")
	return ip

# Predefined Smart Plug Commands
# For a full list of commands, consult tplink_commands.txt
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
# <<<<<<< Updated upstream:tplink_smartplug.py
			'power'	   : '{"emeter":{"get_realtime":{}}}',
			'reset'    : '{"system":{"reset":{"delay":1}}}',
# =======
			'reset'    : '{"system":{"reset":{"delay":1}}}',
			'emeter'   : '{"emeter":{"get_realtime":{}}}'
# >>>>>>> Stashed changes:tplink-smartplug.py
}

# Encryption and Decryption of TP-Link Smart Home Protocol
# XOR Autokey Cipher with starting key = 171
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

ip = "10.0.0.244"
port = 9999

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(2048)
        cmd = commands[self.data]
        print "command: ", cmd
        try:
        	sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        	sock_tcp.connect((ip, port))
        	sock_tcp.send(encrypt(cmd))
        	data = sock_tcp.recv(2048)
        	sock_tcp.close()
        except socket.error:
        	quit("Cound not connect to host " + ip + ":" + str(port))

        # print "{} wrote:".format(self.client_address[0])
        # print self.data
        msg = decrypt(data[4:])
        print "Returned: ", msg
        self.request.sendall(msg)




if __name__ == "__main__":
    HOST, PORT = "10.0.0.94", 8000

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
