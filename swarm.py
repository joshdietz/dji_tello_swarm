# Requires (from pip)
# python-nmap
import nmap
import socket
import threading
import time
from subprocess import Popen, PIPE
import re

"""
CONFIGURATION SECTION
"""
# store the prefix of the mac addresses
MAC_PREFIX = "10:2c:6b:77"

# store the ID's of the drones (last four of SSID/MAC)
DEVICES = ["cba2"]

# store the host of the network
HOST = '192.168.0.1/24'

"""
END OF CONFIGURATION SECTION

START OF NETWORK SCANNING SECTION
"""

# store information on each drone
DRONES = []

TELLO_ADDRESSES = []

LOCAL_ADDRESSES = []

SOCKETS = []

NEXT_AVAILABLE_PORT = 9010

# take drone name, and return the mac addresses in a dictionary
for device in DEVICES:
    # split each device into 4 parts, and concatenate them with the prefix
    mac_address = MAC_PREFIX + ":" + device[0:2] + ":" + device[2:4]

    DRONES.append({
        "ID": device,
        "MAC": mac_address,
        "IP":""
    })

# scan the network for all devices
print("Starting port scan...")
nm = nmap.PortScanner()
nm.scan(hosts=HOST, arguments='-sP')
host_list = nm.all_hosts()

print("Processing results...")
# iterate through the list of devices
for host in host_list:
        pid = Popen(['arp', '-n', host], stdout=PIPE)
        s = pid.communicate()[0]
        mac = s.split()[-3].decode('utf-8')

        # iterate through the list of drones
        for drone in DRONES:
            # if the mac address of the drone is found in the arp table
            if mac == drone["MAC"]:
                drone["IP"] = host
                print("Found drone: " + drone["ID"] + " at " + host)


"""
END OF NETWORK SCANNING SECTION

START OF SETUP SECTION
"""
for drone in DRONES:
    # setup tello and local addresses
    tello = (drone["IP"], 8889)
    local = ('', NEXT_AVAILABLE_PORT)
    TELLO_ADDRESSES.append(tello)
    LOCAL_ADDRESSES.append(local)

    # increment next available port
    NEXT_AVAILABLE_PORT += 1

    # setup sockets
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # bind the socket to the local address
    sock.bind(local)

    # add the socket to the list of sockets
    SOCKETS.append(sock)

"""
END OF SETUP SECTION

START OF SWARM CONTROL
(note everything will be repeated across all drones)
"""
