import mysql.connector 
import numpy as np 
import scipy.stats
import TCPServer

label = "router"
sql = "SELECT current,power FROM plug WHERE name = \"" + label + "\" and status = 0 and power > 0.2 ORDER BY id DESC LIMIT 10;" 
print sql