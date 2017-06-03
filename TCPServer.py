import socket
import mysql.connector
import SocketServer
import mysql.connector  

import subprocess


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
			'power'	   : '{"emeter":{"get_realtime":{}}}',
			'reset'    : '{"system":{"reset":{"delay":1}}}',
			'emeter'   : '{"emeter":{"get_realtime":{}}}',
			'status'   : 'status',
			'label'	   : 'label'
}

#global label

label = ''


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

socket_ip = "10.105.110.33"
port = 9999


def check_status_name():
	sql = "SELECT status,name FROM plug ORDER BY id DESC LIMIT 1;" 
	cnx = mysql.connector.connect(user='root', password='12345678',
								host='localhost',
								database='tplink')
	try:
		cursor = cnx.cursor()
		cursor.execute(sql)
		for row in cursor.fetchall():
			get_status = row[0]
			get_name = row[1]
	except:
		cnx.rollback()
	res = []
	res.append(get_status)
	res.append(get_name)
	cnx.close()	
	return res

def check_realtime():
	sql = "SELECT power,status,name FROM plug ORDER BY id DESC LIMIT 1;" 
	cnx = mysql.connector.connect(user='root', password='12345678',
								host='localhost',
								database='tplink')
	try:
		cursor = cnx.cursor()
		cursor.execute(sql)
		for row in cursor.fetchall():
			rt_power = row[0]
			rt_status = row[1]
			rt_name = row[2]
	except:
		cnx.rollback()
	rt_res = []
	rt_res.append(rt_power)
	rt_res.append(rt_status)
	rt_res.append(rt_name)
	cnx.close()	
	return rt_res

def month_cons():
	cnx = mysql.connector.connect(user='root', password='12345678', host='localhost', database='tplink')
	sql = "SELECT cons WHERE DATE_SUB(CURDATE(), INTERVAL 30 DAY) <= datatime;"	
	total_cons = []
	try:
		cursor = cnx.cursor()
		cursor.execute(sql)
		for row in cursor.fetchall():
    			total_cons.append(row[0])
	except:
		cnx.rollback()
	cnx.close()	
	return max(total_cons) - min(total_cons) 		

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


        if self.data[0:2] == "m:":
            label = self.data[2:]
            print label
            self.request.sendall("Set label to: "+ label)
            subprocess.Popen(["python","test_subp.py",label])
        else:
            cmd = commands[self.data]
            print "command: ", cmd
            if cmd == "status":
                res_string = check_status_name()
                print "status", res_string[0]
                print "name", res_string[1]
                self.request.sendall(res_string[1] + ": "+ res_string[0])
            if cmd == "usage":
                res_val = month_cons()
                print "usage", res_val
                self.request.sendall("Monthly Usage: " + res_val  + "KWh")
            else:
                try:
                    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock_tcp.connect((socket_ip, port))
                    sock_tcp.send(encrypt(cmd))
                    data = sock_tcp.recv(2048)
                    sock_tcp.close()
                except socket.error:
                    quit("Cound not connect to host " + socket_ip + ":" + str(port))

                # print "{} wrote:".format(self.client_address[0])
                # print self.data
                msg = decrypt(data[4:])
                print "Returned: ", msg
                self.request.sendall(msg[0])





if __name__ == "__main__":

    HOST, PORT = "10.105.110.33", 8000


    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
