import mysql.connector 
import numpy as np 
import scipy.stats
sql = "SELECT current,power FROM plug where name = \"light\" and status = 0 and power > 0.2 ORDER BY id DESC LIMIT 10;" 
cnx = mysql.connector.connect(user='root', password='12345678',
                            host='localhost',
                            database='tplink')

status = 0

try:
    cursor = cnx.cursor()
    cursor.execute(sql)
    current = []
    power = []
    #cnx.commit()
    for row in cursor.fetchall():
        power.append(row[1])
        current.append(row[0])
except:
    cnx.rollback()

power_mean = np.mean(power)
power_std = np.std(power)
power_diff = np.max(power) - np.min(power)
current_mean = np.mean(current)
current_diff = np.max(current) - np.min(current)
power_min = power_mean - power_diff
power_max = power_mean - power_diff
current_min = current_mean - current_diff
current_max = current_mean - current_diff
cnx.close()

current = 0

if (current < current_min or current > current_max) and (power < power_min or power > power_max):
    		status = 1

print status