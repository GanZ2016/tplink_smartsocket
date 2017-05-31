#!/usr/bin/env python
# 
# TP-Link Wi-Fi Smart Plug Protocol Client
# For use with TP-Link HS-100 or HS-110
#  
# by Lubomir Stroetmann
# Copyright 2016 softScheck GmbH 
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
#
import socket
import argparse
import csv
import re
from decimal import Decimal
from datetime import datetime
version = 0.1

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
			'reset'    : '{"system":{"reset":{"delay":1}}}'
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
	timeStr=datetime.now().strftime('%Y-%m-%d %H%M%S')
	print res
	print "current:",current
	print "voltage:",voltage
	print "power:",power
	print "Time:",timeStr
	#print "last Use", lastuse
	print "Use:",use
	#print "diff",diff

	with open('HS110.csv', 'a+') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter=',',quoting=csv.QUOTE_ALL)
		spamwriter.writerow([timeStr, current, voltage, power,use])
	# print "Sent:     ", cmd
	# print "Received: ", decrypt(data[4:])
	# print "current:" , decrypt(data[40:49])
	# print "voltage:", decrypt(data[60:70])
	# print "power:", decrypt(data[78:87])
#	return use
except socket.error:
	quit("Cound not connect to host " + ip + ":" + str(port))

