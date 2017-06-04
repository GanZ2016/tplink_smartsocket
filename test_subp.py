import sys
import socket
import argparse
import csv
import re
import numpy as np 
import scipy.stats
from decimal import Decimal
from datetime import datetime
import mysql.connector    
import TCPServer
import json
import time

#-------------

status = 0;
ip = "192.168.43.216"
#-------------

# print sys.argv[1]
label = sys.argv[1]

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

def insertToDB(result,label):
	#--------------------
	#match string
	current = Decimal(re.findall(r"current\":(.+?),",result)[0])
	voltage = Decimal(re.findall(r"voltage\":(.+?),",result)[0])
	power = Decimal(re.findall(r"power\":(.+?),",result)[0])
	use = Decimal(re.findall(r"total\":(.+?),",result)[0])
	timeStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	#-------------------
	# sql = "SELECT current,power FROM plug WHERE name = \"" + label + "\" and status = 0 and power > 0.2 ORDER BY id DESC LIMIT 10;" 
	# cnx = mysql.connector.connect(user='root', password='12345678',
	# 							host='localhost',
	# 							database='tplink')

	# try:
	# 	cursor = cnx.cursor()
	# 	cursor.execute(sql)
	# 	get_current = []
	# 	get_power = []
	# 	print "select success"
	# 	#cnx.commit()
	# 	for row in cursor.fetchall():
	# 		get_power.append(row[1])
	# 		get_current.append(row[0])
	# finally:
	# 	cnx.rollback()

	# power_mean = np.mean(get_power)
	# power_std = np.std(get_power)
	# power_diff = np.max(get_power) - np.min(get_power)
	# current_mean = np.mean(get_current)
	# current_diff = np.max(get_current) - np.min(get_current)
	# power_min = power_mean - power_diff
	# power_max = power_mean - power_diff
	# current_min = current_mean - current_diff
	# current_max = current_mean - current_diff
	# cnx.close()	
	# #--------------------
	# #set status to 1 if abnormal
	# if (current < current_min or current > current_max) and (power < power_min or power > power_max):
    # 		status = 1
	#--------------------
	#insert into database
	cnx = mysql.connector.connect(user='root', password='12345678',
                              host='localhost',
                              database='tplink')
	#sql = 
	try:
		cursor = cnx.cursor()
		cursor.execute("INSERT INTO plug (datetime, current, voltage, power, cons, status, name) VALUES (%s, %s, %s, %s, %s, %s, %s)",(timeStr,current,voltage,power,use,status,label))
		cnx.commit()
		print "INSERT INTO DATABASE"
	finally:
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
	print "label:",label
	print "--------------"

	with open('HS110.csv', 'a+') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter=',',quoting=csv.QUOTE_ALL)
		spamwriter.writerow([timeStr, current, voltage, power,use,label,status])

	# print "Sent:     ", cmd
	# print "Received: ", decrypt(data[4:])

while(1):
    result = measure_socket(ip, port)
    insertToDB(result,label)
    time.sleep(10)
