import socket
import struct
import time
from tkinter import Event

import serial
import numpy as np

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_ip = "10.2.1.177"
udp_port = 8888
router_left = bytes('/lguitar', 'utf8')
router_picker = bytes('/rguitar', 'utf8')

#Add/remove any LH/strum events as desired to test
#Format of event is:
# [event type (LH/strum/pick),
# properties (LH can be slide/press lists, strum can be pick angle--45==down strum, -45==up strum, pick can be pick/don't pick),
# time]
LH = [['LH', [[1, 2, 2, 1, 1, 1], [1, 2, 2, 1, 1, 1]], 0], ['LH', [[1, 1, 1, 2, 3, 2], [3, 3, 1, 2, 2, 2]], 1.193478260869565], ['LH', [[1, 1, 5, 4, 3, 3], [3, 3, 2, 2, 2, 2]], 3.130434782608695]]
strum = [['strum', 'U', 0.5217391304347826], ['strum', 'D', 1.565217391304348]]

Events = []
for event in LH:
    Events.append(event)

for event in strum:
    Events.append(event)

Events.sort(key=lambda x: x[2])

start = time.time()
for e in Events:
    tNextEvent = e[2]
    type = e[0]
    if type == 'LH':
        chordtoplay = e[1]
