import socket
import argparse
import csv
import re
from decimal import Decimal
from datetime import datetime
example = "{\"emeter\":{\"get_realtime\":{\"current\":0.153188,\"voltage\":123.45678,\"power\":8.9012345,\"total\":0.002031,\"err_code\":0}}}"
current = Decimal(re.findall(r"current\":(.+?),",example)[0])
voltage = Decimal(re.findall(r"voltage\":(.+?),",example)[0])
power = Decimal(re.findall(r"power\":(.+?),",example)[0])
total_use = Decimal(re.findall(r"total\":(.+?),",example)[0])
print current,voltage,power,total_use
# current = Decimal(example)
# voltage = Decimal(res[61:70])
# power = Decimal(res[80:87])
# print example