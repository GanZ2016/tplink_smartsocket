import socket
import mysql.connector
import SocketServer
import re
import subprocess
from decimal import Decimal
from datetime import datetime

#------------

socket_ip = "192.168.43.216"
port = 9999
#-------------
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




def check_status_name():
	#----------------------
	# Get realtime power
	cmd = '{"emeter":{"get_realtime":{}}}'
	try:
		sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock_tcp.connect((socket_ip, port))
		sock_tcp.send(encrypt(cmd))
		data = sock_tcp.recv(2048)
		sock_tcp.close()
	except socket.error:
		quit("Cound not connect to host " + socket_ip + ":" + str(port))
	msg = decrypt(data[4:])
	realtime_power = Decimal(re.findall(r"power\":(.+?),",msg)[0])
	
	#------------------
	#Get name
	sql = "SELECT name FROM plug ORDER BY id DESC LIMIT 1;" 
	cnx = mysql.connector.connect(user='root', password='12345678',
								host='localhost',
								database='tplink')
	try:
		cursor = cnx.cursor()
		cursor.execute(sql)
		for row in cursor.fetchall():
			get_name = row[0]
	except:
		cnx.rollback()
	cnx.close()	
	#------------------


	#------------------
	#Get power
	get_power = []
	sql = "SELECT power FROM plug WHERE name = \"" + get_name +"\";" 
	cnx = mysql.connector.connect(user='root', password='12345678',
								host='localhost',
								database='tplink')
	try:
		cursor = cnx.cursor()
		cursor.execute(sql)
		for row in cursor.fetchall():
			get_power.append(row[0])
	except:
		cnx.rollback()
	cnx.close()	

	#TODO
	# Use getpower, realtime_power to calculate the status.


	#result
	res = []
	res.append("0")
	res.append(get_name)
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
	#----------------------
	# Get realtime cosumption
	cmd = '{"emeter":{"get_realtime":{}}}'
	try:
		sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock_tcp.connect((socket_ip, port))
		sock_tcp.send(encrypt(cmd))
		data = sock_tcp.recv(2048)
		sock_tcp.close()
	except socket.error:
		quit("Cound not connect to host " + socket_ip + ":" + str(port))
	msg = decrypt(data[4:])
	use = Decimal(re.findall(r"total\":(.+?),",msg)[0])
	return use

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
            elif cmd == "usage":
				self.data[0:2] == "u:"
				cost = self.data[2:]
				res_val = month_cons()
				total_cost = float(cost) * res_val
				print "total cost", total_cost
				self.request.sendall("Monthly Cost: " + total_cost  + "KWh")
            else:
                try:
                    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock_tcp.connect((socket_ip, port))
                    sock_tcp.send(encrypt(cmd))
                    data = sock_tcp.recv(2048)
                    sock_tcp.close()
                except socket.error:
                    quit("Cound not connect to host " + socket_ip + ":" + str(port))
                msg = decrypt(data[4:])
                print "Returned: ", msg
                self.request.sendall(msg)

                # print "{} wrote:".format(self.client_address[0])
                # print self.data






if __name__ == "__main__":

    HOST, PORT = "192.168.43.122", 8000


    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
