import socket
import struct
import time

from matplotlib.cbook import flatten

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_ip = "10.2.1.177"
udp_port = 8888
LH = bytes('L', 'utf8')
strum = bytes('S', 'utf8')
pick = bytes('P', 'utf8')

def send_msg(type, command):
    message = None
    flattened = []
    if type == 'LH':
        message = LH
        flattened = [i for list in command for i in list]
    elif type == 'strum':
        message = strum
        flattened = [i for i in command]
    elif type == 'pick':
        message = pick
        flattened = [i for list in command for i in list]

    print(type, ": ", flattened)
    pCommand = struct.pack(f'<{len(flattened)}b', *flattened)
    packed_data = message + pCommand
    time.sleep(0.005)
    # self.sock.sendto(bytes(msg, 'utf8'), (self.udp_ip, self.udp_port))
    sock.sendto(packed_data, (udp_ip, udp_port))

    time.sleep(0.01)
    return 0

def main():
    #Add/remove any LH/strum/pick events as desired to test
    #Format of event is:
    # [event type (LH/strum/pick),
    # properties (LH can be slide, press lists, strum can be pick angle--45==down strum, -45==up strum, pick can be don't pick (0), pick (1), tremolo (2) + length of a quarter note IN TRAJ POINTS + speed of tremolo IN TRAJ POINTS),
    # time]
    LH = [['LH', [[1, 3, 2, 1, 1, 1], [3, 2, 2, 1, 2, 3]], 0], ['LH', [[1, 3, 4, 1, 1, 1], [3, 2, 2, 1, 2, 3]], 1], ['LH', [[1, 1, 1, 2, 3, 2], [3, 3, 1, 2, 2, 2]], 2], ['LH', [[1, 1, 1, 2, 3, 2], [3, 3, 1, 2, 2, 2]], 3], ['LH', [[1, 1, 1, 2, 1, 2], [3, 3, 1, 2, 2, 2]], 4], ['LH', [[1, 2, 4, 4, 3, 1], [3, 2, 2, 2, 2, 3]], 5], ['LH', [[1, 2, 4, 2, 5, 2], [3, 2, 2, 2, 2, 2]], 6], ['LH', [[1, 2, 2, 1, 3, 2], [1, 2, 2, 1, 2, 2]], 7], ['LH', [[1, 1, 5, 4, 7, 3], [1, 3, 2, 2, 2, 2]], 8], ['LH', [[1, 1, 5, 4, 7, 3], [1, 1, 1, 1, 1, 1]], 9]]
    strum = [['strum', [45, 75, 0], 0], ['strum', [-45, 75, 0], 1], ['strum', [45, 75, 0], 2], ['strum', [-45, 75, 0], 3], ['strum', [45, 75, 0], 4], ['strum', [-45, 75, 0], 5], ['strum', [45, 75, 0], 6], ['strum', [-45, 75, 0], 7], ['strum', [45, 75, 0], 8], ['strum', [-45, 75, 1], 9]]
    #strum = []
    # pick = [['pick', [[1, 1, 1, 1, 1, 1], [5, 0]], 1], ['pick', [[1, 1, 1, 1, 1, 1], [5, 0]], 1.5], ['pick', [[1, 1, 1, 2, 1, 1], [120, 10]], 2], ['pick', [[1, 1, 1, 2, 1, 1], [100, 20]], 3.5], ['pick', [[1, 1, 1, 2, 1, 1], [120, 15]], 4], ['pick', [[1, 1, 1, 2, 1, 1], [120, 5]], 5]]
    pick = []
    Events = []
    for event in LH:
        Events.append(event)

    for event in strum:
        Events.append(event)

    for event in pick:
        Events.append(event)

    Events.sort(key=lambda x: x[2])

    print("4")
    time.sleep(1)
    print("3")
    time.sleep(1)
    print("2")
    time.sleep(1)
    print("1")
    time.sleep(1)

    start = time.time()
    for e in Events:
        tNextEvent = e[2]
        eventType = e[0]

        # Calculate the target time for the next event
        target_time = start + tNextEvent

        # Wait until the target time
        tElapsed = time.time()
        while tElapsed < target_time:
            time.sleep(0.0001)  # Small sleep to avoid busy waiting
            tElapsed = time.time()  # Update elapsed time

        # Send the event message
        if eventType == 'LH':
            send_msg(type='LH', command=e[1])
        elif eventType == 'strum':
            send_msg(type='strum', command=e[1])
        elif eventType == 'pick':
            send_msg(type='pick', command=e[1])

        # Print elapsed time for debugging
        tElapsed = time.time() - start
        print("Elapsed time:", tElapsed)

if __name__ == "__main__":
    main()