import numpy as np
import time
import matplotlib.pyplot as plt
from typing import NamedTuple
import threading
import logging
from queue import Queue
from GuitarBotUDP import GuitarBotUDP
from xarm.wrapper import XArmAPI
from pymidi import server
# import GBotData as gbd
from rtpmidi import RtpMidi
import pretty_midi
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)



def midi_info(file):
    pm = pretty_midi.PrettyMIDI(file)

    onsets = pm.get_onsets()
    #onsets = onsets - onsets[0] + pre_count
    # notes_duration = np.diff(onsets)
    notes_value = []
    notes_vel = []
    notes_duration = []
    #onsets = []
    for instrument in pm.instruments:
        for note in instrument.notes:
            notes_value = np.append(notes_value, note.pitch)
            notes_vel = np.append(notes_vel, note.velocity)
            notes_duration = np.append(notes_duration, note.end - note.start)
            #onsets = np.append(onsets, note.start)
    onsets = np.round(onsets, 2)
    onsets = onsets - onsets[0] + 5
    onsets = np.append(onsets,onsets[-1]+0.15)
    # for i in range(len(notes_duration)):
    #     notes_duration[i] = int(notes_duration[i] * 1000)/1000
    #     notes_duration[i] = np.ceil(SYNC_RATE * notes_duration[i]) / SYNC_RATE
    return onsets, notes_duration, notes_vel


onsets, notes_duration, notes_vel = midi_info('SD MIDI S48(1).mid')
print(onsets, notes_duration, notes_vel)
print(len(onsets))



# global constant
UDP_IP = "192.168.1.50"
XARM_IP = '192.168.1.215'
UDP_PORT = 1001
pre_count = 5
OFFSET = 20.5

STRUM_PT = [375.7, 365.7, 347.7, 337.7, 305.7, 300.7, 260.7]
PICK_PT = [371.6 - OFFSET, 362.4 - OFFSET, 351.4 - OFFSET, 340.8 - OFFSET, 331.3 - OFFSET, 321.4 - OFFSET]
INIT_POSE = [684.3, 246.8, 375.7, -90, 0, 0]
SYNC_RATE = 250
move_time = 0.1
ipickeracc = 200
ipickvel = 50
pgain = 8000

left_queue = Queue()
pick_queue = Queue()
robot_queue = Queue()
#left hand cmd trigger in sec
left_hand_timing = np.array([4.8, 7.3, 8.55, 9.8, 12,13, 14])*1000

print(left_hand_timing)
#right hand pick cmd trigger in sec
pick_timing = onsets * 1000
for i in range(len(pick_timing)):
    pick_timing[i] = int(pick_timing[i]/10)*10
print(pick_timing)
robot_timing = 5000
#song length in sec
song_length = 25




class GuitarRobotController():
    def __init__(self):
        # self.cobot_controller = CobotController(250, INIT_POSE)
        self.xarm = XArmAPI(XARM_IP)
        self.guitarbot_udp = GuitarBotUDP(UDP_IP, UDP_PORT)
        self.left_thread = threading.Thread(target=self.lefthand_move)
        self.right_thread = threading.Thread(target=self.robot_move)
        self.pick_thread = threading.Thread(target=self.pick_move)

    def robot_init(self):

        self.xarm.set_simulation_robot(on_off=False)
        self.xarm.motion_enable(enable=True)
        self.xarm.clean_warn()
        self.xarm.set_mode(0)
        self.xarm.set_state(0)
        self.xarm.set_position(*INIT_POSE, wait=True)

    def xarm_start(self):
        self.xarm.set_mode(1)
        self.xarm.set_state(0)

    def thread_start(self):
        self.left_thread.start()
        self.right_thread.start()
        self.pick_thread.start()

    def thread_end(self):
        self.left_thread.join()
        self.right_thread.join()
        self.pick_thread.join()

    def _fifth_poly(self, q_i, q_f, time):
        # for picking, try 100 or 150 ms
        traj_t = np.linspace(0, time, int(time * SYNC_RATE))
        dq_i = 0
        dq_f = 0
        ddq_i = 0
        ddq_f = 0
        a0 = q_i
        a1 = dq_i
        a2 = 0.5 * ddq_i
        a3 = 1 / (2 * time ** 3) * (20 * (q_f - q_i) - (8 * dq_f + 12 * dq_i) * time - (3 * ddq_f - ddq_i) * time ** 2)
        a4 = 1 / (2 * time ** 4) * (
                30 * (q_i - q_f) + (14 * dq_f + 16 * dq_i) * time + (3 * ddq_f - 2 * ddq_i) * time ** 2)
        a5 = 1 / (2 * time ** 5) * (12 * (q_f - q_i) - (6 * dq_f + 6 * dq_i) * time - (ddq_f - ddq_i) * time ** 2)
        traj_pos = a0 + a1 * traj_t + a2 * traj_t ** 2 + a3 * traj_t ** 3 + a4 * traj_t ** 4 + a5 * traj_t ** 5
        return traj_pos

    def get_traj_p2p(self, note_i, note_f, move_time):
        pos_z = self._fifth_poly(note_i, note_f, move_time)

        pos_y = np.ones(len(pos_z)) * INIT_POSE[1]
        return pos_y, pos_z

    def get_traj(self, note_i, note_f, length, is_circular, note_ii=-1):
        if note_ii == -1:
            note_ii = note_i
        elps_b = 5

        if is_circular:
            pos_z1 = self._fifth_poly(note_i, note_f, length / 2)
            pos_z2 = self._fifth_poly(note_f, note_ii, length / 2)
            strum_range = note_i - note_f
            pos_y1 = abs((elps_b / (strum_range / 2)) * np.sqrt(
                abs((strum_range / 2) ** 2 - (pos_z1 - note_f - strum_range / 2) ** 2))) + INIT_POSE[1]

            pos_y2 = np.ones(len(pos_z2)) * INIT_POSE[1]
            pos_z = np.append(pos_z1, pos_z2)
            pos_y = np.append(pos_y1, pos_y2)

        else:
            pos_z = self._fifth_poly(note_i, note_f, length)
            strum_range = note_i - note_f
            pos_y = abs((elps_b / (strum_range / 2)) * np.sqrt(
                abs((strum_range / 2) ** 2 - (pos_z - note_f - strum_range / 2) ** 2))) + INIT_POSE[1]

        return pos_y, pos_z

    def lefthand_move(self):
        # First Two Measures
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[2, 2, 1, 1, 2, 2], ifretnumber=[3, 2, 2, 2, 3, 3])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 2, 2, 1, 2, 2], ifretnumber=[3, 3, 2, 2, 3, 3])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 1, 1, 2, 2, 2], ifretnumber=[3, 3, 2, 2, 3, 3])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[2, 2, 1, 1, 2, 2], ifretnumber=[3, 2, 2, 2, 3, 3])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 2, 2, 1, 2, 2], ifretnumber=[3, 3, 2, 2, 3, 3])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 1, 1, 2, 2, 2], ifretnumber=[3, 3, 2, 2, 3, 3])
        left_queue.get()
        self.guitarbot_udp.send_msg_left(iplaycommand=[3, 1, 1, 3, 3, 3], ifretnumber=[3, 3, 2, 2, 3, 3])
        return 0

    def pick_move(self):
        pick_queue.get()
        angle = -8
        self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        pick_queue.get()
        angle = -18
        self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        pick_queue.get()
        angle = -18
        self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)

        pick_queue.get()
        angle = -12
        self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        pick_queue.get()
        angle = -18
        self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        pick_queue.get()
        angle = -18
        self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)



        i  = 0
        while i < 2:
            pick_queue.get()
            angle = -15
            self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                               ipickerpos=angle,
                                               ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
            pick_queue.get()
            angle = -18
            self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                               ipickerpos=angle,
                                               ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
            pick_queue.get()
            angle = -18
            self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                               ipickerpos=angle,
                                               ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
            i += 1

        pick_queue.get()
        angle = -8
        self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        pick_queue.get()
        angle = -18
        self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
        pick_queue.get()
        angle = -18
        self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)

        i = 0
        while i < 2:
            pick_queue.get()
            angle = -15
            self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                               ipickerpos=angle,
                                               ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
            pick_queue.get()
            angle = -18
            self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                               ipickerpos=angle,
                                               ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
            pick_queue.get()
            angle = -18
            self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=2000, dgain=50,
                                               ipickerpos=angle,
                                               ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)
            i += 1

        pick_queue.get()
        angle = 0
        self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=1200, dgain=50,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)

        return 0
    def traj_generation(self):

        posZ = []
        posY = []

        str_i = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 6, 1, 6]
        str_f = [6, 4, 4, 6, 4, 4, 6, 5, 5, 6, 5, 5, 6, 4, 4, 6, 4, 4, 6, 5, 5, 5, 6, 1, 6, 1]
        str_ii = [0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1]
        for i in range(26):
            if i < 22:
                pos_y, pos_z = self.get_traj(STRUM_PT[str_i[i]], STRUM_PT[str_f[i]], onsets[i+1] - onsets[i], True, STRUM_PT[str_ii[i]])
            else:
                pos_y, pos_z = self.get_traj(STRUM_PT[str_i[i]], STRUM_PT[str_f[i]], onsets[i + 1] - onsets[i], False)
            posZ = np.append(posZ, pos_z)
            posY = np.append(posY, pos_y)



        #
        # print(posZ, posY)
        # fig = plt.figure()
        # plt.plot(posZ)
        # plt.show()
        return posY, posZ

    def robot_move(self):
        posY, posZ = self.traj_generation()
        robot_queue.get()
        for i in range(len(posZ)):
            start = time.time()
            new_pose = [INIT_POSE[0], posY[i], posZ[i], INIT_POSE[3], INIT_POSE[4], INIT_POSE[5]]
            self.xarm.set_servo_cartesian(new_pose)
            time.sleep(0.004 - (time.time() - start))

def main():

    grc = GuitarRobotController()
    #grc.traj_generation()
    grc.robot_init()
    time.sleep(1)
    grc.xarm_start()
    time.sleep(1)
    grc.thread_start()


    t_init = time.time()
    endOfSong = t_init + song_length
    # print(endOfSong)
    # print(t_init)
    Pi = 0
    Li = 0
    Ri = 0
    time_stamp = 0
    logging.info("start")
    logging.info(left_hand_timing)
    while time_stamp < song_length * 1000:
        t_i = time.time()
        if time_stamp == left_hand_timing[Li]:

            print(time_stamp)
            left_queue.put(Li)
            Li += 1
            Li = Li % len(left_hand_timing)
        if time_stamp == pick_timing[Pi]:
            pick_queue.put(Pi)
            print("right hand triggered")
            Pi += 1
            Pi = Pi % len(pick_timing)
        if time_stamp == robot_timing:
            robot_queue.put(1)

        time_stamp += 5
        #logging.info(time_stamp)
        time.sleep(0.005 - (time.time() - t_i))

        #print(time_stamp)
    logging.info("end")
    grc.thread_end()
if __name__ == '__main__':
    main()
