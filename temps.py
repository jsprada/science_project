import os
import re
from datetime import datetime
import time

# this script is called once per minute, by cron.
# to increase the number of times the sensors are polled per run
# edit the interval to the number of additional rounds
# and delay to the number of seconds between rounds.  
# It takes about 5-6 seconds for the pi to poll 4 sensors per round.  
# So adding a 15 second delay, and interval of 2 will effectively create 
# one poll every 20 seconds(ish)
# set interval to 0 for once per minute
# set interval to 1 and delay to 25 for twice per minute
# set interval to 2 and delay to 15 for thrice per minute
# It is not recommended to poll more often than that.

interval = 2 # number of times to run after first run
delay = 15 # delay between running (takes about 5-6 seconds each poll)
header = ['datetime', 'sensor_1', 'sensor_2', 'sensor_3', 'sensor_4']
log_file = '/home/pi/sp/temps_log'
w1_path = '/sys/bus/w1/devices/'

counter = 0

def get_probes(path):
    temp_list=[]
    probe_dir=os.listdir(path)

    for probe in probe_dir:
        if probe == 'w1_bus_master1':
            
            pass
        else:
            temp_list.append(probe)
            

    return temp_list




def get_temperature(w1_path, temp_string):
    filename = os.path.join(w1_path, temp_string+"/w1_slave")
    f = open(filename, "r")
    text_temp = f.read()
    f.close()
    raw_temp = text_temp.split('t=')
    
    return str(round(float(raw_temp[1])/1000, 1))


def check_for_log_file(log_file):
        if os.path.isfile(log_file):
            #print('Log File already exists')
            pass
        else:
            #print('Creating New Temperatures Log File')
            with open(log_file, "a") as f:
                for col in header:
                    f.write("%s\t" % col)
                f.write("\n")
            f.close()


def loop():
    row = []
    row.append( datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    check_for_log_file(log_file)

    for temperature in get_probes(w1_path):
        row.append(get_temperature(w1_path, temperature))



    with open(log_file, "a") as f:
        for col in row:
            f.write("%s\t" % col)
        f.write("\n")
    f.close()




loop()
while counter < interval:    
    time.sleep(delay)
    #print(counter)
    loop()
    counter += 1
