
import socket
import argparse

import csv
import re
import numpy as np 
import scipy.stats
from decimal import Decimal
from datetime import datetime
import mysql.connector    

import json


version = 0.1

#---------------------------
#Type

lable = 'light';

status = 0;

#---------------------------

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
			'emeter'   : '{"emeter":{"get_realtime":{}}}'
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





# Parse commandline arguments
parser = argparse.ArgumentParser(description="TP-Link Wi-Fi Smart Plug Client v" + str(version))
parser.add_argument("-t", "--target", metavar="<ip>", required=True, help="Target IP Address", type=validIP)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-c", "--command", metavar="<command>", help="Preset command to send. Choices are: "+", ".join(commands), choices=commands)
group.add_argument("-j", "--json", metavar="<JSON string>", help="Full JSON string of command to send")
args = parser.parse_args()

# Set target IP, port and command to send
ip = args.target
port = 9999
if args.command is None:
	cmd = args.json
else:
	cmd = commands[args.command]

# initial value
#lastuse = Decimal(0.0);
#example = "{\"emeter\":{\"get_realtime\":{\"current\":0.153188,\"voltage\":123.45678,\"power\":8.9012345,\"total\":0.002031,\"err_code\":0}}}"
# Send command and receive reply 



# Send command and receive reply

try:
	sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock_tcp.connect((ip, port))
	sock_tcp.send(encrypt(cmd))
	data = sock_tcp.recv(2048)
	sock_tcp.close()

	res = decrypt(data)
	#match string
	current = Decimal(re.findall(r"current\":(.+?),",res)[0])
	voltage = Decimal(re.findall(r"voltage\":(.+?),",res)[0])
	power = Decimal(re.findall(r"power\":(.+?),",res)[0])
	use = Decimal(re.findall(r"total\":(.+?),",res)[0])
	#diff = use - lastuse
	#time = 
	timeStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	#-------------------
	#get the range of current and power to check the status
	sql = "SELECT current,power FROM plug where name = \"light\" and status = 0 and power > 0.2 ORDER BY id DESC LIMIT 10;" 
	cnx = mysql.connector.connect(user='root', password='12345678',
								host='localhost',
								database='tplink')

	try:
		cursor = cnx.cursor()
		cursor.execute(sql)
		get_current = []
		get_power = []
		#cnx.commit()
		for row in cursor.fetchall():
			get_power.append(row[1])
			get_current.append(row[0])
	except:
		cnx.rollback()

	power_mean = np.mean(get_power)
	power_std = np.std(get_power)
	power_diff = np.max(get_power) - np.min(get_power)
	current_mean = np.mean(get_current)
	current_diff = np.max(get_current) - np.min(get_current)
	power_min = power_mean - power_diff
	power_max = power_mean - power_diff
	current_min = current_mean - current_diff
	current_max = current_mean - current_diff
	cnx.close()	
	#--------------------
	#set status to 1 if abnormal
	if (current < current_min or current > current_max) and (power < power_min or power > power_max):
    		status = 1
	#--------------------
	#insert into database
	cnx = mysql.connector.connect(user='root', password='12345678',
                              host='localhost',
                              database='tplink')
	
	sql = "INSERT INTO plug (datetime, current, voltage, power, cons, status, name) VALUES (%s, %s, %s, %s, %s, %s, %s)",(timeStr,current,voltage,power,use,status,lable)
	try:
		cursor = cnx.cursor(sql)
		cursor.execute()
		cnx.commit()
	except:
		cnx.rollback()		
	cnx.close()	
	#----------------------
	#print res
	print "current:",current
	print "voltage:",voltage
	print "power:",power
	print "Time:",timeStr
	print "Use:",use
	print "status",status

	with open('HS110.csv', 'a+') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter=',',quoting=csv.QUOTE_ALL)
		spamwriter.writerow([timeStr, current, voltage, power,use,lable,status])
	# print type(data)

	# with open('data.json','a') as f:
	# 	f.write('\n')
	# 	f.write(decrypt(data[4:]))

	print "Sent:     ", cmd
	print "Received: ", decrypt(data[4:])
except socket.error:
	quit("Cound not connect to host " + ip + ":" + str(port))

